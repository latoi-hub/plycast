"""Translation protocols, providers, and :class:`TranslateService`."""

from __future__ import annotations

from plycast.engines.translate.base import TranslatorProvider
from plycast.engines.translate.service import TranslateService

__all__ = ["TranslateService", "TranslatorProvider"]
