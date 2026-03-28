"""Chunking for Parler TTS (no model load)."""

from plycast.engines.tts.providers.parler import _split_tts_chunks


def test_split_respects_max_chars() -> None:
    text = "A" * 100 + "\n\n" + "B" * 50
    chunks = _split_tts_chunks(text, max_chars=40)
    assert all(len(c) <= 40 for c in chunks)
    assert "".join(chunks).replace("\n", "") == "A" * 100 + "B" * 50


def test_split_preserves_short_paragraph() -> None:
    chunks = _split_tts_chunks("One paragraph.\n\nAnother.", max_chars=500)
    assert chunks == ["One paragraph.", "Another."]
