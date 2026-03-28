# QuickStart

Step-by-step install and usage for **plycast**. For a short overview of the project, see the [README](../README.md).

## Table of contents

- [Prerequisites](#prerequisites)
- [Installing plycast](#installing-plycast)
- [Optional: PDF and Word](#optional-pdf-and-word)
- [System software (OCR and audio)](#system-software-ocr-and-audio)
- [macOS voices (`--voice`)](Voices.md)
- [Running the CLI](#running-the-cli)
- [CLI reference (CLI.md)](CLI.md)
- [Translators](#translators)
- [Self-hosted LibreTranslate (Docker)](#self-hosted-libretranslate-docker)
- [CLI options (reference)](#cli-options-reference)
- [LLM examples](#llm-examples)
- [Python API](#python-api)
- [Environment variables](#environment-variables)
- [Smoke test script](#smoke-test-script)
- [Troubleshooting](#troubleshooting)

## Prerequisites

- **Python** 3.10 or newer
- A virtual environment is recommended (`python -m venv .venv` then `source .venv/bin/activate`)

## Installing plycast

**From PyPI:**

```bash
pip install plycast
```

Optional extras: `pip install "plycast[docs]"`, `pip install "plycast[dev]"`, etc.

**From a clone** of this repository (development or before PyPI):

```bash
python -m pip install -e .
```

The package lives under **`src/plycast/`** (src layout). Tests and editable installs use that path automatically.

Equivalent:

```bash
pip install -r requirements.txt
```

Dependencies are declared in `pyproject.toml`. Runtime Python packages include **Pillow** and **pytesseract** (for image OCR).

**Development** (tests):

```bash
python -m pip install -e ".[dev]"
python -m pytest
```

The CLI automatically loads a `.env` file in the **current working directory** if present.

## Optional: PDF and Word

```bash
python -m pip install -e ".[docs]"
```

This adds **pypdf** and **python-docx** for `.pdf` and `.docx` ingestion. Same as `pip install -e ".[full]"`.

## System software (OCR and audio)

| Need | What to install |
|------|------------------|
| **Image OCR** (`.png`, `.jpg`, …) | A **Tesseract** binary on your `PATH`. macOS: `brew install tesseract tesseract-lang` (language packs, e.g. Chinese `chi_sim`). Linux/Windows: install Tesseract from your package manager or installer. |
| **MP3 / m4a / aiff** (after WAV) | **ffmpeg** on `PATH`. macOS: `brew install ffmpeg`. Linux: `apt install ffmpeg` or equivalent. |
| **`--tts system_say`** | **macOS** `say` only. |
| **`--tts parler`** | **Parler-TTS** (neural). **English-only** for reliable speech. Install: `pip install 'plycast[parler]'`. Default on **Linux/Windows** when `parler_tts` is importable. See **[Voices.md](Voices.md)**. |
| **`--tts espeak`** | **`espeak-ng`** or **`espeak`** on `PATH` — fallback when Parler is not installed. See **[Voices.md](Voices.md)**. |
| **`--tts text_file`** | Any OS; no audio engine. |
| **Pick `--voice`** | **`system_say`**: macOS voice name. **`espeak`**: `espeak-ng --voices`. **`parler`**: optional raw description; else seed via **`--parler-voice`** + **`--parler-gender`** (or default voice from **`--target-lang`**). See **[Voices.md](Voices.md)**. |

For images, **`--source-lang`** selects the Tesseract language (e.g. `zh` → simplified Chinese).

## Running the CLI

The CLI is a **thin Typer wrapper** over the same functions as the Python API (`convert_book`, `translate_book`, …). Subcommands:

| Command | Purpose |
|---------|---------|
| **`plycast convert`** | Read → translate → audio (default path for most users) |
| **`plycast translate`** | Read → translated text file only |
| **`plycast tts`** | Read → speech (no translation) |
| **`plycast inspect`** | File metadata + text preview (debugging) |

**Full pipeline** (uses default **LibreTranslate** unless you pass `--translator identity`):

```bash
plycast convert ./book.txt \
  --source-lang en \
  --target-lang vi \
  --output-dir ./dist \
  --tts system_say
```

**JSON output** (automation):

```bash
plycast convert ./book.txt -s en -t vi -o ./dist --translator identity --tts text_file --json
```

**Module entry** (same app):

```bash
python -m plycast.cli convert ./book.txt --source-lang en --target-lang vi --output-dir ./dist
```

**Outputs**

- Translated text: `dist/<stem>.<target>.txt`
- Audio (default **mp3** with `system_say`, `espeak`, or `parler`): `dist/<stem>.<target>.mp3`

## Translators

| CLI `--translator` | Purpose |
|--------------------|---------|
| `libretranslate` | Default. Point with `--base-url` to a [LibreTranslate](https://github.com/LibreTranslate/LibreTranslate) instance. |
| `identity` | No translation (useful for testing TTS only). |
| `llm` | OpenAI or Anthropic via **`--llm-model`**; optional **`--llm-provider`** or infer from model name. Use **`--api-key`** / **`--base-url`** or env vars (see below). |

**When to use which:** `llm` tends to produce **more natural, fluent** text for listening. **LibreTranslate** is **free to self-host** and works well when you want a **machine draft to open, edit, and save** (the translated `.txt`) before running TTS again.

## Self-hosted LibreTranslate (Docker)

From the repo root:

```bash
docker compose -f docker-compose.yml up -d
```

Health check:

```bash
curl http://localhost:5001/languages
```

Example CLI against local LibreTranslate:

```bash
plycast convert ./book.txt \
  --source-lang en \
  --target-lang vi \
  --output-dir ./dist \
  --base-url http://localhost:5001 \
  --tts text_file
```

Stop:

```bash
docker compose -f docker-compose.yml down
```

Adjust `LT_LOAD_ONLY` in `docker-compose.yml` for loaded languages, then restart the container.

## CLI options (reference)

For **tables of every flag** on **`convert`**, **`translate`**, **`tts`**, and **`inspect`**, plus translators, TTS backends, and **`--json`**, see **[CLI.md](CLI.md)**.

Quick reminders for **`convert`**:

| Option | Purpose |
|--------|---------|
| `-s` / `--source-lang` | Source language |
| `-t` / `--target-lang` | Target language |
| `-o` / `--output-dir` | Output directory (default `dist`) |
| `--translator` | `identity` \| `libretranslate` \| `llm` |
| `--llm-model`, `--llm-provider` | When using `llm` |
| `--base-url`, `--api-key` | LibreTranslate or LLM |
| `--tts` | `system_say` \| `parler` \| `espeak` \| `text_file` |
| `--voice`, `--parler-voice`, `--parler-gender`, `--parler-seed` | TTS / Parler seed |
| `--max-chunk-chars`, `--audio-format` | Chunking and audio format |
| `--json` | Machine-readable result on stdout |

## LLM examples

**Provider inferred from model** (`gpt-*` → OpenAI):

```bash
OPENAI_API_KEY=your_key plycast convert ./book.txt \
  --output-dir ./dist \
  --source-lang en \
  --target-lang vi \
  --translator llm \
  --llm-model gpt-4o-mini \
  --tts text_file
```

**Explicit Anthropic:**

```bash
ANTHROPIC_API_KEY=your_key plycast convert ./book.txt \
  --output-dir ./dist \
  --source-lang en \
  --target-lang vi \
  --translator llm \
  --llm-provider anthropic \
  --llm-model claude-3-5-haiku-latest \
  --tts text_file
```

**Chinese → Vietnamese** (LLM + macOS `say`, Vietnamese voice):

```bash
OPENAI_API_KEY=your_key plycast convert ./book.txt \
  --output-dir dist \
  --source-lang zh \
  --target-lang vi \
  --translator llm \
  --llm-model gpt-4o-mini \
  --tts system_say \
  --voice "Linh"
```

If `OPENAI_API_KEY` is already exported, omit the prefix; you can pass **`--api-key`** instead.

## Python API

**One-shot workflow (matches `plycast convert`):**

```python
from pathlib import Path

from plycast import convert_book

result = convert_book(
    Path("book.txt"),
    source_lang="en",
    target_lang="vi",
    output_dir=Path("dist"),
    translator="identity",
    tts="text_file",
)

print(result.translated_text_path, result.audio_path)
```

**Composable pipeline (custom providers):**

```python
from pathlib import Path

from plycast import PlycastPipeline
from plycast.core.models import PipelineInput
from plycast.engines.translate.providers import LibreTranslateTranslator
from plycast.engines.tts.providers import SystemSayTTS

pipeline = PlycastPipeline(
    translator=LibreTranslateTranslator(base_url="https://libretranslate.com"),
    tts=SystemSayTTS(voice="Samantha"),
)

result = pipeline.run(
    payload=PipelineInput(
        source_path=Path("book.txt"),
        source_language="en",
        target_language="vi",
        max_chunk_chars=1500,
        audio_format="mp3",
    ),
    output_dir=Path("dist"),
)

print(result.translated_text_path)
print(result.audio_path)
```

**Pipeline functions without `PlycastPipeline`:**

```python
from pathlib import Path
from plycast.pipeline import run_read_translate
from plycast.engines.translate.providers import IdentityTranslator

run_read_translate(
    Path("book.txt"),
    output_dir=Path("dist"),
    translator=IdentityTranslator(),
    source_language="en",
    target_language="vi",
    max_chunk_chars=1500,
)
```

**Custom adapters:** implement `plycast.engines.translate.base.TranslatorProvider` and `plycast.engines.tts.base.TTSProvider`. Concrete translators live under `plycast.engines.translate.providers`; TTS engines under `plycast.engines.tts.providers`.

## Environment variables

| Variable | Used for |
|----------|----------|
| `OPENAI_API_KEY` | OpenAI / `llm` when routed to OpenAI |
| `ANTHROPIC_API_KEY` | Anthropic / `llm` when routed to Anthropic |
| `LIBRETRANSLATE_API_KEY` | LibreTranslate |

Legacy dotted names (`openai-api-key`, etc.) are still read by the CLI for compatibility.

## Smoke test script

```bash
python scripts/smoke_test.py
```

With local LibreTranslate:

```bash
python scripts/smoke_test.py \
  --translator libretranslate \
  --libretranslate-url http://localhost:5001
```

Supported smoke translators: `identity`, `libretranslate`.

## Troubleshooting

- **`system_say` spells characters:** choose a `--voice` that matches the target language, and avoid mixing scripts (e.g. Chinese + Latin) in one paragraph when possible.
- **MP3 output:** `system_say` writes AIFF first; **ffmpeg** converts. Install ffmpeg if conversion fails. Same for **`espeak`** and **`parler`** (WAV → mp3/m4a) when not using **`--audio-format wav`**.
- **Parler import / CUDA:** install with `pip install 'plycast[parler]'`. First run downloads model weights. Use **`PLYCAST_PARLER_DEVICE=cpu`** if GPU drivers are broken.
- **Parler + non-English `--target-lang`:** Parler is **English-only** for good results; use **`--target-lang en`** or another **`--tts`** backend. The CLI warns on stderr when Parler is used with a non-English target language.
- **Unknown Parler voice:** use a name from the packaged seed (see **[Voices.md](Voices.md)**) or **`--parler-seed`** / **`PLYCAST_PARLER_SEED`** for your own JSON.
- **`No module named 'PIL'`:** reinstall with `pip install -e .` so Pillow is installed.
- **`tesseract` not found:** install Tesseract and ensure it is on `PATH`, or install via Homebrew (`brew install tesseract tesseract-lang`). The library also checks common Homebrew paths on macOS.
