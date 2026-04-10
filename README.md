# plycast

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![PyPI](https://img.shields.io/badge/PyPI-plycast-3775A9?logo=pypi&logoColor=white)](https://pypi.org/project/plycast/)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Open Source](https://img.shields.io/badge/open%20source-yes-success.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-0.1.1-informational.svg)](pyproject.toml)

Turn documents into translated audio — in one command.

Convert text, PDFs, Word docs, or images into **natural-sounding multilingual audiobooks** using translation + text-to-speech in a single pipeline.



## 📑 Table of contents

- [Quick start](#-quick-start)
- [What you can do](#-what-you-can-do)
- [Example](#-example-real-usage)
- [Why plycast](#-why-plycast)
- [Supported inputs](#-supported-inputs)
- [Audio output](#-audio-output)
- [Translation options](#-translation-options)
- [Installation](#-installation)
- [CLI usage](#-cli-usage)
- [Python usage](#-python-usage)
- [Features](#-features)
- [Documentation](#-documentation)
- [Use cases](#-use-cases)
- [Contributing](#-contributing)
- [License](#-license)

---

## ⚡ Quick start

Install:

```bash
pip install plycast
```

Run:

```bash
plycast tts input.txt
```

Python:

```python
from plycast import synthesize_book

result = synthesize_book("input.txt")
print(result.audio_path)
```

👉 That’s it — text → audio.

---

## 🎯 What you can do

* 📚 Convert documents into audiobooks
* 🌍 Translate into another language
* 🧠 Use LLMs for more natural phrasing
* 🔊 Generate audio (MP3, WAV, etc.)
* 🖼️ Extract text from images (OCR)

---

## 💡 Example (real usage)

```bash
plycast tts book.txt --lang vi
```

```python
from pathlib import Path
from plycast import synthesize_book

r = synthesize_book(
    Path("book.txt"),
    tts_language="vi",
    audio_format="mp3",
)

print(r.audio_path)
```

---

## 🧠 Why plycast?

* **All-in-one pipeline**
  No need to glue translation + TTS tools together

* **Better for listening**
  LLM-based translation produces more natural speech

* **Flexible**
  Works locally or with APIs (BYOK-friendly)

* **CLI + Python**
  Use it in scripts or quick terminal workflows

---

## 📦 Supported inputs

* ✅ Text (`.txt`, `.md`)
* 📄 PDF / Word (`.pdf`, `.docx`) *(optional install)*
* 🖼️ Images (via OCR)

---

## 🔊 Audio output

* System voices (macOS `say`, Linux `espeak`)
* Neural voices (optional)
* Formats: WAV, MP3, M4A (with ffmpeg)

---

## 🌍 Translation options

* **LibreTranslate**

  * Free / self-hostable
  * Good for editable drafts

* **LLMs (OpenAI, Anthropic)**

  * More natural phrasing
  * Better for listening

---

## 📥 Installation

### Basic install (recommended first)

```bash
pip install plycast
```

Works immediately for:

* text input
* basic TTS

---

### Optional features

| Feature    | Install                         | Purpose                 |
| ---------- | ------------------------------- | ----------------------- |
| PDF / Word | `pip install "plycast[docs]"`   | `.pdf`, `.docx` support |
| Neural TTS | `pip install "plycast[parler]"` | higher-quality voices   |
| Full       | `pip install "plycast[full]"`   | everything              |
| Dev        | `pip install "plycast[dev]"`    | contributors            |

---

## ⚙️ Optional system setup

Only needed depending on features you use:

### OCR (images)

Install **Tesseract**

* macOS: `brew install tesseract`
* Ubuntu: `sudo apt install tesseract-ocr`
* Windows: installer or `winget install tesseract`

---

### Audio formats (MP3, M4A)

Install **ffmpeg**

* macOS: `brew install ffmpeg`
* Ubuntu: `sudo apt install ffmpeg`
* Windows: `winget install ffmpeg`

---

### Speech engines

* macOS: built-in `say` (no install)
* Linux: `espeak-ng`

---

## 🧪 CLI usage

Basic:

```bash
plycast tts input.txt
```

With options:

```bash
plycast tts input.txt \
  --lang en \
  --tts system_say \
  --voice Samantha \
  --audio-format mp3
```

---

## 🐍 Python usage

```python
from pathlib import Path
from plycast import synthesize_book

result = synthesize_book(
    Path("input.txt"),
    tts_language="en",
    tts="system_say",
    voice="Samantha",
    audio_format="mp3",
)

print(result.audio_path)
```

---

## 🧩 Features

* Chunked text processing
* OCR support (Tesseract)
* Multiple translators (LibreTranslate, LLMs)
* Multiple TTS backends
* CLI + Python API
* Local-first, API-optional

---

## 📚 Documentation

* `docs/QuickStart.md` — setup and tutorials
* `docs/CLI.md` — full CLI reference
* `docs/Voices.md` — voice options
* `examples/` — real usage examples

---

## 🛠️ Use cases

* Listen to books or articles in another language
* Convert PDFs into audiobooks
* Translate and narrate notes
* Turn scanned text into speech

---

## 🤝 Contributing

Contribution workflow is not finalized yet.

For now:

* Open issues for bugs or ideas
* Discussions and feedback welcome

---

## 📄 License

MIT License — open-source and free to use.
