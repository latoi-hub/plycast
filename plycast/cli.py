from __future__ import annotations

import argparse
import os
from pathlib import Path

from .models import PipelineInput
from .pipeline import PlycastPipeline
from .providers import (
    AnthropicTranslator,
    IdentityTranslator,
    LibreTranslateTranslator,
    OpenAITranslator,
    SystemSayTTS,
    TextFileTTS,
)


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
    parser.add_argument("--input", required=True, help="Input .txt or .md path")
    parser.add_argument("--output-dir", default="dist", help="Output directory")
    parser.add_argument("--source-lang", required=True, help="Source language code")
    parser.add_argument("--target-lang", required=True, help="Target language code")
    parser.add_argument(
        "--translator",
        choices=("identity", "libretranslate", "openai", "anthropic"),
        default="libretranslate",
        help="Translator backend",
    )
    parser.add_argument(
        "--libretranslate-url",
        default="https://libretranslate.com",
        help="Base URL for LibreTranslate backend",
    )
    parser.add_argument("--libretranslate-api-key", default=None)
    parser.add_argument("--openai-api-key", default=None)
    parser.add_argument("--openai-model", default="gpt-4o-mini")
    parser.add_argument("--openai-base-url", default="https://api.openai.com/v1")
    parser.add_argument("--anthropic-api-key", default=None)
    parser.add_argument("--anthropic-model", default="claude-3-5-haiku-latest")
    parser.add_argument(
        "--anthropic-base-url",
        default="https://api.anthropic.com/v1",
    )
    parser.add_argument(
        "--tts",
        choices=("system_say", "text_file"),
        default="system_say",
    )
    parser.add_argument(
        "--voice",
        default=None,
        help="Voice name for system_say",
    )
    parser.add_argument("--max-chunk-chars", type=int, default=1500)
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
        translator = LibreTranslateTranslator(
            base_url=args.libretranslate_url,
            api_key=(
                args.libretranslate_api_key
                or _get_env("LIBRETRANSLATE_API_KEY", "libretranslate-api-key")
            ),
        )
    elif args.translator == "openai":
        key = args.openai_api_key or _get_env("OPENAI_API_KEY", "openai-api-key")
        if not key:
            raise ValueError("Missing OpenAI key.")
        translator = OpenAITranslator(
            api_key=key,
            model=args.openai_model,
            base_url=args.openai_base_url,
        )
    elif args.translator == "anthropic":
        key = args.anthropic_api_key or _get_env(
            "ANTHROPIC_API_KEY",
            "anthropic-api-key",
        )
        if not key:
            raise ValueError("Missing Anthropic key.")
        translator = AnthropicTranslator(
            api_key=key,
            model=args.anthropic_model,
            base_url=args.anthropic_base_url,
        )
    else:
        translator = IdentityTranslator()

    tts = (
        SystemSayTTS(voice=args.voice)
        if args.tts == "system_say"
        else TextFileTTS()
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
