from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping


@dataclass(frozen=True, slots=True)
class ApiKeyHeader:
    header_name: str
    api_key: str

    def headers(self) -> Mapping[str, str]:
        return {self.header_name: self.api_key}


@dataclass(frozen=True, slots=True)
class CompositeAuth:
    parts: tuple[object, ...]

    def headers(self) -> dict[str, str]:
        merged: dict[str, str] = {}
        for part in self.parts:
            if hasattr(part, "headers"):
                merged.update(dict(part.headers()))  # type: ignore[arg-type]
        return merged


class AnthropicVersionHeader:
    def __init__(self, version: str) -> None:
        self._version = version

    def headers(self) -> dict[str, str]:
        return {"anthropic-version": self._version}
