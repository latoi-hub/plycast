"""OpenAI HTTP client (chat completions and future endpoints)."""

from __future__ import annotations

from typing import Any

from plycast.engines.translate.providers.http import post_json

from .auth import BearerToken


class OpenAIClient:
    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = "https://api.openai.com/v1",
        timeout: int = 60,
    ) -> None:
        self._auth = BearerToken(api_key)
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def chat_completions(
        self,
        *,
        model: str,
        messages: list[dict[str, str]],
        temperature: float = 0,
        extra: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
        }
        if extra:
            payload.update(extra)
        return post_json(
            f"{self.base_url}/chat/completions",
            payload,
            headers=self._auth.headers(),
            timeout=self.timeout,
        )

    def assistant_message_content(self, response: dict[str, Any]) -> str:
        content = response.get("choices", [{}])[0].get("message", {}).get("content")
        if not content:
            raise RuntimeError("OpenAI response missing message content")
        return str(content).strip()
