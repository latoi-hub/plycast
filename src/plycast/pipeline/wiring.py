"""Shared translator/TTS construction for Python API and CLI (single place)."""

from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path

from plycast.engines.translate.base import TranslatorProvider
from plycast.engines.tts.base import TTSProvider
from plycast.engines.translate.service import TranslateService
from plycast.engines.tts.service import AudioService


def load_dotenv_cwd(path: Path | None = None) -> None:
    p = path or Path.cwd() / ".env"
    if not p.exists():
        return
    for line in p.read_text(encoding="utf-8").splitlines():
        entry = line.strip()
        if not entry or entry.startswith("#") or "=" not in entry:
            continue
        key, value = entry.split("=", 1)
        key = key.strip()
        value = value.strip()
        if key and key not in os.environ:
            os.environ[key] = value


def get_env(*keys: str) -> str | None:
    for key in keys:
        value = os.getenv(key)
        if value:
            return value
    return None


def bcp47_primary_language(code: str) -> str:
    s = code.strip().lower().replace("_", "-")
    if not s:
        return ""
    return s.split("-", 1)[0]


def warn_if_parler_not_english_target(target_lang: str) -> None:
    if bcp47_primary_language(target_lang) == "en":
        return
    print(
        "plycast: Parler-TTS is intended for English speech only; "
        f"--target-lang {target_lang!r} may sound poor or wrong. "
        "Use --target-lang en for reliable audio, or choose --tts espeak / system_say for other languages.",
        file=sys.stderr,
    )


def default_tts_backend() -> str:
    if sys.platform == "darwin":
        return "system_say"
    try:
        if importlib.util.find_spec("parler_tts") is not None:
            return "parler"
    except (ImportError, ValueError):
        pass
    return "espeak"


def build_translator(
    *,
    translator: str,
    base_url: str | None,
    api_key: str | None,
    llm_model: str,
    llm_provider: str | None,
) -> TranslatorProvider:
    if translator == "libretranslate":
        bu = base_url or "https://libretranslate.com"
        key = api_key or get_env("LIBRETRANSLATE_API_KEY", "libretranslate-api-key")
        return TranslateService.make_libretranslate_translator(
            base_url=bu,
            api_key=key,
        )
    if translator == "llm":
        provider = llm_provider
        if provider is None:
            provider = TranslateService.infer_llm_provider(llm_model)
        if provider == "openai":
            key = api_key or get_env("OPENAI_API_KEY", "openai-api-key")
            bu = base_url or "https://api.openai.com/v1"
        else:
            key = api_key or get_env("ANTHROPIC_API_KEY", "anthropic-api-key")
            bu = base_url or "https://api.anthropic.com/v1"
        if not key:
            raise ValueError(f"Missing API key for LLM provider {provider}.")
        return TranslateService.make_llm_translator(
            api_key=key,
            model=llm_model,
            provider=provider,
            base_url=bu,
        )
    return TranslateService.make_identity_translator()


def build_tts(
    *,
    tts: str,
    voice: str | None,
    parler_voice: str | None,
    parler_gender: str | None,
    parler_seed: str | None,
    target_lang_for_parler_warn: str | None = None,
) -> TTSProvider:
    if tts == "system_say":
        return AudioService.make_system_say_tts(voice=voice)
    if tts == "espeak":
        return AudioService.make_espeak_tts(voice=voice)
    if tts == "parler":
        if target_lang_for_parler_warn:
            warn_if_parler_not_english_target(target_lang_for_parler_warn)
        return AudioService.make_parler_tts(
            description=voice,
            parler_voice=parler_voice,
            gender=parler_gender,
            seed_path=parler_seed,
        )
    return AudioService.make_text_file_tts()
