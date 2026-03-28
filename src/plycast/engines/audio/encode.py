from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


def convert_audio(source_path: Path, output_path: Path) -> Path:
    source_ext = source_path.suffix.lower()
    target_ext = output_path.suffix.lower()

    if source_ext == target_ext:
        if source_path != output_path:
            output_path.write_bytes(source_path.read_bytes())
        return output_path

    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise RuntimeError(
            f"Requested {target_ext} output, but ffmpeg is not installed. "
            f"Install it (brew install ffmpeg) or output {source_ext}."
        )

    if target_ext == ".mp3":
        cmd = [
            ffmpeg,
            "-y",
            "-i",
            str(source_path),
            "-codec:a",
            "libmp3lame",
            "-q:a",
            "2",
            str(output_path),
        ]
    elif target_ext == ".wav":
        cmd = [
            ffmpeg,
            "-y",
            "-i",
            str(source_path),
            "-codec:a",
            "pcm_s16le",
            str(output_path),
        ]
    elif target_ext == ".m4a":
        cmd = [
            ffmpeg,
            "-y",
            "-i",
            str(source_path),
            "-codec:a",
            "aac",
            "-b:a",
            "192k",
            str(output_path),
        ]
    elif target_ext == ".aiff":
        cmd = [
            ffmpeg,
            "-y",
            "-i",
            str(source_path),
            str(output_path),
        ]
    else:
        raise ValueError(f"Unsupported audio format: {target_ext}")

    subprocess.run(cmd, check=True)
    return output_path
