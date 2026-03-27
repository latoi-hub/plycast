# QuickStart

Step-by-step install and usage for **plycast**. For a short overview of the project, see the [README](../README.md).

## Table of contents

- [Prerequisites](#prerequisites)
- [Installing plycast](#installing-plycast)
- [Optional: PDF and Word](#optional-pdf-and-word)
- [System software (OCR and audio)](#system-software-ocr-and-audio)
- [Running the CLI](#running-the-cli)
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
| **Image OCR** (`.png`, `.jpg`, …) | A **Tesseract** binary on your `PATH`. macOS: `brew install tesseract tesseract-lang` (language packs, e.g. Chinese `chi_sim`). |
| **MP3 / m4a / wav** from `system_say` | **ffmpeg** on `PATH`. macOS: `brew install ffmpeg`. |
| **macOS speech** | Built-in `say`; pick `--voice` to match the target language. |

For images, **`--source-lang`** selects the Tesseract language (e.g. `zh` → simplified Chinese).

## Running the CLI

Minimal example (uses default **LibreTranslate** public API; set `--base-url` to your own server if needed):

```bash
python -m plycast.cli \
  --input ./book.txt \
  --output-dir ./dist \
  --source-lang en \
  --target-lang vi \
  --tts system_say
```

Console script (same entry point):

```bash
plycast --input ./book.txt --output-dir ./dist --source-lang en --target-lang vi --tts system_say
```

**Outputs**

- Translated text: `dist/<stem>.<target>.txt`
- Audio (default **mp3** with `system_say`): `dist/<stem>.<target>.mp3`

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
python -m plycast.cli \
  --input ./book.txt \
  --output-dir ./dist \
  --source-lang en \
  --target-lang vi \
  --base-url http://localhost:5001 \
  --tts text_file
```

Stop:

```bash
docker compose -f docker-compose.yml down
```

Adjust `LT_LOAD_ONLY` in `docker-compose.yml` for loaded languages, then restart the container.

## CLI options (reference)

| Option | Purpose |
|--------|---------|
| `--translator identity\|libretranslate\|llm` | Backend |
| `--translator llm` | OpenAI or Anthropic via `--llm-model` and optional `--llm-provider` |
| `--llm-model` | Model id (default `gpt-4o-mini` when using `llm`) |
| `--llm-provider openai\|anthropic` | Force vendor; omit to infer from model name |
| `--base-url` | LibreTranslate server URL, or LLM API base (defaults if omitted) |
| `--api-key` | Optional LibreTranslate key; required for `llm` unless set in env |
| `--tts text_file` | No audio; writes a text artifact |
| `--voice` | macOS `say` voice |
| `--max-chunk-chars` | Translation chunk size |
| `--audio-format mp3\|aiff\|wav\|m4a` | Audio output |

Run **`plycast --help`** for the full list.

## LLM examples

**Provider inferred from model** (`gpt-*` → OpenAI):

```bash
OPENAI_API_KEY=your_key python -m plycast.cli \
  --input ./book.txt \
  --output-dir ./dist \
  --source-lang en \
  --target-lang vi \
  --translator llm \
  --llm-model gpt-4o-mini \
  --tts text_file
```

**Explicit Anthropic:**

```bash
ANTHROPIC_API_KEY=your_key python -m plycast.cli \
  --input ./book.txt \
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
OPENAI_API_KEY=your_key python -m plycast.cli \
  --input ./book.txt \
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

**High-level pipeline:**

```python
from pathlib import Path

from plycast.models import PipelineInput
from plycast.pipeline import PlycastPipeline
from plycast.providers import LibreTranslateTranslator, SystemSayTTS

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
from plycast.pipelines import run_read_translate
from plycast.providers import IdentityTranslator

run_read_translate(
    Path("book.txt"),
    output_dir=Path("dist"),
    translator=IdentityTranslator(),
    source_language="en",
    target_language="vi",
    max_chunk_chars=1500,
)
```

**Custom adapters:** implement `plycast.providers.TranslatorProvider` and `plycast.providers.TTSProvider`. Vendor HTTP clients live under `plycast.providers.<vendor>`.

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
- **MP3 output:** `system_say` writes AIFF first; **ffmpeg** converts. Install ffmpeg if conversion fails.
- **`No module named 'PIL'`:** reinstall with `pip install -e .` so Pillow is installed.
- **`tesseract` not found:** install Tesseract and ensure it is on `PATH`, or install via Homebrew (`brew install tesseract tesseract-lang`). The library also checks common Homebrew paths on macOS.
