"""Neural TTS via Hugging Face Parler-TTS (GPU/MPS/CPU; chunked long text)."""

from __future__ import annotations

import os
import re
import threading
from pathlib import Path
from typing import Any

from .convert import convert_audio

_DEFAULT_MODEL = "parler-tts/parler-tts-mini-v1"
_cache_lock = threading.Lock()
_model_cache: dict[tuple[str, str, str], tuple[Any, Any, int]] = {}


def _auto_device() -> str:
    import torch

    if torch.cuda.is_available():
        return "cuda:0"
    if getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
        return "mps"
    return "cpu"


def _pick_dtype(device: str) -> Any:
    import torch

    if device.startswith("cuda") and torch.cuda.is_bf16_supported():
        return torch.bfloat16
    return torch.float32


def _split_tts_chunks(text: str, max_chars: int) -> list[str]:
    if max_chars <= 0:
        raise ValueError("max_chunk_chars must be > 0")
    chunks: list[str] = []
    for para in text.split("\n\n"):
        p = para.strip()
        if not p:
            continue
        if len(p) <= max_chars:
            chunks.append(p)
            continue
        sentences = re.split(r"(?<=[.!?…])\s+", p)
        buf = ""
        for s in sentences:
            s = s.strip()
            if not s:
                continue
            candidate = f"{buf} {s}".strip() if buf else s
            if len(candidate) <= max_chars:
                buf = candidate
            else:
                if buf:
                    chunks.append(buf)
                    buf = ""
                if len(s) <= max_chars:
                    buf = s
                else:
                    start = 0
                    while start < len(s):
                        chunks.append(s[start : start + max_chars])
                        start += max_chars
        if buf:
            chunks.append(buf)
    return [c for c in chunks if c.strip()]


def _get_sampling_rate(model: Any) -> int:
    cfg = getattr(model, "config", None)
    if cfg is not None:
        sr = getattr(cfg, "sampling_rate", None)
        if sr is not None:
            return int(sr)
    enc = getattr(model, "audio_encoder", None)
    if enc is not None and getattr(enc, "config", None) is not None:
        sr = getattr(enc.config, "sampling_rate", None)
        if sr is not None:
            return int(sr)
    return 44100


def _load_cached(model_name: str, device: str) -> tuple[Any, Any, int]:
    import torch
    from parler_tts import ParlerTTSForConditionalGeneration
    from transformers import AutoTokenizer

    dtype = _pick_dtype(device)
    key = (model_name, device, str(dtype))
    with _cache_lock:
        hit = _model_cache.get(key)
        if hit is not None:
            return hit
        tok = AutoTokenizer.from_pretrained(model_name)
        m = ParlerTTSForConditionalGeneration.from_pretrained(model_name)
        m = m.to(device, dtype=dtype)
        m.eval()
        sr = _get_sampling_rate(m)
        _model_cache[key] = (m, tok, sr)
        return m, tok, sr


def _synthesize_chunk(
    model: Any,
    tokenizer: Any,
    device: str,
    description: str,
    text: str,
) -> Any:
    import torch

    desc_t = tokenizer(description, return_tensors="pt")
    prompt_t = tokenizer(text, return_tensors="pt")
    input_ids = desc_t.input_ids.to(device)
    prompt_input_ids = prompt_t.input_ids.to(device)
    attn = desc_t.attention_mask.to(device) if hasattr(desc_t, "attention_mask") else None
    prompt_attn = (
        prompt_t.attention_mask.to(device) if hasattr(prompt_t, "attention_mask") else None
    )
    kwargs: dict[str, Any] = {
        "input_ids": input_ids,
        "prompt_input_ids": prompt_input_ids,
    }
    if attn is not None:
        kwargs["attention_mask"] = attn
    if prompt_attn is not None:
        kwargs["prompt_attention_mask"] = prompt_attn

    with torch.inference_mode():
        generation = model.generate(**kwargs)
    arr = generation.detach().float().cpu().squeeze()
    if arr.dim() > 1:
        arr = arr.reshape(-1)
    return arr.contiguous()


