import os

from anthropic import AsyncAnthropicVertex
from dotenv import load_dotenv
from livekit.agents import Agent, AgentSession, JobContext, WorkerOptions, cli
from livekit.plugins import anthropic, silero

from gemini_stt import GeminiSTT
from gemini_tts import GeminiTTS

load_dotenv(".env.local")


class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions=(
                "你是 Chris 的中文语音助手，名字叫 tianmaojingling。"
                "你在打电话，不是写文档——所有回复必须能被 TTS 自然念出。"
                "\n\n【风格】"
                "\n- 像朋友闲聊一样自然，每句不超过 25 字，连续不超过 3 句"
                "\n- 主动追问、确认理解，不要一次塞太多信息"
                "\n- 技术术语保留英文（API、token、Vertex 等），不要翻译"
                "\n\n【绝对不要】"
                "\n- markdown 标记：星号、井号、反引号、列表符号"
                "\n- 代码块、表格、长 bullet 清单"
                "\n- 念长 URL 或长 ID（说'我把链接发到聊天里'即可）"
                "\n\n【情绪标签】"
                "\n在重要句子开头可以加一个情绪标签控制语气，TTS 会按标签调整：[casually] 日常、[thoughtfully] 思考、[excitedly] 兴奋、[seriously] 严肃、[cheerfully] 愉快、[calmly] 平和"
                "\n例："
                "\n  '[casually] 嗯，这个简单，我帮你查下。'"
                "\n  '[excitedly] 好消息！部署成功了！'"
                "\n  '[thoughtfully] 这个有两种方案，一个快但贵，一个慢但省。'"
                "\n不必每句都加，自然语气切换时再用。"
            ),
        )


async def entrypoint(ctx: JobContext):
    await ctx.connect()

    vad = silero.VAD.load(min_silence_duration=0.6)

    vertex_client = AsyncAnthropicVertex(
        project_id=os.environ.get("ANTHROPIC_VERTEX_PROJECT_ID", "gpu-launchpad-playground"),
        region=os.environ.get("ANTHROPIC_VERTEX_REGION", "global"),
    )

    session = AgentSession(
        vad=vad,
        turn_handling={
            "endpointing": {"min_delay": 0.8, "max_delay": 4.0},
            "interruption": {
                # GeminiSTT 是 buffered（utterance-level，无 streaming partial），
                # 所以 adaptive interruption 和 MultilingualModel turn detector 用不了，
                # 必须回退到 VAD-based 方案。
                "mode": "vad",
                "min_duration": 0.5,
            },
        },
        stt=GeminiSTT(
            model=os.environ.get("STT_MODEL", "gemini-3-flash-preview"),
        ),
        llm=anthropic.LLM(
            model=os.environ.get("CLAUDE_MODEL", "claude-opus-4-7"),
            client=vertex_client,
            api_key="vertex-dummy-not-used",  # plugin __init__ requires api_key check, but our `client` overrides it
            # temperature omitted: Claude Opus 4.7+ deprecates the parameter
        ),
        tts=GeminiTTS(
            model=os.environ.get("TTS_MODEL", "gemini-3.1-flash-tts-preview"),
            voice=os.environ.get("TTS_VOICE", "Charon"),
        ),
    )

    await session.start(agent=Assistant(), room=ctx.room)
    await session.generate_reply(instructions="向用户打个招呼，自我介绍一下你是中文语音助手")


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
