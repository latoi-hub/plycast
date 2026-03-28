from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class BearerToken:
    """``Authorization: Bearer <token>`` for OpenAI-compatible APIs."""

    token: str

    def headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.token}"}
