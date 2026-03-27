from __future__ import annotations

from plycast.providers.translation_prompt import translation_prompt

from .client import OpenAIClient


class OpenAITranslator:
    def __init__(
        self,
        api_key: str | None = None,
        model: str = "gpt-4o-mini",
        base_url: str = "https://api.openai.com/v1",
        timeout: int = 60,
        *,
        client: OpenAIClient | None = None,
    ) -> None:
        self.model = model
        if client is not None:
            self._client = client
        else:
            if not api_key:
                raise ValueError("api_key is required when client is not provided")
            self._client = OpenAIClient(
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
        raw = self._client.chat_completions(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a translation engine."},
                {
                    "role": "user",
                    "content": translation_prompt(
                        text=text,
                        source_language=source_language,
                        target_language=target_language,
                    ),
                },
            ],
            temperature=0,
        )
        return self._client.assistant_message_content(raw)
