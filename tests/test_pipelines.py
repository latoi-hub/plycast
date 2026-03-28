from pathlib import Path

from plycast.pipeline import run_read_translate
from plycast.engines.translate.providers import IdentityTranslator


def test_run_read_translate_identity(tmp_path: Path) -> None:
    src = tmp_path / "book.txt"
    src.write_text("Hello world.", encoding="utf-8")
    result = run_read_translate(
        src,
        output_dir=tmp_path,
        translator=IdentityTranslator(),
        source_language="en",
        target_language="vi",
        max_chunk_chars=500,
    )
    assert result.translated_text == "Hello world."
    assert result.translated_text_path.exists()
    assert result.translated_text_path.read_text(encoding="utf-8") == "Hello world."
