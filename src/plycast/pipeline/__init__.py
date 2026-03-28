"""
High-level workflows: book-style API (:mod:`plycast.pipeline.convert`),
composed read/translate/audio steps, and :class:`PlycastPipeline`.
"""

from __future__ import annotations

from .composed import (
    run_read_audio,
    run_read_text_only,
    run_read_translate,
    run_read_translate_audio,
)
from .convert import (
    ConvertResult,
    InspectResult,
    TranslateResult,
    TtsResult,
    convert_book,
    inspect_book,
    load_book,
    result_to_json,
    synthesize_book,
    translate_book,
)
from .facade import PlycastPipeline

__all__ = [
    "ConvertResult",
    "InspectResult",
    "PlycastPipeline",
    "TranslateResult",
    "TtsResult",
    "convert_book",
    "inspect_book",
    "load_book",
    "result_to_json",
    "run_read_audio",
    "run_read_text_only",
    "run_read_translate",
    "run_read_translate_audio",
    "synthesize_book",
    "translate_book",
]
