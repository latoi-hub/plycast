"""Speech synthesis via espeak-ng / espeak (Linux; optional on macOS/Windows)."""

from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

from plycast.engines.audio.encode import convert_audio


def _find_espeak() -> str | None:
    return shutil.which("espeak-ng") or shutil.which("espeak")


def _default_voice_for_language(language: str) -> str:
    """Map ISO-ish codes to espeak-ng ``-v`` (see ``espeak-ng --voices``)."""
    s = language.strip().lower().replace("_", "-")
    if s.startswith("zh"):
        return "cmn"
    if "hant" in s or s.startswith("zh-tw") or s.startswith("zh-hk"):
        return "yue"
    base = s.split("-")[0]
    return base if len(base) >= 2 else "en"


class EspeakTTS:
    """
    ``espeak-ng`` (preferred) or ``espeak`` writes WAV, then
    :func:`~plycast.engines.audio.encode.convert_audio` for mp3/m4a/aiff.
    """

    def __init__(self, voice: str | None = None) -> None:
        self.voice = voice

    def synthesize(self, text: str, language: str, output_path: Path) -> Path:
        exe = _find_espeak()
        if not exe:
            raise RuntimeError(
                "espeak-ng (or espeak) not found on PATH. "
                "Install: Debian/Ubuntu `sudo apt install espeak-ng`, "
                "Fedora `dnf install espeak-ng`, macOS `brew install espeak-ng`. "
                "Or use --tts text_file / (macOS) --tts system_say."
            )
        output_path.parent.mkdir(parents=True, exist_ok=True)
        v = self.voice if self.voice else _default_voice_for_language(language)

        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            delete=False,
            suffix=".txt",
        ) as f:
            f.write(text)
            text_file = f.name

        wav_path = (
            output_path
            if output_path.suffix.lower() == ".wav"
            else output_path.with_suffix(".wav")
        )
        try:
            cmd = [exe, "-v", v, "-w", str(wav_path), "-f", text_file]
            subprocess.run(cmd, check=True)
        finally:
            Path(text_file).unlink(missing_ok=True)

        if wav_path.resolve() == output_path.resolve():
            return output_path
        try:
            return convert_audio(wav_path, output_path)
        finally:
            if wav_path.exists() and wav_path != output_path:
                wav_path.unlink(missing_ok=True)
