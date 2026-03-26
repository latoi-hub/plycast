from __future__ import annotations

import json
from urllib import error, request


class LibreTranslateTranslator:
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
        source_language: str,
        target_language: str,
    ) -> str:
        payload: dict[str, str] = {
            "q": text,
            "source": source_language,
            "target": target_language,
            "format": "text",
        }
        if self.api_key:
            payload["api_key"] = self.api_key

        body = json.dumps(payload).encode("utf-8")
        req = request.Request(
            f"{self.base_url}/translate",
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with request.urlopen(req, timeout=self.timeout) as resp:
                raw = resp.read().decode("utf-8")
        except error.HTTPError as exc:
            details = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(
                f"LibreTranslate HTTP error {exc.code}: {details}"
            ) from exc
        except error.URLError as exc:
            raise RuntimeError(
                f"LibreTranslate request failed: {exc.reason}"
            ) from exc

        data = json.loads(raw)
        translated = data.get("translatedText")
        if not translated:
            raise RuntimeError("LibreTranslate response missing translatedText")
        return str(translated)
