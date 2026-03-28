"""Backward-compatible :class:`PlycastPipeline` wrapper (library API)."""

from __future__ import annotations

from pathlib import Path

from plycast.core.models import PipelineInput, PipelineOutput
from plycast.pipeline.composed import run_read_translate_audio
from plycast.engines.translate.base import TranslatorProvider
from plycast.engines.tts.base import TTSProvider


class PlycastPipeline:
    """Thin wrapper around :func:`~plycast.pipeline.composed.run_read_translate_audio`."""

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
