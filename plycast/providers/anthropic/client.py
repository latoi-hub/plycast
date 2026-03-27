"""Anthropic Messages API client."""

from __future__ import annotations

from typing import Any

from plycast.providers.http import post_json

from .auth import ApiKeyHeader, AnthropicVersionHeader, CompositeAuth


class AnthropicClient:
    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = "https://api.anthropic.com/v1",
        api_version: str = "2023-06-01",
        timeout: int = 60,
    ) -> None:
        self._auth = CompositeAuth(
            (
                ApiKeyHeader("x-api-key", api_key),
                AnthropicVersionHeader(api_version),
            )
        )
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def messages(
        self,
        *,
        model: str,
        messages: list[dict[str, Any]],
        max_tokens: int = 4096,
        temperature: float = 0,
        system: str | None = None,
        extra: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "model": model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": messages,
        }
        if system is not None:
            payload["system"] = system
        if extra:
            payload.update(extra)
        return post_json(
            f"{self.base_url}/messages",
            payload,
            headers=dict(self._auth.headers()),
            timeout=self.timeout,
        )

    def first_text_block(self, response: dict[str, Any]) -> str:
        content = response.get("content", [])
        text_value = content[0].get("text") if content else None
        if not text_value:
            raise RuntimeError("Anthropic response missing text")
        return str(text_value).strip()