class ParlerTTS:
    """
    Parler-TTS: natural neural speech (English-centric; reliable quality for **English** text
    only). Requires ``pip install 'plycast[parler]'`` (or equivalent torch/transformers/parler-tts).

    **Voice selection (most specific wins):**

    1. Constructor ``description=`` (CLI ``--voice`` with ``--tts parler``): full custom prompt.
    2. Env ``PLYCAST_PARLER_DESCRIPTION``: custom prompt without CLI.
    3. Else: JSON seed (packaged or ``PLYCAST_PARLER_SEED`` / ``seed_path=``) via
       ``parler_voice`` (CLI ``--parler-voice``) and ``gender``. If ``parler_voice`` is
       omitted, the voice name defaults from ``normalize_parler_language(language)`` using
       ``--target-lang`` at synthesize time.

    Env: ``PLYCAST_PARLER_MODEL``, ``PLYCAST_PARLER_DEVICE``, ``PLYCAST_PARLER_GENDER``,
    ``PLYCAST_PARLER_VOICE``, ``PLYCAST_PARLER_SEED``.
    Long text is chunked, synthesized, concatenated, then converted via ffmpeg when needed.
    """

    def __init__(
        self,
        *,
        model_name: str | None = None,
        device: str | None = None,
        description: str | None = None,
        parler_voice: str | None = None,
        gender: str | None = None,
        seed_path: str | Path | None = None,
        max_chunk_chars: int = 450,
    ) -> None:
        self.model_name = model_name or os.environ.get(
            "PLYCAST_PARLER_MODEL", _DEFAULT_MODEL
        )
        self.device = device or os.environ.get("PLYCAST_PARLER_DEVICE") or _auto_device()
        # Explicit override only; seed resolved in ``_resolve_description``.
        self._description_override = (
            description.strip() if description and description.strip() else None
        )
        pv = parler_voice or os.environ.get("PLYCAST_PARLER_VOICE")
        self._parler_voice = pv.strip() if pv and str(pv).strip() else None
        sp = seed_path or os.environ.get("PLYCAST_PARLER_SEED")
        self._seed_path: Path | None
        if sp and str(sp).strip():
            self._seed_path = Path(str(sp).strip()).expanduser()
        else:
            self._seed_path = None
        g = (gender or os.environ.get("PLYCAST_PARLER_GENDER") or "female").strip().lower()
        self._gender = "male" if g == "male" else "female"
        self.max_chunk_chars = max_chunk_chars

    def _resolve_description(self, language: str) -> str:
        if self._description_override:
            return self._description_override
        env_desc = os.environ.get("PLYCAST_PARLER_DESCRIPTION")
        if env_desc and env_desc.strip():
            return env_desc.strip()
        from .parler_voices import normalize_parler_language, parler_voice_description

        voice_key = self._parler_voice or normalize_parler_language(language)
        return parler_voice_description(
            voice_key,
            self._gender,
            seed_path=self._seed_path,
        )

    def synthesize(self, text: str, language: str, output_path: Path) -> Path:
        description = self._resolve_description(language)
        try:
            import soundfile as sf
        except ImportError as e:
            raise RuntimeError(
                "Parler TTS requires the 'soundfile' package. "
                "Install with: pip install 'plycast[parler]'"
            ) from e
        try:
            model, tokenizer, sampling_rate = _load_cached(
                self.model_name, self.device
            )
        except ImportError as e:
            raise RuntimeError(
                "Parler TTS requires torch, transformers, and parler-tts. "
                "Install with: pip install 'plycast[parler]'"
            ) from e

        stripped = text.strip()
        if not stripped:
            raise ValueError("Cannot synthesize empty text.")

        output_path.parent.mkdir(parents=True, exist_ok=True)
        chunks = _split_tts_chunks(stripped, self.max_chunk_chars)
        import torch

        wave_parts: list[Any] = []
        for part in chunks:
            wave_parts.append(
                _synthesize_chunk(
                    model,
                    tokenizer,
                    self.device,
                    description,
                    part,
                )
            )
        audio = (
            torch.cat(wave_parts, dim=0).cpu().numpy()
            if len(wave_parts) > 1
            else wave_parts[0].cpu().numpy()
        )

        wav_path = (
            output_path
            if output_path.suffix.lower() == ".wav"
            else output_path.with_suffix(".wav")
        )
        sf.write(str(wav_path), audio, sampling_rate)

        if wav_path.resolve() == output_path.resolve():
            return output_path
        try:
            return convert_audio(wav_path, output_path)
        finally:
            if wav_path.exists() and wav_path != output_path:
                wav_path.unlink(missing_ok=True)
