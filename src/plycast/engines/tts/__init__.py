"""TTS protocols, providers, and :class:`AudioService`."""

from __future__ import annotations

from plycast.engines.tts.base import TTSProvider
from plycast.engines.tts.service import AudioService

__all__ = ["AudioService", "TTSProvider"]
