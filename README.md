# plycast

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![PyPI](https://img.shields.io/badge/PyPI-plycast-3775A9?logo=pypi&logoColor=white)](https://pypi.org/project/plycast/)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Open Source](https://img.shields.io/badge/open%20source-yes-success.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-0.1.2-informational.svg)](pyproject.toml)

Convert books into multilingual audiobooks with context-aware LLM translation and text-to-speech.
Turn PDF, DOCX, images, or text → translate → generate audio (MP3) in one pipeline.

## 🚀 At a glance

- 📚 Convert documents into **translated audiobooks**
- 🌍 Multilingual support with LLM-based translation
- 🧠 More natural, context-aware wording (better for listening)
- 🔌 Open-source, local-first, BYOK-friendly


---

## Table of contents

- [About](#about)
- [Installation](#installation)
- [Features](#features)
- [Documentation](#documentation)
- [Contributing](#contributing)
- [License](#license)

## About

**What it’s for**

- One workflow from a **file on disk** to **translated text** and **audio**—no need to chain many tools by hand.
- Fits **drafts, articles, chapters**, or **scans** you’d rather **listen to** in another language.

**How you use it**

- **Terminal:** run the **`plycast`** command for quick jobs.
```bash
plycast tts examples/input/nhat-ky-nu-phap-y-c1.txt \
  --lang vi --tts system_say --voice Linh
```
- **Python:** after **`import plycast`** use it in Python scripts
```python
from pathlib import Path
from plycast import synthesize_book

r = synthesize_book(
    Path("examples/input/nhat-ky-nu-phap-y-c1.txt"),
    tts_language="vi",
    tts="system_say",
    voice="Linh",
    audio_format="mp3",
)
print(r.audio_path)
```

**Inputs**

- **Text** and **Markdown** out of the box.
- **PDF**, **Word**, and **images** (e.g. photos of text) with a little extra setup.

**Translation (pick what matches you)**

- **LibreTranslate** (hosted or self-hosted): straightforward; good if you want to **edit the text** before audio.
- **Large language models**: geared toward **natural, listenable** wording when you’re fine using a **vendor API** and key.

**Speech**

- Uses **voices already on your system** where possible (e.g. Mac **say**, **espeak**-style on Linux).
- Optional **neural** voices if you install that stack.

## Installation

**Published package:** [plycast on PyPI](https://pypi.org/project/plycast/).

### Prerequisites

Before `pip install`, install anything below that matches what you will use. After installing **system** tools, open a **new terminal** (or restart the IDE) so `PATH` updates.

- **Python 3.10+** (3.11+ recommended)  
  - **Where:** [python.org/downloads](https://www.python.org/downloads/), your OS package manager, or a version manager (**pyenv**, **conda**, etc.).  
  - **Check:** `python3 --version` (or `python --version` on Windows).

- **Virtual environment** (recommended)  
  - **How:** `python3 -m venv .venv` then `source .venv/bin/activate` (macOS/Linux) or `.venv\Scripts\activate` (Windows).  
  - **Why:** keeps `pip install plycast` isolated from system Python.

- **Tesseract** (only if you use **image** inputs for OCR)  
  - **What:** the `tesseract` binary on your `PATH` (plycast installs **pytesseract** via pip, not the engine).  
  - **macOS (Homebrew):** `brew install tesseract tesseract-lang`  
  - **Debian / Ubuntu:** `sudo apt install tesseract-ocr` (add language packs, e.g. `tesseract-ocr-chi-sim`, as needed)  
  - **Windows:** installer from the [Tesseract at UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki) wiki, or **Chocolatey** / **winget** packages named `tesseract`.  
  - **Check:** `tesseract --version`

- **ffmpeg** (only if you want **mp3 / m4a / aiff** after WAV-based TTS)  
  - **macOS (Homebrew):** `brew install ffmpeg`  
  - **Debian / Ubuntu:** `sudo apt install ffmpeg`  
  - **Windows:** `winget install ffmpeg` or [ffmpeg.org](https://ffmpeg.org/download.html) builds; ensure `ffmpeg` is on `PATH`.  
  - **Check:** `ffmpeg -version`

- **Speech backends** (pick what matches `--tts`):
  - **`system_say`:** **macOS** only — uses the built-in **`say`** command; nothing to install.
  - **`espeak`:** install **`espeak-ng`** (or legacy **`espeak`**) on your `PATH`.  
    - **Debian / Ubuntu:** `sudo apt install espeak-ng`  
    - **macOS (Homebrew):** `brew install espeak`  
    - **Check:** `espeak-ng --version` or `espeak --version`
  - **`text_file`:** no audio engine.

- **Translation / APIs**  
  - **LibreTranslate:** run your own server (e.g. Docker — see **[QuickStart → Self-hosted LibreTranslate](docs/QuickStart.md#self-hosted-libretranslate-docker)**) or use a host you trust; optional API key.  
  - **LLM (OpenAI / Anthropic):** create a key in the vendor console ([OpenAI](https://platform.openai.com/), [Anthropic](https://console.anthropic.com/)); export **`OPENAI_API_KEY`** or **`ANTHROPIC_API_KEY`** (details in [QuickStart](docs/QuickStart.md#environment-variables)).

More env vars, CLI flags, and troubleshooting → **[docs/QuickStart.md](docs/QuickStart.md)**.

### Install with pip

1. Activate your virtual environment (see above).
2. Install the library and CLI:

   ```bash
   pip install plycast
   ```

   This pulls in core Python packages (Typer, Rich, Pillow, pytesseract, …). System tools (**Tesseract**, **ffmpeg**, etc.) stay separate—see **Prerequisites**.

3. **Optional extras** (pick what you need):

   | Extra | Command | Purpose |
   |-------|---------|---------|
   | PDF / Word | `pip install 'plycast[docs]'` | `pypdf`, `python-docx` for `.pdf` / `.docx` |
   | Parler TTS | `pip install 'plycast[parler]'` | Neural TTS (Parler-TTS, PyTorch, transformers, soundfile, … — large download). **English-centric**; see **[Voices.md](docs/Voices.md)**. |
   | Docs + PDF/Word | `pip install 'plycast[full]'` | Same as `[docs]` today |
   | Development | `pip install 'plycast[dev]'` | pytest (for contributors) |

   **Parler troubleshooting:** if **`soundfile`** fails to install, install OS **libsndfile** first (macOS: `brew install libsndfile`; Debian/Ubuntu: `sudo apt install libsndfile1`), then re-run **`pip install 'plycast[parler]'`**. **mp3 / m4a** output still needs **ffmpeg** (see **Prerequisites**).

4. **From a git clone** (editable install):

   ```bash
   pip install -e ".[dev]"
   ```

   Add `[docs]` or `[parler]` as needed, e.g. `pip install -e ".[dev,docs]"`.

## Features

- **Input:** `.txt`, `.md`; optional `.pdf` / `.docx` (`pip install ".[docs]"`); images with OCR and `--source-lang` for Tesseract languages (e.g. `zh`).
- **Translation:** chunked text; **LLM** path for natural tone; **LibreTranslate** for a free, self-hostable draft you can review and edit; Identity, OpenAI, Anthropic, unified **LLM** routing (`LLMTranslator`).
- **Audio:** **`SystemSayTTS`** (macOS **`say`**); **`ParlerTTS`** / **`--tts parler`** (neural TTS, **English-only** for reliable quality; optional **`pip install 'plycast[parler]'`**, default on non-macOS when installed; seed voices + **`--parler-gender`**, or raw **`--voice`**); **`EspeakTTS`** / **`--tts espeak`** (**`espeak-ng`**, fallback when Parler is not installed); **`TextFileTTS`** / **`--tts text_file`** anywhere. See **[docs/Voices.md](docs/Voices.md)**.
- **CLI:** flags for translator, languages, API keys, TTS, chunk size — **[docs/CLI.md](docs/CLI.md)** (reference) and **[docs/QuickStart.md](docs/QuickStart.md)** (tutorials).

## Documentation

| Doc | Contents |
|-----|----------|
| **[docs/QuickStart.md](docs/QuickStart.md)** | Install, prerequisites, CLI intro, LibreTranslate Docker, LLM examples, Python API, env vars, troubleshooting |
| **[docs/CLI.md](docs/CLI.md)** | **CLI reference:** all commands and options (`convert`, `translate`, `tts`, `inspect`), outputs, translators, TTS backends, `--json` |
| **[docs/Voices.md](docs/Voices.md)** | **`system_say`** (macOS) and **`espeak`** (Linux-friendly) voices / **`--voice`** |
| **[examples/README.md](examples/README.md)** | Vietnamese sample: **vi → en + Parler (laura)** and **vi + system_say (Linh)** — CLI + Python |
| **This README** | Project introduction and layout |

## Contributing

A **contribution workflow** (guidelines, review process, and what we merge) is **in progress** and **not finalized** yet — so we are **not ready for pull requests** or formal code contributions at this time.

**Issues are welcome:** please [open an issue](https://github.com/latoi-hub/plycast/issues) on GitHub for bugs, ideas, or questions.

## License

**Open-source.** This project is released under the [MIT License](LICENSE).
