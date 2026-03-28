from __future__ import annotations


class IdentityTranslator:
    def translate(
        self,
        text: str,
        source_language: str,
        target_language: str,
    ) -> str:
        _ = source_language, target_language
        return text
