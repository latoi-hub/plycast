from __future__ import annotations

import argparse
import os
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
        choices=("system_say", "text_file"),
        default="system_say",
        help="system_say: macOS speech (default); text_file: write text artifact instead of audio",
    )
    parser.add_argument(
        "--voice",
        default=None,
        help="Voice name for system_say",
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
        help="Audio output format (system_say converts when needed)",
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

    tts = (
        AudioService.make_system_say_tts(voice=args.voice)
        if args.tts == "system_say"
        else AudioService.make_text_file_tts()
    )
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
