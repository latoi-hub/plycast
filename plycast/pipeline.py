from __future__ import annotations

from pathlib import Path

from plycast.models import PipelineInput, PipelineOutput
from plycast.pipelines.composed import run_read_translate_audio
from plycast.providers.base import TTSProvider, TranslatorProvider


class PlycastPipeline:
    """Backward-compatible wrapper around ``run_read_translate_audio``."""

    def __init__(
        self,
        translator: TranslatorProvider,
        tts: TTSProvider,
    ) -> None:
        self.translator = translator
        self.tts = tts

    def run(self, payload: PipelineInput, output_dir: Path) -> PipelineOutput:
        return run_read_translate_audio(
            payload.source_path,
            output_dir=output_dir,
            translator=self.translator,
            tts=self.tts,
            source_language=payload.source_language,
            target_language=payload.target_language,
            max_chunk_chars=payload.max_chunk_chars,
            audio_format=payload.audio_format,
        )
