from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path

from .convert import convert_audio


class SystemSayTTS:
    def __init__(self, voice: str | None = None) -> None:
        self.voice = voice

    def synthesize(self, text: str, language: str, output_path: Path) -> Path:
        _ = language
        output_path.parent.mkdir(parents=True, exist_ok=True)
        say_out = (
            output_path
            if output_path.suffix.lower() == ".aiff"
            else output_path.with_suffix(".aiff")
        )

        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            delete=False,
        ) as f:
            f.write(text)
            text_file = f.name

        try:
            command = ["say", "-o", str(say_out), "-f", text_file]
            if self.voice:
                command.extend(["-v", self.voice])
            subprocess.run(command, check=True)
        finally:
            try:
                Path(text_file).unlink(missing_ok=True)
            except Exception:
                pass

        if say_out == output_path:
            return output_path
        return convert_audio(say_out, output_path)
