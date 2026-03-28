#!/usr/bin/env python3
"""Minimal ``convert_book`` example (same workflow as ``plycast convert``)."""

from pathlib import Path

from plycast import convert_book

if __name__ == "__main__":
    repo = Path(__file__).resolve().parents[1]
    inp = repo / "data" / "input" / "c2.txt"
    if not inp.exists():
        inp = Path("book.txt")
    r = convert_book(
        inp,
        source_lang="en",
        target_lang="en",
        output_dir=repo / "dist",
        translator="identity",
        tts="text_file",
    )
    print(r.translated_text_path)
    print(r.audio_path)
