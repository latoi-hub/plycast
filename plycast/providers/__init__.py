"""
Public API for translation and TTS adapters.

Subpackages hold vendor-specific code (``openai/``, ``anthropic/``, ``libretranslate/``,
``tts/``). For app-level wiring, see :mod:`plycast.services`.

``*Connector`` names are aliases for ``*Client`` (backward compatibility with the old
``connectors`` package); prefer ``OpenAIClient``, ``AnthropicClient``, ``LibreTranslateClient``.
"""

from __future__ import annotations

# Protocols
from .base import TTSProvider, TranslatorProvider

# Vendors
from .anthropic import AnthropicClient, AnthropicTranslator
from .identity import IdentityTranslator
from .libretranslate import LibreTranslateClient, LibreTranslateTranslator
from .openai import BearerToken, OpenAIClient, OpenAITranslator
from .tts import SystemSayTTS, TextFileTTS

# LLM
from .llm import LLMTranslator, infer_llm_provider

# Shared prompt helper (used by LLM translators)
from .translation_prompt import translation_prompt


__all__ = [
    "AnthropicClient",
    "AnthropicTranslator",
    "IdentityTranslator",
    "LLMTranslator",
    "LibreTranslateClient",
    "LibreTranslateTranslator",
    "OpenAIClient",
    "OpenAITranslator",
    "SystemSayTTS",
    "TextFileTTS",
    "TTSProvider",
    "TranslatorProvider",
    "infer_llm_provider",
]
