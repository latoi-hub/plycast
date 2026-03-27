"""Chunked translation and translator construction (service entry point)."""

from __future__ import annotations

from typing import Literal

from plycast.providers import (
    AnthropicTranslator,
    IdentityTranslator,
    LLMTranslator,
    LibreTranslateTranslator,
    OpenAITranslator,
)
from plycast.providers.base import TranslatorProvider
from plycast.providers.llm import infer_llm_provider
from plycast.text import chunk_text


class TranslateService:
    """Chunked translate over a :class:`~plycast.providers.base.TranslatorProvider`."""

    infer_llm_provider = staticmethod(infer_llm_provider)

    @staticmethod
    def make_identity_translator() -> TranslatorProvider:
        return IdentityTranslator()

    @staticmethod
    def make_libretranslate_translator(
        base_url: str,
        api_key: str | None = None,
    ) -> TranslatorProvider:
        return LibreTranslateTranslator(base_url=base_url, api_key=api_key)

    @staticmethod
    def make_openai_translator(
        api_key: str,
        model: str = "gpt-4o-mini",
        *,
        base_url: str = "https://api.openai.com/v1",
    ) -> TranslatorProvider:
        return OpenAITranslator(
            api_key=api_key,
            model=model,
            base_url=base_url,
        )

    @staticmethod
    def make_anthropic_translator(
        api_key: str,
        model: str = "claude-3-5-haiku-latest",
        *,
        base_url: str = "https://api.anthropic.com/v1",
    ) -> TranslatorProvider:
        return AnthropicTranslator(
            api_key=api_key,
            model=model,
            base_url=base_url,
        )

    @staticmethod
    def make_llm_translator(
        api_key: str,
        model: str,
        *,
        provider: Literal["openai", "anthropic"] | None = None,
        base_url: str | None = None,
    ) -> TranslatorProvider:
        return LLMTranslator(
            api_key=api_key,
            model=model,
            provider=provider,
            base_url=base_url,
        )

    def __init__(self, translator: TranslatorProvider) -> None:
        self._translator = translator

    def translate_text(
        self,
        text: str,
        *,
        source_language: str,
        target_language: str,
        max_chunk_chars: int,
    ) -> str:
        chunks = chunk_text(text, max_chunk_chars)
        translated = [
            self._translator.translate(
                text=chunk,
                source_language=source_language,
                target_language=target_language,
            )
            for chunk in chunks
        ]
        return "\n\n".join(translated)
