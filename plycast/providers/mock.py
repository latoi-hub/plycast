from __future__ import annotations

import subprocess
import shutil
import tempfile
from pathlib import Path


class IdentityTranslator:
    def translate(
        self,
        text: str,
        source_language: str,
        target_language: str,
    ) -> str:
        _ = source_language, target_language
        return text


class TextFileTTS:
    def synthesize(self, text: str, language: str, output_path: Path) -> Path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        text_path = output_path.with_suffix(".txt")
        text_path.write_text(
            f"[language={language}]\n\n{text}",
            encoding="utf-8",
        )
        return text_path


class SystemSayTTS:
    def __init__(self, voice: str | None = None) -> None:
        self.voice = voice

    def synthesize(self, text: str, language: str, output_path: Path) -> Path:
        _ = language
        output_path.parent.mkdir(parents=True, exist_ok=True)
        target_suffix = output_path.suffix.lower()
        say_out = (
            output_path
            if target_suffix == ".aiff"
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

        ffmpeg = shutil.which("ffmpeg")
        if not ffmpeg:
            raise RuntimeError(
                f"Requested {output_path.suffix} output, but ffmpeg is not installed. "
                f"Install it (brew install ffmpeg) or use --audio-format aiff."
            )

        out_parent = output_path.parent
        out_parent.mkdir(parents=True, exist_ok=True)

        if target_suffix == ".mp3":
            cmd = [
                ffmpeg,
                "-y",
                "-i",
                str(say_out),
                "-codec:a",
                "libmp3lame",
                "-q:a",
                "2",
                str(output_path),
            ]
        elif target_suffix == ".wav":
            cmd = [
                ffmpeg,
                "-y",
                "-i",
                str(say_out),
                "-codec:a",
                "pcm_s16le",
                str(output_path),
            ]
        elif target_suffix == ".m4a":
            cmd = [
                ffmpeg,
                "-y",
                "-i",
                str(say_out),
                "-codec:a",
                "aac",
                "-b:a",
                "192k",
                str(output_path),
            ]
        else:
            raise ValueError(f"Unsupported audio format: {output_path.suffix}")

        subprocess.run(cmd, check=True)
        return output_path
