from plycast.providers.llm import infer_llm_provider


def test_infer_openai_models() -> None:
    assert infer_llm_provider("gpt-4o-mini") == "openai"
    assert infer_llm_provider("o3-mini") == "openai"


def test_infer_anthropic_models() -> None:
    assert infer_llm_provider("claude-3-5-haiku-latest") == "anthropic"
