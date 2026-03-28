from __future__ import annotations

import argparse
import importlib.util
import os
import sys
from pathlib import Path

from .models import PipelineInput
from .pipeline import PlycastPipeline
from .services import AudioService, TranslateService


def _load_dotenv(path: Path) -> None:
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        entry = line.strip()
        if not entry or entry.startswith("#") or "=" not in entry:
            continue
        key, value = entry.split("=", 1)
        key = key.strip()
        value = value.strip()
        if key and key not in os.environ:
            os.environ[key] = value


def _get_env(*keys: str) -> str | None:
    for key in keys:
        value = os.getenv(key)
        if value:
            return value
    return None


def _bcp47_primary_language(code: str) -> str:
    s = code.strip().lower().replace("_", "-")
    if not s:
        return ""
    return s.split("-", 1)[0]


def _warn_if_parler_not_english_target(target_lang: str) -> None:
    """Parler checkpoints used by plycast are English-centric; spoken output quality is only reliable for English."""
    if _bcp47_primary_language(target_lang) == "en":
        return
    print(
        "plycast: Parler-TTS is intended for English speech only; "
        f"--target-lang {target_lang!r} may sound poor or wrong. "
        "Use --target-lang en for reliable audio, or choose --tts espeak / system_say for other languages.",
        file=sys.stderr,
    )


def _default_tts_backend() -> str:
    """macOS: ``say``; else Parler when installed, otherwise espeak-ng."""
    if sys.platform == "darwin":
        return "system_say"
    try:
        if importlib.util.find_spec("parler_tts") is not None:
            return "parler"
    except (ImportError, ValueError):
        pass
    return "espeak"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="plycast",
        description="Read long-form text, translate it, and generate audio output.",
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Input file (.txt/.md/.pdf/.docx or image for OCR)",
    )
    parser.add_argument("--output-dir", default="dist", help="Output directory")
    parser.add_argument("--source-lang", required=True, help="Source language code")
    parser.add_argument("--target-lang", required=True, help="Target language code")
    parser.add_argument(
        "--translator",
        choices=("identity", "libretranslate", "llm"),
        default="libretranslate",
        help="Translator backend (llm: openai/anthropic via --llm-model)",
    )
    parser.add_argument(
        "--base-url",
        default=None,
        help="Backend base URL: LibreTranslate server, or LLM API base (defaults per mode)",
    )
    parser.add_argument(
        "--api-key",
        default=None,
        help="API key for the active backend (LibreTranslate or LLM; env fallbacks apply)",
    )
    parser.add_argument(
        "--llm-model",
        default="gpt-4o-mini",
        help="With --translator llm: model id (default gpt-4o-mini); vendor inferred from "
        "name unless --llm-provider is set",
    )
    parser.add_argument(
        "--llm-provider",
        choices=("openai", "anthropic"),
        default=None,
        help="When --translator llm: force vendor (default: infer from --llm-model)",
    )
    parser.add_argument(
        "--tts",
        choices=("system_say", "espeak", "parler", "text_file"),
        default=_default_tts_backend(),
        help="system_say: macOS say; parler: neural TTS, English-only for reliable speech "
        "(needs pip install 'plycast[parler]'); espeak: espeak-ng/espeak; text_file: text only. "
        "Non-macOS default: parler if installed, else espeak.",
    )
    parser.add_argument(
        "--voice",
        default=None,
        help="system_say: macOS voice name; espeak: espeak-ng -v voice (e.g. vi, cmn); "
        "parler: full custom English description (overrides seed + --parler-voice)",
    )
    parser.add_argument(
        "--parler-voice",
        default=None,
        help="With --tts parler: seed voice name (e.g. en, laura, jon); 'vi' etc. are style "
        "labels only—spoken output should still be English text. Env: PLYCAST_PARLER_VOICE.",
    )
    parser.add_argument(
        "--parler-seed",
        default=None,
        help="With --tts parler: path to custom parler_voices.json (default: packaged seed). "
        "Env: PLYCAST_PARLER_SEED.",
    )
    parser.add_argument(
        "--parler-gender",
        choices=("female", "male"),
        default=None,
        help="With --tts parler: female or male row in the seed (ignored if --voice is set). "
        "Omit for PLYCAST_PARLER_GENDER or female.",
    )
    parser.add_argument(
        "--max-chunk-chars",
        type=int,
        default=1500,
        help="Max characters per translation chunk",
    )
    parser.add_argument(
        "--audio-format",
        choices=("mp3", "aiff", "wav", "m4a"),
        default="mp3",
        help="Audio output format (system_say / espeak convert when needed)",
    )
    return parser


def main() -> None:
    _load_dotenv(Path.cwd() / ".env")
    args = build_parser().parse_args()

    if args.translator == "libretranslate":
        base_url = args.base_url or "https://libretranslate.com"
        api_key = args.api_key or _get_env(
            "LIBRETRANSLATE_API_KEY",
            "libretranslate-api-key",
        )
        translator = TranslateService.make_libretranslate_translator(
            base_url=base_url,
            api_key=api_key,
        )
    elif args.translator == "llm":
        provider = args.llm_provider
        if provider is None:
            provider = TranslateService.infer_llm_provider(args.llm_model)
        if provider == "openai":
            key = args.api_key or _get_env(
                "OPENAI_API_KEY",
                "openai-api-key",
            )
            base_url = args.base_url or "https://api.openai.com/v1"
        else:
            key = args.api_key or _get_env(
                "ANTHROPIC_API_KEY",
                "anthropic-api-key",
            )
            base_url = args.base_url or "https://api.anthropic.com/v1"
        if not key:
            raise ValueError(f"Missing API key for LLM provider {provider}.")
        translator = TranslateService.make_llm_translator(
            api_key=key,
            model=args.llm_model,
            provider=provider,
            base_url=base_url,
        )
    else:
        translator = TranslateService.make_identity_translator()

    if args.tts == "system_say":
        tts = AudioService.make_system_say_tts(voice=args.voice)
    elif args.tts == "espeak":
        tts = AudioService.make_espeak_tts(voice=args.voice)
    elif args.tts == "parler":
        _warn_if_parler_not_english_target(args.target_lang)
        tts = AudioService.make_parler_tts(
            description=args.voice,
            parler_voice=args.parler_voice,
            gender=args.parler_gender,
            seed_path=args.parler_seed,
        )
    else:
        tts = AudioService.make_text_file_tts()
    pipeline = PlycastPipeline(translator=translator, tts=tts)
    result = pipeline.run(
        payload=PipelineInput(
            source_path=Path(args.input),
            source_language=args.source_lang,
            target_language=args.target_lang,
            max_chunk_chars=args.max_chunk_chars,
            audio_format=args.audio_format,
        ),
        output_dir=Path(args.output_dir),
    )
    print(f"Translated text: {result.translated_text_path}")
    print(f"Audio file: {result.audio_path}")


if __name__ == "__main__":
    main()
