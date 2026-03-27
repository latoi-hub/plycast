# plycast

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Open Source](https://img.shields.io/badge/open%20source-yes-success.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-0.1.0-informational.svg)](pyproject.toml)

**Ingest** text from common formats, **translate** in chunks, **synthesize** audio — as a **Python library** you import and a **CLI** you run on the same implementation.

**plycast** is **open-source** software ([MIT License](LICENSE)): you may use, modify, and distribute it freely.

---

## Table of contents

- [About](#about)
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
| **Library** | Importable package **`plycast`**: `providers` (translators, TTS), `services`, `pipelines`, and **`PlycastPipeline`** for end-to-end runs from Python. |
| **CLI** | Commands **`plycast`** and **`python -m plycast.cli`** — thin wrapper around the same pipeline code; useful for scripts and automation. |

Together they cover: plain text and Markdown; optional PDF/Word (extra deps); images via **OCR** (Pillow + pytesseract + system **Tesseract**); translation through **LibreTranslate**, vendor LLMs, or **identity** passthrough; speech via macOS **`say`** (with optional **ffmpeg** for mp3/wav/m4a) or a text-only artifact for CI.

The default CLI translator is **LibreTranslate**, which you can [self-host](https://github.com/LibreTranslate/LibreTranslate) or use against a public instance, depending on your `--base-url`.

**Choosing a translator:** **`--translator llm`** (OpenAI or Anthropic) is aimed at **natural, fluent** output—well suited to audiobook-style listening when you want the model’s tone and wording. **LibreTranslate** is a **free, open stack** you can run yourself; it is a strong fit when you want a **draft to review and edit** (adjust the translated `.txt`, then regenerate audio) or to keep costs and data policy simple.

**Install:** use **`pip install plycast`** from PyPI, or install from a clone — see **[docs/QuickStart.md](docs/QuickStart.md)**.

## Features

- **Input:** `.txt`, `.md`; optional `.pdf` / `.docx` (`pip install ".[docs]"`); images with OCR and `--source-lang` for Tesseract languages (e.g. `zh`).
- **Translation:** chunked text; **LLM** path for natural tone; **LibreTranslate** for a free, self-hostable draft you can review and edit; Identity, OpenAI, Anthropic, unified **LLM** routing (`LLMTranslator`).
- **Audio:** **`SystemSayTTS`** (macOS **`say`**); **`EspeakTTS`** / **`--tts espeak`** (**`espeak-ng`**, default on Linux); **`TextFileTTS`** / **`--tts text_file`** anywhere. See **[docs/Voices.md](docs/Voices.md)**.
- **CLI:** flags for translator, languages, API keys, TTS, chunk size — see QuickStart.

## Quick CLI sample (LLM)

Set **`OPENAI_API_KEY`** (or **`ANTHROPIC_API_KEY`** if you use a Claude model with `--llm-provider anthropic` / inferred from the model name), then run:

```bash
export OPENAI_API_KEY={Your API Key}
plycast \
  --input ./book.png \
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

1. **`plycast.providers`** — vendor code (HTTP clients, auth, translators, TTS), plus `base` protocols, `llm`, `translation_prompt`.
2. **`plycast.services`** — **`TranslateService`**, **`ReadTextService`**, **`AudioService`** (including static factory methods for wiring).
3. **`plycast.pipelines`** — composed flows: read-only, read→translate, read→translate→audio, read→audio.
4. **`PlycastPipeline`** + **`plycast.cli`** — convenience wrapper and command-line entry points.

Implement custom backends against **`TranslatorProvider`** and **`TTSProvider`** in `plycast.providers.base`.

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
