from plycast.preprocess.chunking import chunk_text


def test_chunk_preserves_short_paragraphs() -> None:
    text = "Hello.\n\nWorld."
    assert chunk_text(text, 500) == ["Hello.", "World."]


def test_chunk_splits_long_paragraph() -> None:
    text = "a" * 100
    chunks = chunk_text(text, 30)
    assert len(chunks) >= 2
    assert "".join(chunks) == text
