from __future__ import annotations

from pathlib import Path


class TextFileTTS:
    def synthesize(self, text: str, language: str, output_path: Path) -> Path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        text_path = output_path.with_suffix(".txt")
        text_path.write_text(
            f"[language={language}]\n\n{text}",
            encoding="utf-8",
        )
        return text_path
