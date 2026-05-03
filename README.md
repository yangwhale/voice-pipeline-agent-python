> [!NOTE]
> **Fork notice** — this fork swaps the upstream Deepgram + OpenAI + Cartesia pipeline for an
> all-Google / Gemini-3.1 Cascade pipeline tuned for **Mandarin Chinese**:
>
> | Stage | Upstream | This fork |
> | --- | --- | --- |
> | STT | `deepgram.STT()` | `GeminiSTT("gemini-3.1-flash-lite-preview")` (custom adapter in `gemini_stt.py`, wrapped in `stt.StreamAdapter` + Silero VAD) |
> | LLM | `openai.LLM("gpt-4o-mini")` | `google.LLM("gemini-3.1-flash-lite-preview")` (Gemini API) |
> | TTS | `cartesia.TTS()` | `GeminiTTS("gemini-3.1-flash-tts-preview", voice="Charon")` (custom adapter in `gemini_tts.py`) |
> | VAD | `silero.VAD` | `silero.VAD` (unchanged, also used by `StreamAdapter` to chunk utterances for the buffered STT) |
>
> Required env var: `GEMINI_API_KEY` (see `.env.example`). Gemini API serves all 3 stage models; no Vertex / GCP project needed.
> See `gemini_stt.py` and `gemini_tts.py` for the custom LiveKit `stt.STT` / `tts.TTS` adapters wrapping Gemini multimodal `generateContent` and the Gemini Generate-Speech API.

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
- `OPENAI_API_KEY`
- `CARTESIA_API_KEY`
- `DEEPGRAM_API_KEY`

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
