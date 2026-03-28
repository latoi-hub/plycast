"""Split long text into translation-sized chunks."""

from __future__ import annotations


def chunk_text(text: str, max_chunk_chars: int) -> list[str]:
    if max_chunk_chars <= 0:
        raise ValueError("max_chunk_chars must be > 0")

    chunks: list[str] = []
    for paragraph in text.split("\n\n"):
        if len(paragraph) <= max_chunk_chars:
            chunks.append(paragraph)
            continue
        start = 0
        while start < len(paragraph):
            end = start + max_chunk_chars
            chunks.append(paragraph[start:end])
            start = end

    return chunks
