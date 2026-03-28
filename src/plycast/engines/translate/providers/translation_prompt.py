from __future__ import annotations


def translation_prompt(
    text: str,
    source_language: str,
    target_language: str,
) -> str:
    return (
        "Translate the following text.\n"
        f"Source language: {source_language}\n"
        f"Target language: {target_language}\n\n"
        "Rules:\n"
        "- Preserve meaning, tone, and paragraph structure.\n"
        "- Do not summarize.\n"
        "- Return translated text only.\n\n"
        f"Text:\n{text}"
    )
