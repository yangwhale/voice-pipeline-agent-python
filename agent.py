import os

from dotenv import load_dotenv
from livekit.agents import Agent, AgentSession, JobContext, WorkerOptions, cli, stt
from livekit.plugins import google, silero

from gemini_stt import GeminiSTT
from gemini_tts import GeminiTTS

load_dotenv(".env.local")


class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions=(
                "你是 Chris 的中文语音助手，名字叫小爱同学。"
                "回答简洁、自然、像朋友聊天一样。"
                "技术术语保留英文，不要翻译。"
            ),
        )


async def entrypoint(ctx: JobContext):
    await ctx.connect()

    session = AgentSession(
        vad=silero.VAD.load(),
        stt=stt.StreamAdapter(
            stt=GeminiSTT(model="gemini-3.1-flash-lite-preview"),
            vad=silero.VAD.load(),
        ),
        llm=google.LLM(
            model="gemini-3.1-flash-lite-preview",
            vertexai=False,
            api_key=os.environ["GEMINI_API_KEY"],
            temperature=0.7,
        ),
        tts=GeminiTTS(
            model="gemini-3.1-flash-tts-preview",
            voice="Charon",
        ),
    )

    await session.start(agent=Assistant(), room=ctx.room)
    await session.generate_reply(instructions="向用户打个招呼，自我介绍一下你是小爱同学")


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
