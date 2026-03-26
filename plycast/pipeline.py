from __future__ import annotations

from pathlib import Path

from .models import PipelineInput, PipelineOutput
from .providers.base import TTSProvider, TranslatorProvider
from .text import chunk_text, read_text_file


class PlycastPipeline:
    def __init__(self, translator: TranslatorProvider, tts: TTSProvider) -> None:
        self.translator = translator
        self.tts = tts

    def run(self, payload: PipelineInput, output_dir: Path) -> PipelineOutput:
        output_dir.mkdir(parents=True, exist_ok=True)
        source_text = read_text_file(payload.source_path)
        chunks = chunk_text(source_text, payload.max_chunk_chars)

        translated_chunks = [
            self.translator.translate(
                text=chunk,
                source_language=payload.source_language,
                target_language=payload.target_language,
            )
            for chunk in chunks
        ]
        translated_text = "\n\n".join(translated_chunks)

        translated_path = output_dir / (
            f"{payload.source_path.stem}.{payload.target_language}.txt"
        )
        translated_path.write_text(translated_text, encoding="utf-8")

        audio_ext = payload.audio_format.lstrip(".").strip() or "mp3"
        audio_path = output_dir / (
            f"{payload.source_path.stem}.{payload.target_language}.{audio_ext}"
        )
        audio_path = self.tts.synthesize(
            text=translated_text,
            language=payload.target_language,
            output_path=audio_path,
        )
        return PipelineOutput(
            translated_text_path=translated_path,
            audio_path=audio_path,
            translated_text=translated_text,
        )
