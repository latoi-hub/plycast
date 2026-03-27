from __future__ import annotations

from pathlib import Path


def read_text_file(
    path: Path,
    *,
    source_language: str | None = None,
) -> str:
    """
    Load plain text via :class:`~plycast.services.ReadTextService`
    (all supported file types).
    """
    from plycast.services.read_text import ReadTextService

    return ReadTextService().read(
        path,
        source_language=source_language,
    ).text


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
