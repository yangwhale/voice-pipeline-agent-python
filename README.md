> [!NOTE]
> **Fork notice** — this fork swaps the upstream Deepgram + OpenAI + Cartesia pipeline for a
> Vertex-AI-backed Mandarin pipeline (Claude Opus + Gemini STT/TTS), runnable from regions
> blocked from the public Gemini API (e.g. HK).
>
> | Stage | Upstream | This fork |
> | --- | --- | --- |
> | STT | `deepgram.STT()` | `GeminiSTT("gemini-3-flash-preview")` — custom buffered adapter in `gemini_stt.py`, dual-mode (Vertex / aistudio). Best Mandarin accuracy in our tests; recognises rare Beijing place names without phrase biasing. |
> | LLM | `openai.LLM("gpt-4o-mini")` | `anthropic.LLM("claude-opus-4-7")` via `AsyncAnthropicVertex` (Vertex Anthropic, `global` region) |
> | TTS | `cartesia.TTS()` | `GeminiTTS("gemini-3.1-flash-tts-preview", voice="Charon")` — custom adapter in `gemini_tts.py`, dual-mode (Vertex / aistudio) |
> | VAD | `silero.VAD` | `silero.VAD` (used for utterance chunking and as the interruption signal — GeminiSTT is buffered, so streaming-only features like LiveKit's `MultilingualModel` turn detector and `adaptive` interruption are not used in this fork) |
>
> Required env vars (Vertex mode, see `.env.example`): `ANTHROPIC_VERTEX_PROJECT_ID`,
> `GOOGLE_CLOUD_PROJECT`, `GOOGLE_GENAI_USE_VERTEXAI=true`. The VM needs ADC or
> `GOOGLE_APPLICATION_CREDENTIALS` with `roles/aiplatform.user`.
>
> ⚠️ **Gemini 3.x defaults `thinking_level` to ON** — `gemini_stt.py` explicitly sets it to
> `MINIMAL` to avoid multi-second latency on transcription. Same applies to any other
> non-reasoning Gemini 3.x usage.

> [!WARNING]
> Upstream notice: this example is outdated. See the [agent-starter-python](https://github.com/livekit-examples/agent-starter-python) repository for the latest example.

# Python Voice Agent

<p>
  <a href="https://cloud.livekit.io/projects/p_/sandbox"><strong>Deploy a sandbox app</strong></a>
  •
  <a href="https://docs.livekit.io/agents/overview/">LiveKit Agents Docs</a>
  •
  <a href="https://livekit.io/cloud">LiveKit Cloud</a>
  •
  <a href="https://blog.livekit.io/">Blog</a>
</p>

A basic example of a voice agent using LiveKit and Python.

## Dev Setup

Clone the repository and install dependencies to a virtual environment:

```console
# Linux/macOS
cd voice-pipeline-agent-python
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 agent.py download-files
```

<details>
  <summary>Windows instructions (click to expand)</summary>
  
```cmd
:: Windows (CMD/PowerShell)
cd voice-pipeline-agent-python
python3 -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

</details>

Set up the environment by copying `.env.example` to `.env.local` and filling in the required values:

- `LIVEKIT_URL`
- `LIVEKIT_API_KEY`
- `LIVEKIT_API_SECRET`
- `ANTHROPIC_VERTEX_PROJECT_ID` — your GCP project (Vertex Anthropic / Claude)
- `GOOGLE_CLOUD_PROJECT` — same GCP project (Vertex Gemini for STT/TTS)
- `GOOGLE_GENAI_USE_VERTEXAI=true` — keep on for HK and other regions blocked from aistudio

You can also do this automatically using the LiveKit CLI:

```console
lk app env
```

Run the agent:

```console
python3 agent.py console
```

This agent can use a frontend application to communicate with. You can use one of our example frontends in [livekit-examples](https://github.com/livekit-examples/), create your own following one of our [client quickstarts](https://docs.livekit.io/realtime/quickstarts/), or test instantly against one of our hosted [Sandbox](https://cloud.livekit.io/projects/p_/sandbox) frontends.

Run the agent with the following command when using a frontend application.

```console
python3 agent.py dev
```
