from __future__ import annotations

from .client import LibreTranslateClient


class LibreTranslateTranslator:
    def __init__(
        self,
        base_url: str,
        api_key: str | None = None,
        timeout: int = 30,
        *,
        client: LibreTranslateClient | None = None,
    ) -> None:
        self._client = client or LibreTranslateClient(
            base_url=base_url,
            api_key=api_key,
            timeout=timeout,
        )

    def translate(
        self,
        text: str,
        source_language: str,
        target_language: str,
    ) -> str:
        return self._client.translate(
            text,
            source=source_language,
            target=target_language,
        )
