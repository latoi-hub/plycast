import pytest

from plycast.engines.tts.providers.parler import ParlerTTS
from plycast.engines.tts.providers.parler_voices import (
    normalize_parler_language,
    parler_preset_description,
    parler_seed_voice_names,
    parler_voice_description,
    reload_parler_voice_seed_cache,
)


def test_seed_voice_names_include_languages_and_personas() -> None:
    names = parler_seed_voice_names()
    assert "en" in names and "vi" in names
    assert "laura" in names and "jon" in names
    assert len(names) >= 10


def test_normalize_zh_and_pt_variants() -> None:
    assert normalize_parler_language("zh-TW") == "zh"
    assert normalize_parler_language("pt-BR") == "pt"


def test_unknown_lang_falls_back_to_en_voice_name() -> None:
    assert normalize_parler_language("xx") == "en"
    f = parler_preset_description("xx", "female")
    m = parler_preset_description("xx", "male")
    assert "female narrator" in f.lower()
    assert "male narrator" in m.lower()


def test_vi_gender_variants_differ() -> None:
    f = parler_voice_description("vi", "female")
    m = parler_voice_description("vi", "male")
    assert "female narrator" in f.lower()
    assert "male narrator" in m.lower()


def test_parler_voice_jon_male() -> None:
    d = parler_voice_description("jon", "male")
    assert "jon" in d.lower()


def test_unknown_voice_raises() -> None:
    with pytest.raises(ValueError, match="Unknown Parler voice"):
        parler_voice_description("not_a_defined_voice_xyz", "female")


def test_parler_tts_resolve_description_override() -> None:
    t = ParlerTTS(description="Only this prompt", gender="female")
    assert t._resolve_description("en") == "Only this prompt"


def test_parler_tts_resolve_from_seed_by_target_lang() -> None:
    t = ParlerTTS(description=None, parler_voice=None, gender="male")
    d = t._resolve_description("vi")
    assert "male narrator" in d.lower()
    assert "vietnamese" in d.lower()


def test_parler_tts_resolve_named_voice() -> None:
    t = ParlerTTS(description=None, parler_voice="jon", gender="male")
    d = t._resolve_description("en")
    assert "jon" in d.lower()


def test_custom_seed_file(tmp_path) -> None:
    seed = tmp_path / "voices.json"
    seed.write_text(
        '{"version": 1, "default_voice": "a", '
        '"voices": {"a": {"female": "F custom", "male": "M custom"}}}',
        encoding="utf-8",
    )
    reload_parler_voice_seed_cache()
    try:
        assert parler_voice_description("a", "female", seed_path=seed) == "F custom"
        assert parler_voice_description("A", "male", seed_path=seed) == "M custom"
    finally:
        reload_parler_voice_seed_cache()
