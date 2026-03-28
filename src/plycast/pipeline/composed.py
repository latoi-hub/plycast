"""Named compositions of read → translate → audio services."""

from __future__ import annotations

from pathlib import Path

from plycast.core.models import (
    PipelineOutput,
    ReadAudioOnlyResult,
    ReadTextResult,
    TranslateOnlyResult,
)
from plycast.io.read_text import ReadTextService
from plycast.engines.translate.base import TranslatorProvider
from plycast.engines.translate.service import TranslateService
from plycast.engines.tts.base import TTSProvider
from plycast.engines.tts.service import AudioService


def run_read_text_only(
    source_path: Path,
    *,
    output_dir: Path | None = None,
    output_stem: str | None = None,
    source_language: str | None = None,
) -> ReadTextResult:
    """Pipeline: extract text only. Optionally write extracted ``.txt``."""
    result = ReadTextService().read(
        source_path,
        source_language=source_language,
    )
    if output_dir is not None:
        output_dir.mkdir(parents=True, exist_ok=True)
        stem = output_stem if output_stem is not None else source_path.stem
        out = output_dir / f"{stem}.extracted.txt"
        out.write_text(result.text, encoding="utf-8")
    return result


def run_read_translate(
    source_path: Path,
    *,
    output_dir: Path,
    translator: TranslatorProvider,
    source_language: str,
    target_language: str,
    max_chunk_chars: int,
) -> TranslateOnlyResult:
    """Pipeline: read → translate (writes ``<stem>.<target>.txt``)."""
    output_dir.mkdir(parents=True, exist_ok=True)
    read = ReadTextService().read(
        source_path,
        source_language=source_language,
    )
    translated = TranslateService(translator).translate_text(
        read.text,
        source_language=source_language,
        target_language=target_language,
        max_chunk_chars=max_chunk_chars,
    )
    translated_path = output_dir / (
        f"{source_path.stem}.{target_language}.txt"
    )
    translated_path.write_text(translated, encoding="utf-8")
    return TranslateOnlyResult(
        source_path=source_path,
        translated_text=translated,
        translated_text_path=translated_path,
    )


def run_read_translate_audio(
    source_path: Path,
    *,
    output_dir: Path,
    translator: TranslatorProvider,
    tts: TTSProvider,
    source_language: str,
    target_language: str,
    max_chunk_chars: int,
    audio_format: str = "mp3",
) -> PipelineOutput:
    """Pipeline: read → translate → TTS (full plycast flow)."""
    tr = run_read_translate(
        source_path,
        output_dir=output_dir,
        translator=translator,
        source_language=source_language,
        target_language=target_language,
        max_chunk_chars=max_chunk_chars,
    )
    audio_ext = audio_format.lstrip(".").strip() or "mp3"
    audio_path = output_dir / (
        f"{source_path.stem}.{target_language}.{audio_ext}"
    )
    audio_path = AudioService(tts).synthesize(
        tr.translated_text,
        language=target_language,
        output_path=audio_path,
    )
    return PipelineOutput(
        translated_text_path=tr.translated_text_path,
        audio_path=audio_path,
        translated_text=tr.translated_text,
    )


def run_read_audio(
    source_path: Path,
    *,
    output_dir: Path,
    tts: TTSProvider,
    tts_language: str,
    audio_format: str = "mp3",
) -> ReadAudioOnlyResult:
    """Pipeline: read → TTS on source text (no translation)."""
    output_dir.mkdir(parents=True, exist_ok=True)
    read = ReadTextService().read(
        source_path,
        source_language=tts_language,
    )
    audio_ext = audio_format.lstrip(".").strip() or "mp3"
    audio_path = output_dir / (
        f"{source_path.stem}.{tts_language}.{audio_ext}"
    )
    audio_path = AudioService(tts).synthesize(
        read.text,
        language=tts_language,
        output_path=audio_path,
    )
    return ReadAudioOnlyResult(
        source_path=source_path,
        text=read.text,
        audio_path=audio_path,
    )
