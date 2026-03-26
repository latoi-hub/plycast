from __future__ import annotations

import json
from urllib import error, request


def _prompt(text: str, source_language: str, target_language: str) -> str:
    return (
        "Translate the following text.\n"
        f"Source language: {source_language}\n"
        f"Target language: {target_language}\n\n"
        "Rules:\n"
        "- Preserve meaning, tone, and paragraph structure.\n"
        "- Do not summarize.\n"
        "- Return translated text only.\n\n"
        f"Text:\n{text}"
    )


class OpenAITranslator:
    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4o-mini",
        base_url: str = "https://api.openai.com/v1",
        timeout: int = 60,
    ) -> None:
        self.api_key = api_key
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def translate(
        self,
        text: str,
        source_language: str,
        target_language: str,
    ) -> str:
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You are a translation engine."},
                {
                    "role": "user",
                    "content": _prompt(
                        text=text,
                        source_language=source_language,
                        target_language=target_language,
                    ),
                },
            ],
            "temperature": 0,
        }
        req = request.Request(
            f"{self.base_url}/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            },
            method="POST",
        )
        try:
            with request.urlopen(req, timeout=self.timeout) as resp:
                raw = resp.read().decode("utf-8")
        except error.HTTPError as exc:
            details = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(
                f"OpenAI HTTP error {exc.code}: {details}"
            ) from exc
        except error.URLError as exc:
            raise RuntimeError(f"OpenAI request failed: {exc.reason}") from exc

        data = json.loads(raw)
        content = data.get("choices", [{}])[0].get("message", {}).get("content")
        if not content:
            raise RuntimeError("OpenAI response missing message content")
        return str(content).strip()


class AnthropicTranslator:
    def __init__(
        self,
        api_key: str,
        model: str = "claude-3-5-haiku-latest",
        base_url: str = "https://api.anthropic.com/v1",
        timeout: int = 60,
    ) -> None:
        self.api_key = api_key
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def translate(
        self,
        text: str,
        source_language: str,
        target_language: str,
    ) -> str:
        payload = {
            "model": self.model,
            "max_tokens": 4096,
            "temperature": 0,
            "system": "You are a translation engine.",
            "messages": [
                {
                    "role": "user",
                    "content": _prompt(
                        text=text,
                        source_language=source_language,
                        target_language=target_language,
                    ),
                }
            ],
        }
        req = request.Request(
            f"{self.base_url}/messages",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
            },
            method="POST",
        )
        try:
            with request.urlopen(req, timeout=self.timeout) as resp:
                raw = resp.read().decode("utf-8")
        except error.HTTPError as exc:
            details = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(
                f"Anthropic HTTP error {exc.code}: {details}"
            ) from exc
        except error.URLError as exc:
            raise RuntimeError(
                f"Anthropic request failed: {exc.reason}"
            ) from exc

        data = json.loads(raw)
        content = data.get("content", [])
        text_value = content[0].get("text") if content else None
        if not text_value:
            raise RuntimeError("Anthropic response missing text")
        return str(text_value).strip()
