#!/usr/bin/env python3
"""
Same workflow as a **Python** one-off: ``convert_book`` (vi → en, LLM, Parler **laura**).

Requires: ``pip install 'plycast[parler]'``, ``ffmpeg``, ``OPENAI_API_KEY``. **Parler** is
English-centric; ``target_lang=en`` matches the translated text.
"""

from __future__ import annotations

import os
from pathlib import Path

from plycast import convert_book

_HERE = Path(__file__).resolve().parent
INPUT = _HERE / "input" / "nhat-ky-nu-phap-y-c1.txt"
OUT = _HERE / "dist"


def main() -> None:
    if not INPUT.exists():
        raise SystemExit(f"Missing sample input: {INPUT}")
    if not os.environ.get("OPENAI_API_KEY"):
        raise SystemExit(
            "Set OPENAI_API_KEY for LLM translation, or edit this script to use "
            "translator='libretranslate' with a running LibreTranslate "
            "server."
        )

    OUT.mkdir(parents=True, exist_ok=True)
    r = convert_book(
        INPUT,
        source_lang="vi",
        target_lang="en",
        output_dir=OUT,
        translator="llm",
        llm_model="gpt-4o-mini",
        tts="parler",
        parler_voice="laura",
        parler_gender="female",
        audio_format="mp3",
    )
    print(r.translated_text_path)
    print(r.audio_path)


if __name__ == "__main__":
    main()
