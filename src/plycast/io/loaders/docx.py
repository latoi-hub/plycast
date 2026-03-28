"""Word .docx extraction."""

from __future__ import annotations

from pathlib import Path


def read_docx(path: Path) -> str:
    try:
        from docx import Document
    except ImportError as exc:
        raise ImportError(
            "Word .docx support requires: pip install python-docx"
        ) from exc
    doc = Document(str(path))
    lines = [p.text for p in doc.paragraphs if p.text.strip()]
    return "\n\n".join(lines).strip()
