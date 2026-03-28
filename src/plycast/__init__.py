"""
plycast — ingest long-form text, translate, synthesize audio.

**Public API (preferred):** workflow functions mirror the CLI.

**Layers:** :mod:`plycast.pipeline` → :mod:`plycast.io` /
:mod:`plycast.engines.translate` / :mod:`plycast.engines.tts`.
"""

from __future__ import annotations

from .pipeline import (
    ConvertResult,
    InspectResult,
    PlycastPipeline,
    TranslateResult,
    TtsResult,
    convert_book,
    inspect_book,
    load_book,
    synthesize_book,
    translate_book,
)
from .engines.translate.providers import (
    IdentityTranslator,
    LLMTranslator,
    LibreTranslateTranslator,
    infer_llm_provider,
)
from .engines.tts.providers import EspeakTTS, ParlerTTS, SystemSayTTS, TextFileTTS

__all__ = [
    "ConvertResult",
    "EspeakTTS",
    "ParlerTTS",
    "IdentityTranslator",
    "InspectResult",
    "LLMTranslator",
    "LibreTranslateTranslator",
    "PlycastPipeline",
    "SystemSayTTS",
    "TextFileTTS",
    "TranslateResult",
    "TtsResult",
    "convert_book",
    "infer_llm_provider",
    "inspect_book",
    "load_book",
    "synthesize_book",
    "translate_book",
]
