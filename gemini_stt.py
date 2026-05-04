"""Custom STT adapter: Gemini multimodal generateContent over Gemini API.

Used because the official google.STT (Chirp/Chirp2) mishears short Mandarin
phrases like 小爱 -> 小艾. Gemini 3.x preview models do better.

Supports both aistudio (api_key) and Vertex AI modes via env vars:
  GOOGLE_GENAI_USE_VERTEXAI=true + GOOGLE_CLOUD_PROJECT + GOOGLE_CLOUD_LOCATION
  -> use Vertex (HK VMs / regions blocked from aistudio)
Otherwise falls back to GEMINI_API_KEY.
"""

from __future__ import annotations

import io
import os
import wave
from typing import Any

from google import genai
from google.genai import types as genai_types

from livekit import rtc
from livekit.agents import APIConnectionError, APIConnectOptions, stt, utils
from livekit.agents.types import NOT_GIVEN, NotGivenOr


_DEFAULT_PROMPT = (
    "Transcribe this Chinese audio verbatim. "
    "Output only the transcription, no explanation, no punctuation other than "
    "what the speaker uses."
)


def _build_genai_client(api_key: str | None) -> genai.Client:
    use_vertex = os.environ.get("GOOGLE_GENAI_USE_VERTEXAI", "").lower() == "true"
    if use_vertex:
        return genai.Client(
            vertexai=True,
            project=os.environ["GOOGLE_CLOUD_PROJECT"],
            location=os.environ.get("GOOGLE_CLOUD_LOCATION", "global"),
        )
    api_key = api_key or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError(
            "Set GOOGLE_GENAI_USE_VERTEXAI=true (+ GOOGLE_CLOUD_PROJECT) for Vertex, "
            "or GEMINI_API_KEY for aistudio."
        )
    return genai.Client(api_key=api_key)


class GeminiSTT(stt.STT):
    def __init__(
        self,
        *,
        model: str = "gemini-3.1-flash-lite-preview",
        language: str = "cmn-Hans-CN",
        prompt: str = _DEFAULT_PROMPT,
        api_key: str | None = None,
    ) -> None:
        super().__init__(
            capabilities=stt.STTCapabilities(streaming=False, interim_results=False),
        )
        self._model = model
        self._language = language
        self._prompt = prompt
        self._client = _build_genai_client(api_key)

    @property
    def model(self) -> str:
        return self._model

    @property
    def provider(self) -> str:
        return "gemini"

    async def _recognize_impl(
        self,
        buffer: utils.AudioBuffer,
        *,
        language: NotGivenOr[str] = NOT_GIVEN,
        conn_options: APIConnectOptions,
    ) -> stt.SpeechEvent:
        frame = rtc.combine_audio_frames(buffer)
        wav_bytes = _pcm_to_wav(
            frame.data.tobytes(),
            sample_rate=frame.sample_rate,
            num_channels=frame.num_channels,
        )

        try:
            response = await self._client.aio.models.generate_content(
                model=self._model,
                contents=[
                    self._prompt,
                    genai_types.Part.from_bytes(
                        data=wav_bytes, mime_type="audio/wav"
                    ),
                ],
                # Gemini 3 Flash defaults to thinking ON; for transcription this
                # adds seconds of latency for zero benefit. MINIMAL = no thinking.
                config=genai_types.GenerateContentConfig(
                    thinking_config=genai_types.ThinkingConfig(thinking_level="MINIMAL"),
                ),
            )
        except Exception as e:  # noqa: BLE001
            raise APIConnectionError() from e

        text = (response.text or "").strip()
        lang_tag: Any = language if language else self._language

        return stt.SpeechEvent(
            type=stt.SpeechEventType.FINAL_TRANSCRIPT,
            alternatives=[stt.SpeechData(language=lang_tag, text=text)],
        )


def _pcm_to_wav(pcm: bytes, *, sample_rate: int, num_channels: int) -> bytes:
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(num_channels)
        w.setsampwidth(2)  # int16
        w.setframerate(sample_rate)
        w.writeframes(pcm)
    return buf.getvalue()
