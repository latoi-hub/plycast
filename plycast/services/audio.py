"""Speech synthesis: TTS factories and :class:`AudioService` wrapper."""

from __future__ import annotations

from pathlib import Path

from plycast.providers.base import TTSProvider
from plycast.providers.tts import EspeakTTS, SystemSayTTS, TextFileTTS


class AudioService:
    """Wraps a :class:`~plycast.providers.base.TTSProvider` for ``synthesize`` calls."""

    @staticmethod
    def make_system_say_tts(voice: str | None = None) -> TTSProvider:
        return SystemSayTTS(voice=voice)

    @staticmethod
    def make_text_file_tts() -> TTSProvider:
        return TextFileTTS()

    @staticmethod
    def make_espeak_tts(voice: str | None = None) -> TTSProvider:
        return EspeakTTS(voice=voice)

    def __init__(self, tts: TTSProvider) -> None:
        self._tts = tts

    def synthesize(
        self,
        text: str,
        *,
        language: str,
        output_path: Path,
    ) -> Path:
        return self._tts.synthesize(text, language, output_path)
