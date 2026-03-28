from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
_src = ROOT_DIR / "src"
if str(_src) not in sys.path:
    sys.path.insert(0, str(_src))

from plycast.core.models import PipelineInput
from plycast.pipeline import PlycastPipeline
from plycast.engines.translate.providers import IdentityTranslator, LibreTranslateTranslator
from plycast.engines.tts.providers import (
    EspeakTTS,
    ParlerTTS,
    SystemSayTTS,
    TextFileTTS,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run plycast smoke test (identity or LibreTranslate)."
    )
    parser.add_argument(
        "--translator",
        choices=("identity", "libretranslate"),
        default="libretranslate",
        help="Translator backend for smoke test",
    )
    parser.add_argument(
        "--libretranslate-url",
        default="http://localhost:5001",
        help="LibreTranslate URL when --translator libretranslate",
    )
    parser.add_argument(
        "--libretranslate-api-key",
        default=None,
        help="Optional LibreTranslate API key",
    )
    parser.add_argument("--source-lang", default="en")
    parser.add_argument("--target-lang", default="vi")
    parser.add_argument(
        "--tts",
        choices=("text_file", "system_say", "espeak", "parler"),
        default="text_file",
        help="TTS backend for smoke test",
    )
    parser.add_argument(
        "--voice",
        default=None,
        help="Voice for system_say, espeak-ng -v, or Parler description override",
    )
    parser.add_argument(
        "--parler-voice",
        default=None,
        help="With --tts parler: seed voice name (e.g. vi, laura)",
    )
    parser.add_argument(
        "--parler-seed",
        default=None,
        help="With --tts parler: custom parler_voices.json path",
    )
    parser.add_argument(
        "--parler-gender",
        choices=("female", "male"),
        default=None,
        help="With --tts parler: female or male (omit for env / default)",
    )
    parser.add_argument(
        "--input-text",
        default=None,
        help="Override sample input text (otherwise built-in sample is used).",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    output_dir = ROOT_DIR / "dist"
    sample_input = output_dir / "smoke_input.txt"

    output_dir.mkdir(parents=True, exist_ok=True)
    default_text = (
        "Chapter 1\n\n"
        "This is a smoke test for plycast.\n\n"
        "It validates ingest, chunking, translation pipeline, and tts output."
    )
    sample_input.write_text(
        args.input_text or default_text,
        encoding="utf-8",
    )

    if args.translator == "libretranslate":
        translator = LibreTranslateTranslator(
            base_url=args.libretranslate_url,
            api_key=(
                args.libretranslate_api_key
                or os.getenv("LIBRETRANSLATE_API_KEY")
            ),
        )
    else:
        translator = IdentityTranslator()

    if args.tts == "system_say":
        tts = SystemSayTTS(voice=args.voice)
    elif args.tts == "espeak":
        tts = EspeakTTS(voice=args.voice)
    elif args.tts == "parler":
        tts = ParlerTTS(
            description=args.voice,
            parler_voice=args.parler_voice,
            gender=args.parler_gender,
            seed_path=args.parler_seed,
        )
    else:
        tts = TextFileTTS()
    pipeline = PlycastPipeline(translator=translator, tts=tts)

    result = pipeline.run(
        payload=PipelineInput(
            source_path=sample_input,
            source_language=args.source_lang,
            target_language=args.target_lang,
            max_chunk_chars=500,
        ),
        output_dir=output_dir,
    )

    print("Smoke test passed.")
    print(f"Translator: {args.translator}")
    print(f"Translated text: {result.translated_text_path}")
    print(f"Audio output: {result.audio_path}")


if __name__ == "__main__":
    main()
