"""
Parler-TTS voice *descriptions* loaded from a JSON seed (packaged or custom path).

Users pick a **voice name** (seed key) and **gender** (`female` / `male`). Optional raw
description still overrides via env or ``ParlerTTS(description=...)``.
"""

from __future__ import annotations

import json
from functools import lru_cache
from importlib import resources
from pathlib import Path
from typing import Any

_SEED_RESOURCE = "seeds/parler_voices.json"


def _read_seed_bytes(seed_path: Path | None) -> bytes:
    if seed_path is not None:
        return Path(seed_path).expanduser().resolve().read_bytes()
    return resources.files(__package__).joinpath(_SEED_RESOURCE).read_bytes()


@lru_cache(maxsize=16)
def _load_seed_cached(seed_path_resolved: str | None) -> dict[str, Any]:
    raw = _read_seed_bytes(Path(seed_path_resolved) if seed_path_resolved else None)
    data = json.loads(raw.decode("utf-8"))
    voices = data.get("voices")
    if not isinstance(voices, dict) or not voices:
        raise ValueError("Parler voice seed must contain a non-empty 'voices' object.")
    for name, row in voices.items():
        if not isinstance(row, dict):
            raise ValueError(f"Parler voice '{name}' must be an object with female/male strings.")
        for g in ("female", "male"):
            v = row.get(g)
            if not isinstance(v, str) or not v.strip():
                raise ValueError(f"Parler voice '{name}' needs a non-empty '{g}' description.")
    return data


def load_parler_voice_seed(*, seed_path: Path | str | None = None) -> dict[str, Any]:
    """
    Load and validate the voice seed. ``seed_path`` defaults to the packaged JSON.

    Cached by resolved path string (``None`` = packaged default).
    """
    if seed_path is not None and not str(seed_path).strip():
        seed_path = None
    key: str | None
    if seed_path is None:
        key = None
    else:
        key = str(Path(seed_path).expanduser().resolve())
    return _load_seed_cached(key)


def reload_parler_voice_seed_cache() -> None:
    """Clear seed cache (tests)."""
    _load_seed_cached.cache_clear()


def normalize_parler_language(code: str) -> str:
    """Map BCP-47-ish tags to a default voice name; unknown → ``en``."""
    s = code.strip().lower().replace("_", "-")
    if not s:
        return "en"
    if s.startswith("zh"):
        return "zh"
    if s.startswith("pt"):
        return "pt"
    base = s.split("-", 1)[0]
    data = load_parler_voice_seed()
    if base in data["voices"]:
        return base
    return str(data.get("default_voice") or "en")


def parler_seed_voice_names(*, seed_path: Path | str | None = None) -> tuple[str, ...]:
    """Sorted voice names defined in the seed."""
    data = load_parler_voice_seed(seed_path=seed_path)
    return tuple(sorted(data["voices"]))


def parler_voice_description(
    voice_name: str,
    gender: str,
    *,
    seed_path: Path | str | None = None,
) -> str:
    """
    Resolve Parler English description for ``voice_name`` and ``gender``.

    ``gender`` is ``female`` or ``male`` (case-insensitive); other values → ``female``.
    ``voice_name`` is matched case-insensitively. Unknown names raise ``ValueError``.
    """
    g = gender.strip().lower()
    if g != "male":
        g = "female"
    key = voice_name.strip().lower()
    data = load_parler_voice_seed(seed_path=seed_path)
    voices: dict[str, Any] = data["voices"]
    row = voices.get(key)
    if row is None:
        # case-insensitive lookup
        lower_map = {str(k).lower(): k for k in voices}
        canon = lower_map.get(key)
        if canon is None:
            available = ", ".join(sorted(voices))
            raise ValueError(
                f"Unknown Parler voice name {voice_name!r}. "
                f"Defined in seed: {available}"
            )
        row = voices[canon]
    text = row.get(g)
    if not isinstance(text, str) or not text.strip():
        raise ValueError(f"Parler voice {voice_name!r} has no {g!r} description in seed.")
    return text.strip()


# Backward-compatible aliases (older docs / tests)
def parler_preset_languages() -> tuple[str, ...]:
    """Deprecated alias: use :func:`parler_seed_voice_names`."""
    return parler_seed_voice_names()


def parler_preset_description(language_code: str, gender: str) -> str:
    """
    Deprecated alias: same as ``parler_voice_description(normalize_parler_language(...), gender)``.
    """
    return parler_voice_description(normalize_parler_language(language_code), gender)
