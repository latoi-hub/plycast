#!/usr/bin/env python3
"""
Same workflow as the README **Python** snippet: ``synthesize_book`` with Vietnamese
and macOS **system_say** voice **Linh**.

Requires: ``pip install plycast``, **ffmpeg** on ``PATH`` for mp3. **macOS** only.
Install **Linh** under **System Settings → Accessibility → Spoken Content** if needed.
"""

from __future__ import annotations

import sys
from pathlib import Path

from plycast import synthesize_book

_HERE = Path(__file__).resolve().parent
INPUT = _HERE / "input" / "nhat-ky-nu-phap-y-c1.txt"
OUT = _HERE / "dist"


def main() -> None:
    if not INPUT.exists():
        raise SystemExit(f"Missing sample input: {INPUT}")
    if sys.platform != "darwin":
        raise SystemExit(
            "This example uses macOS system_say; run on macOS or use "
            "--tts espeak."
        )

    OUT.mkdir(parents=True, exist_ok=True)
    r = synthesize_book(
        INPUT,
        tts_language="vi",
        output_dir=OUT,
        tts="system_say",
        voice="Linh",
        audio_format="mp3",
    )
    print(r.audio_path)


if __name__ == "__main__":
    main()
