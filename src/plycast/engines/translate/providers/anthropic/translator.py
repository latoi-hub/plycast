from __future__ import annotations

from plycast.engines.translate.providers.translation_prompt import translation_prompt

from .client import AnthropicClient


class AnthropicTranslator:
    def __init__(
        self,
        api_key: str | None = None,
        model: str = "claude-3-5-haiku-latest",
        base_url: str = "https://api.anthropic.com/v1",
        timeout: int = 60,
        *,
        client: AnthropicClient | None = None,
    ) -> None:
        self.model = model
        if client is not None:
            self._client = client
        else:
            if not api_key:
                raise ValueError("api_key is required when client is not provided")
            self._client = AnthropicClient(
                api_key=api_key,
                base_url=base_url,
                timeout=timeout,
            )

    def translate(
        self,
        text: str,
        source_language: str,
        target_language: str,
    ) -> str:
        raw = self._client.messages(
            model=self.model,
            system="You are a translation engine.",
            messages=[
                {
                    "role": "user",
                    "content": translation_prompt(
                        text=text,
                        source_language=source_language,
                        target_language=target_language,
                    ),
                }
            ],
            max_tokens=4096,
            temperature=0,
        )
        return self._client.first_text_block(raw)
