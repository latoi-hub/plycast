# Examples (Vietnamese sources)

Sample text: **[`input/nhat-ky-nu-phap-y-c1.txt`](input/nhat-ky-nu-phap-y-c1.txt)** (Vietnamese fiction excerpt).

Run commands from the **repository root** (`latoi-hub/plycast/`). Install the package first (`pip install -e .` or `pip install plycast`).

---

## 1 — Translate to English + Parler TTS (voice **laura**)

Full pipeline: **vi → en** with an LLM, then **Parler** using seed voice **laura** (female).

**Needs:** `pip install 'plycast[parler]'`, **ffmpeg** on `PATH` for mp3, **`OPENAI_API_KEY`**, GPU/CPU patience for Parler.

### CLI

```bash
export OPENAI_API_KEY=sk-...
plycast convert examples/input/nhat-ky-nu-phap-y-c1.txt \
  --source-lang vi \
  --target-lang en \
  --output-dir dist/examples \
  --translator llm \
  --llm-model gpt-4o-mini \
  --tts parler \
  --parler-voice laura \
  --parler-gender female \
  --audio-format mp3
```

### Python

After `pip install 'plycast[parler]'`, from the **repo root** (so paths match):

```python
import os
from pathlib import Path
from plycast import convert_book

assert os.environ.get("OPENAI_API_KEY")

r = convert_book(
    Path("examples/input/nhat-ky-nu-phap-y-c1.txt"),
    source_lang="vi",
    target_lang="en",
    output_dir=Path("dist/examples"),
    translator="llm",
    llm_model="gpt-4o-mini",
    tts="parler",
    parler_voice="laura",
    parler_gender="female",
    audio_format="mp3",
)
print(r.translated_text_path, r.audio_path)
```

Optional: run the same logic via **`python examples/vi_to_en_parler_laura.py`** (writes under **`examples/dist/`**).

---

## 2 — Vietnamese audio only (macOS **system_say**, voice **Linh**)

Read the Vietnamese file and speak it with voice **Linh** (no translation).

**Needs:** **macOS**, **Linh** available in **System Settings → Accessibility → Spoken Content** (add **Vietnamese** voices if needed), **ffmpeg** for mp3.

### CLI

```bash
plycast tts examples/input/nhat-ky-nu-phap-y-c1.txt \
  --lang vi \
  --tts system_say \
  --voice Linh \
  --output-dir examples/dist \
  --audio-format mp3
```

### Python

After `pip install plycast`:

```python
from pathlib import Path
from plycast import synthesize_book

r = synthesize_book(
    Path("examples/input/nhat-ky-nu-phap-y-c1.txt"),
    tts_language="vi",
    output_dir=Path("examples/dist"),
    tts="system_say",
    voice="Linh",
    audio_format="mp3",
)
print(r.audio_path)
```

Optional: **`python examples/vi_tts_system_say_linh.py`** (same calls; writes under **`examples/dist/`**).
