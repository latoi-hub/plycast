"""
High-level public workflow functions (Layer 1). CLI and scripts should call these.

Core logic stays in :mod:`plycast.io`, :mod:`plycast.engines.translate`,
:mod:`plycast.engines.tts`, and :mod:`plycast.pipeline.composed`; this module only
wires options and returns stable result objects.
"""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from plycast.core.models import (
    ConvertResult,
    InspectResult,
    PipelineInput,
    ReadTextResult,
    TranslateResult,
    TtsResult,
)
from plycast.io.read_text import ReadTextService
from plycast.pipeline.composed import run_read_audio, run_read_translate
from plycast.pipeline.facade import PlycastPipeline

from .wiring import build_translator, build_tts, load_dotenv_cwd


def load_book(
    path: str | Path,
    *,
    source_language: str | None = None,
) -> ReadTextResult:
    """
    Load and extract text from a supported file
    (txt, md, pdf, docx, image OCR, …).

    Returns :class:`~plycast.core.models.ReadTextResult` (normalized ingest
    result; a richer ``Book`` type may be added later).
    """
    load_dotenv_cwd()
    return ReadTextService().read(Path(path), source_language=source_language)


def translate_book(
    path: str | Path,
    *,
    source_lang: str,
    target_lang: str,
    output_dir: str | Path = "dist",
    translator: str = "libretranslate",
    base_url: str | None = None,
    api_key: str | None = None,
    llm_model: str = "gpt-4o-mini",
    llm_provider: str | None = None,
    max_chunk_chars: int = 1500,
) -> TranslateResult:
    """
    Read ``path``, translate to ``target_lang``,
    write ``<stem>.<target>.txt``.
    """
    load_dotenv_cwd()
    tr = build_translator(
        translator=translator,
        base_url=base_url,
        api_key=api_key,
        llm_model=llm_model,
        llm_provider=llm_provider,
    )
    out = run_read_translate(
        Path(path),
        output_dir=Path(output_dir),
        translator=tr,
        source_language=source_lang,
        target_language=target_lang,
        max_chunk_chars=max_chunk_chars,
    )
    return TranslateResult(
        source_path=out.source_path,
        translated_text=out.translated_text,
        translated_text_path=out.translated_text_path,
        source_language=source_lang,
        target_language=target_lang,
    )


def synthesize_book(
    path: str | Path,
    *,
    tts_language: str,
    output_dir: str | Path = "dist",
    tts: str = "espeak",
    voice: str | None = None,
    parler_voice: str | None = None,
    parler_gender: str | None = None,
    parler_seed: str | None = None,
    audio_format: str = "mp3",
) -> TtsResult:
    """
    Read ``path`` and synthesize speech for extracted text
    (no translation).
    """
    load_dotenv_cwd()
    backend = build_tts(
        tts=tts,
        voice=voice,
        parler_voice=parler_voice,
        parler_gender=parler_gender,
        parler_seed=parler_seed,
        target_lang_for_parler_warn=tts_language if tts == "parler" else None,
    )
    out = run_read_audio(
        Path(path),
        output_dir=Path(output_dir),
        tts=backend,
        tts_language=tts_language,
        audio_format=audio_format,
    )
    return TtsResult(
        source_path=out.source_path,
        text=out.text,
        audio_path=out.audio_path,
        tts_language=tts_language,
    )


def convert_book(
    path: str | Path,
    *,
    source_lang: str,
    target_lang: str,
    output_dir: str | Path = "dist",
    translator: str = "libretranslate",
    base_url: str | None = None,
    api_key: str | None = None,
    llm_model: str = "gpt-4o-mini",
    llm_provider: str | None = None,
    tts: str | None = None,
    voice: str | None = None,
    parler_voice: str | None = None,
    parler_gender: str | None = None,
    parler_seed: str | None = None,
    max_chunk_chars: int = 1500,
    audio_format: str = "mp3",
) -> ConvertResult:
    """
    Full pipeline: read → translate → TTS
    (same as :class:`~plycast.pipeline.facade.PlycastPipeline`).
    """
    load_dotenv_cwd()
    from .wiring import default_tts_backend

    tts_backend = tts if tts is not None else default_tts_backend()
    tr = build_translator(
        translator=translator,
        base_url=base_url,
        api_key=api_key,
        llm_model=llm_model,
        llm_provider=llm_provider,
    )
    tts_provider = build_tts(
        tts=tts_backend,
        voice=voice,
        parler_voice=parler_voice,
        parler_gender=parler_gender,
        parler_seed=parler_seed,
        target_lang_for_parler_warn=target_lang,
    )
    pipe = PlycastPipeline(translator=tr, tts=tts_provider)
    payload = PipelineInput(
        source_path=Path(path),
        source_language=source_lang,
        target_language=target_lang,
        max_chunk_chars=max_chunk_chars,
        audio_format=audio_format,
    )
    out = pipe.run(payload, Path(output_dir))
    return ConvertResult(
        source_path=payload.source_path,
        output_dir=Path(output_dir),
        translated_text_path=out.translated_text_path,
        audio_path=out.audio_path,
        translated_text=out.translated_text,
        source_language=source_lang,
        target_language=target_lang,
    )


def inspect_book(
    path: str | Path,
    *,
    source_language: str | None = None,
    preview_chars: int = 240,
) -> InspectResult:
    """Parse input and return basic metadata plus an optional text preview."""
    load_dotenv_cwd()
    p = Path(path)
    st = p.stat()
    text_preview: str | None = None
    nchars: int | None = None
    try:
        r = ReadTextService().read(p, source_language=source_language)
        nchars = len(r.text)
        text_preview = r.text[:preview_chars] if r.text else ""
    except Exception as exc:  # noqa: BLE001 — inspect is diagnostic
        text_preview = f"<could not extract text: {exc}>"
    return InspectResult(
        path=p.resolve(),
        suffix=p.suffix.lower(),
        size_bytes=st.st_size,
        text_char_count=nchars,
        preview=text_preview,
        source_language=source_language,
    )


def result_to_json(result: Any) -> str:
    """Serialize a result dataclass to JSON (for CLI ``--json``)."""
    d = (
        result.to_json_dict()
        if hasattr(result, "to_json_dict")
        else asdict(result)
    )
    return json.dumps(d, indent=2, ensure_ascii=False)
