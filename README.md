# plycast

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![PyPI](https://img.shields.io/badge/PyPI-plycast-3775A9?logo=pypi&logoColor=white)](https://pypi.org/project/plycast/)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Open Source](https://img.shields.io/badge/open%20source-yes-success.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-0.1.0-informational.svg)](pyproject.toml)

**Ingest** text from common formats, **translate** in chunks, **synthesize** audio — as a **Python library** you import and a **CLI** you run on the same implementation.

**plycast** is **open-source** software ([MIT License](LICENSE)): you may use, modify, and distribute it freely.

---

## Table of contents

- [About](#about)
- [Installation](#installation)
- [Features](#features)
- [Quick CLI sample (LLM)](#quick-cli-sample-llm)
- [Architecture](#architecture)
- [Documentation](#documentation)
- [Contributing](#contributing)
- [License](#license)

## About

This repository contains:

| Piece | What it is |
|-------|------------|
| **Library** | Importable **`plycast`**: workflow helpers (**`convert_book`**, …), **`PlycastPipeline`**, **`io`**, **`plycast.engines`** (translate, TTS, audio encode), and **`plycast.pipeline`**. |
| **CLI** | **`plycast`** (Typer): **`convert`**, **`translate`**, **`tts`**, **`inspect`** — thin wrapper over the same functions as the Python API. Also **`python -m plycast.cli`**. |

Together they cover: plain text and Markdown; optional PDF/Word (extra deps); images via **OCR** (Pillow + pytesseract + system **Tesseract**); translation through **LibreTranslate**, vendor LLMs, or **identity** passthrough; speech via macOS **`say`**, **espeak-ng**, **Parler-TTS** (optional extra), or a text-only artifact for CI. **Package layout:** `src/plycast/` (src layout); core workflows live in **`plycast.pipeline.convert`** (`core/`, `io/`, **`engines/`** (translate, tts, audio), `pipeline/`, …).

The default CLI translator is **LibreTranslate**, which you can [self-host](https://github.com/LibreTranslate/LibreTranslate) or use against a public instance, depending on your `--base-url`.

**Choosing a translator:** **`--translator llm`** (OpenAI or Anthropic) is aimed at **natural, fluent** output—well suited to audiobook-style listening when you want the model’s tone and wording. **LibreTranslate** is a **free, open stack** you can run yourself; it is a strong fit when you want a **draft to review and edit** (adjust the translated `.txt`, then regenerate audio) or to keep costs and data policy simple.

## Installation

**Published package:** [plycast on PyPI](https://pypi.org/project/plycast/).

1. Use **Python 3.10+** and a virtual environment (`python -m venv .venv` then `source .venv/bin/activate` on macOS/Linux, or `.venv\Scripts\activate` on Windows).
2. Install the library and CLI:

   ```bash
   pip install plycast
   ```

   That installs core dependencies (Typer, Rich, Pillow, pytesseract, …). You still need a **Tesseract** binary on your system for image OCR; see [QuickStart](docs/QuickStart.md).

3. **Optional extras** (pick what you need):

   | Extra | Command | Purpose |
   |-------|---------|---------|
   | PDF / Word | `pip install 'plycast[docs]'` | `pypdf`, `python-docx` for `.pdf` / `.docx` |
   | Parler TTS | `pip install 'plycast[parler]'` | Neural TTS (large deps: torch, transformers, soundfile, …) |
   | Docs + PDF/Word | `pip install 'plycast[full]'` | Same as `[docs]` today |
   | Development | `pip install 'plycast[dev]'` | pytest (for contributors) |

4. **From a git clone** (editable install):

   ```bash
   pip install -e ".[dev]"
   ```

   Add `[docs]` or `[parler]` as needed, e.g. `pip install -e ".[dev,docs]"`.

More detail, env vars, and troubleshooting → **[docs/QuickStart.md](docs/QuickStart.md)**.

## Features

- **Input:** `.txt`, `.md`; optional `.pdf` / `.docx` (`pip install ".[docs]"`); images with OCR and `--source-lang` for Tesseract languages (e.g. `zh`).
- **Translation:** chunked text; **LLM** path for natural tone; **LibreTranslate** for a free, self-hostable draft you can review and edit; Identity, OpenAI, Anthropic, unified **LLM** routing (`LLMTranslator`).
- **Audio:** **`SystemSayTTS`** (macOS **`say`**); **`ParlerTTS`** / **`--tts parler`** (neural TTS, **English-only** for reliable quality; optional **`pip install 'plycast[parler]'`**, default on non-macOS when installed; seed voices + **`--parler-gender`**, or raw **`--voice`**); **`EspeakTTS`** / **`--tts espeak`** (**`espeak-ng`**, fallback when Parler is not installed); **`TextFileTTS`** / **`--tts text_file`** anywhere. See **[docs/Voices.md](docs/Voices.md)**.
- **CLI:** flags for translator, languages, API keys, TTS, chunk size — see QuickStart.

## Quick CLI sample (LLM)

Set **`OPENAI_API_KEY`** (or **`ANTHROPIC_API_KEY`** if you use a Claude model with `--llm-provider anthropic` / inferred from the model name), then run:

```bash
export OPENAI_API_KEY={Your API Key}
plycast convert ./book.png \
  --output-dir ./dist \
  --source-lang vi \
  --target-lang en \
  --translator llm \
  --llm-model gpt-4o-mini \
  --tts system_say \
  --voice "Samantha"
```

**Images** use OCR (install **Tesseract**; `--source-lang` selects the OCR language). For a faster check without audio, use **`--tts text_file`**. More examples and flags → **[docs/QuickStart.md](docs/QuickStart.md)**.

## Architecture

1. **`plycast.pipeline.convert`** — **`convert_book`**, **`translate_book`**, **`synthesize_book`**, **`load_book`**, **`inspect_book`** (public API; CLI calls these).
2. **`plycast.pipeline.wiring`** — shared translator/TTS construction for API + CLI.
3. **`plycast.engines`** — **`engines.translate`** / **`engines.tts`** (protocols, providers, services) and **`engines.audio`** (format conversion for TTS output).
4. **`plycast.io`** — **`ReadTextService`** and format loaders.
5. **`plycast.pipeline`** — book-style API (**`convert`**, **`composed`**, **`facade`**, **`wiring`**): composed flows + **`PlycastPipeline`**.
6. **`plycast.cli`** — Typer app (`plycast convert`, …).

Implement custom backends against **`TranslatorProvider`** and **`TTSProvider`** in **`plycast.engines.translate.base`** and **`plycast.engines.tts.base`**.

## Documentation

| Doc | Contents |
|-----|----------|
| **[docs/QuickStart.md](docs/QuickStart.md)** | Install, prerequisites, CLI, LibreTranslate Docker, LLM examples, Python API, env vars, troubleshooting |
| **[docs/Voices.md](docs/Voices.md)** | **`system_say`** (macOS) and **`espeak`** (Linux-friendly) voices / **`--voice`** |
| **This README** | Project introduction and layout |

## Contributing

A **contribution workflow** (guidelines, review process, and what we merge) is **in progress** and **not finalized** yet — so we are **not ready for pull requests** or formal code contributions at this time.

**Issues are welcome:** please [open an issue](https://github.com/latoi-hub/plycast/issues) on GitHub for bugs, ideas, or questions.

## License

**Open-source.** This project is released under the [MIT License](LICENSE).
