"""Data models for pipelines and service results."""

from .pipeline import PipelineInput, PipelineOutput
from .results import (
    ReadAudioOnlyResult,
    ReadTextResult,
    TranslateOnlyResult,
)

__all__ = [
    "PipelineInput",
    "PipelineOutput",
    "ReadAudioOnlyResult",
    "ReadTextResult",
    "TranslateOnlyResult",
]
