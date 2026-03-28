from __future__ import annotations

from plycast.engines.translate.providers.http import post_json


class LibreTranslateClient:
    def __init__(
        self,
        base_url: str,
        api_key: str | None = None,
        timeout: int = 30,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout

    def translate(
        self,
        text: str,
        *,
        source: str,
        target: str,
        format_: str = "text",
    ) -> str:
        payload: dict[str, str] = {
            "q": text,
            "source": source,
            "target": target,
            "format": format_,
        }
        if self.api_key:
            payload["api_key"] = self.api_key
        data = post_json(
            f"{self.base_url}/translate",
            payload,
            headers={},
            timeout=self.timeout,
        )
        translated = data.get("translatedText")
        if not translated:
            raise RuntimeError("LibreTranslate response missing translatedText")
        return str(translated)
