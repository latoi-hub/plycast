"""Shared JSON HTTP helpers for provider clients."""

from __future__ import annotations

import json
from typing import Any
from urllib import error, request


def post_json(
    url: str,
    payload: dict[str, Any],
    *,
    headers: dict[str, str],
    timeout: int,
) -> dict[str, Any]:
    merged = {"Content-Type": "application/json", **headers}
    body = json.dumps(payload).encode("utf-8")
    req = request.Request(url, data=body, headers=merged, method="POST")
    try:
        with request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8")
    except error.HTTPError as exc:
        details = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP error {exc.code}: {details}") from exc
    except error.URLError as exc:
        raise RuntimeError(f"Request failed: {exc.reason}") from exc
    return json.loads(raw)
