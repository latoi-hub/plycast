"""Speech synthesis: TTS factories and :class:`AudioService` wrapper."""

from __future__ import annotations

from pathlib import Path

from plycast.engines.tts.base import TTSProvider
from plycast.engines.tts.providers import EspeakTTS, SystemSayTTS, TextFileTTS


class AudioService:
    """Wraps a :class:`~plycast.engines.tts.base.TTSProvider` for ``synthesize`` calls."""

    @staticmethod
    def make_system_say_tts(voice: str | None = None) -> TTSProvider:
        return SystemSayTTS(voice=voice)

    @staticmethod
    def make_text_file_tts() -> TTSProvider:
        return TextFileTTS()

    @staticmethod
    def make_espeak_tts(voice: str | None = None) -> TTSProvider:
        return EspeakTTS(voice=voice)

    @staticmethod
    def make_parler_tts(
        description: str | None = None,
        *,
        parler_voice: str | None = None,
        gender: str | None = None,
        seed_path: str | Path | None = None,
        model_name: str | None = None,
        device: str | None = None,
        max_chunk_chars: int = 450,
    ) -> TTSProvider:
        """
        ``description``: raw Parler prompt (overrides seed; CLI ``--voice`` when parler).
        ``parler_voice``: name in ``seeds/parler_voices.json`` (or custom seed).
        ``gender``: ``female`` or ``male``. Parler is **English-centric**; omit
        ``parler_voice`` to derive a default seed key from ``--target-lang`` at synthesize time.
        """
        from plycast.engines.tts.providers.parler import ParlerTTS

        return ParlerTTS(
            model_name=model_name,
            device=device,
            description=description,
            parler_voice=parler_voice,
            gender=gender,
            seed_path=seed_path,
            max_chunk_chars=max_chunk_chars,
        )

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
