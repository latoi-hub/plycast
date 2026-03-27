"""Unified LLM translation: OpenAI or Anthropic."""

from __future__ import annotations

from typing import Literal

from plycast.providers.anthropic.client import AnthropicClient
from plycast.providers.anthropic.translator import AnthropicTranslator
from plycast.providers.openai.client import OpenAIClient
from plycast.providers.openai.translator import OpenAITranslator


def infer_llm_provider(model: str) -> Literal["openai", "anthropic"]:
    """Guess vendor from model id (``gpt-*`` / ``claude*``)."""
    m = model.strip().lower()
    if m.startswith("claude"):
        return "anthropic"
    if m.startswith(("gpt-", "o1", "o3", "o4", "chatgpt")):
        return "openai"
    raise ValueError(
        f"Cannot infer LLM provider from model {model!r}; "
        "pass provider='openai' or 'anthropic' explicitly."
    )


class LLMTranslator:
    """
    Routes to :class:`OpenAITranslator` or :class:`AnthropicTranslator`
    based on ``provider`` or inferred from ``model``.
    """

    def __init__(
        self,
        api_key: str,
        model: str,
        *,
        provider: Literal["openai", "anthropic"] | None = None,
        base_url: str | None = None,
        timeout: int = 60,
    ) -> None:
        pv = provider if provider is not None else infer_llm_provider(model)
        self.provider: Literal["openai", "anthropic"] = pv
        self.model = model
        if pv == "openai":
            cli = OpenAIClient(
                api_key=api_key,
                base_url=base_url or "https://api.openai.com/v1",
                timeout=timeout,
            )
            self._impl = OpenAITranslator(model=model, client=cli)
        else:
            cli = AnthropicClient(
                api_key=api_key,
                base_url=base_url or "https://api.anthropic.com/v1",
                timeout=timeout,
            )
            self._impl = AnthropicTranslator(model=model, client=cli)

    def translate(
        self,
        text: str,
        source_language: str,
        target_language: str,
    ) -> str:
        return self._impl.translate(text, source_language, target_language)
