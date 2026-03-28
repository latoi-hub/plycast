# Command-line interface (CLI)

Guidelines and option reference for the **`plycast`** Typer app. It mirrors the Python API (`convert_book`, `translate_book`, `synthesize_book`, `inspect_book`). For install, prerequisites, and Docker LibreTranslate, see **[QuickStart.md](QuickStart.md)**. For **`--voice`** and TTS engines, see **[Voices.md](Voices.md)**.

## Table of contents

- [How to run](#how-to-run)
- [Environment and `.env`](#environment-and-env)
- [Output files](#output-files)
- [`plycast convert`](#plycast-convert)
- [`plycast translate`](#plycast-translate)
- [`plycast tts`](#plycast-tts)
- [`plycast inspect`](#plycast-inspect)
- [Translators (`--translator`)](#translators---translator)
- [TTS backends (`--tts`)](#tts-backends---tts)
- [JSON output (`--json`)](#json-output---json)

Examples for **`convert`**, **`translate`**, **`tts`**, and **`inspect`** sit under each command below. For longer Vietnamese → English + Parler walkthroughs, see **[examples/README.md](../examples/README.md)**.

## How to run

After **`pip install plycast`**, the console script **`plycast`** is on your `PATH` inside the active virtual environment.

```bash
plycast --help
plycast convert --help
```

Same application via module:

```bash
python -m plycast.cli --help
python -m plycast.cli convert --help
```

With no arguments, **`plycast`** prints help (no subcommand is assumed).

## Environment and `.env`

On each run, plycast loads a **`.env`** file in the **current working directory** if it exists (key=value lines; existing real environment variables are not overwritten). Use this for **`OPENAI_API_KEY`**, **`LIBRETRANSLATE_API_KEY`**, etc. See **[QuickStart → Environment variables](QuickStart.md#environment-variables)**.

## Output files

Unless you pass **`--output-dir`** / **`-o`**, outputs go under **`dist/`** relative to the process **current working directory**.

| Step | Typical path |
|------|----------------|
| Translated text | `<output_dir>/<input_stem>.<target_lang>.txt` |
| Audio (`convert` / `tts`) | `<output_dir>/<input_stem>.<tts_or_target_lang>.<ext>` |

**`audio_format`** (default **`mp3`**) sets **`<ext>`** (`mp3`, `wav`, `aiff`, `m4a`). **`text_file`** TTS writes a **`.txt`** placeholder instead of sound.

## `plycast convert`

**Flow:** read input → translate → synthesize audio.

**Arguments**

| Argument | Description |
|----------|-------------|
| `INPUT_PATH` | Path to **`.txt`**, **`.md`**, **`.pdf`**, **`.docx`**, or a supported **image** (OCR). |

**Options**

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--source-lang` | `-s` | *(required)* | Source language tag (e.g. `en`, `vi`). For **images**, guides Tesseract OCR language. |
| `--target-lang` | `-t` | *(required)* | Target language for translation and for naming outputs. |
| `--output-dir` | `-o` | `dist` | Directory for `.txt` and audio files (created if needed). |
| `--translator` | | `libretranslate` | `identity` \| `libretranslate` \| `llm` |
| `--base-url` | | *(env)* | LibreTranslate or LLM API base URL when needed. |
| `--api-key` | | *(env)* | API key when the translator requires it. |
| `--llm-model` | | `gpt-4o-mini` | Model id when `--translator llm`. |
| `--llm-provider` | | *(inferred)* | `openai` \| `anthropic` if not inferred from `--llm-model`. |
| `--tts` | | *(platform)* | `system_say` \| `espeak` \| `parler` \| `text_file`. If omitted, **macOS** defaults to **`system_say`**; otherwise see wiring (may be **parler** if installed, else **espeak**). |
| `--voice` | | | **`system_say`**: macOS voice name. **`espeak`**: `-v` voice. **`parler`**: optional raw English description override. |
| `--parler-voice` | | | Seed **name** from packaged or custom JSON (see **Voices.md**). |
| `--parler-gender` | | | `female` \| `male` (with seed voices). |
| `--parler-seed` | | | Path to custom **`parler_voices.json`**. |
| `--max-chunk-chars` | | `1500` | Max characters per translation chunk. |
| `--audio-format` | | `mp3` | `mp3` \| `wav` \| `aiff` \| `m4a` |
| `--json` | | off | Print a JSON object for the result instead of human text. |

**Parler:** Intended for **English** speech; using **`--target-lang`** that is not English may sound poor. The CLI prints a **stderr** warning in that case.

### Examples (`convert`)

```bash
# Full pipeline with default translator (LibreTranslate). Point --base-url at your instance if needed.
plycast convert book.txt --source-lang vi --target-lang en --output-dir dist
```

```bash
# Same with short flags
plycast convert book.txt -s vi -t en -o dist
```

```bash
# Skip translation: copy text through, then TTS only (good for testing ingest + audio)
plycast convert draft.txt -s en -t en --translator identity --tts system_say
```

```bash
# LLM translation + Parler (English audio). Needs OPENAI_API_KEY (or --api-key) and: pip install 'plycast[parler]'
# From this repo root, sample input is under examples/input/
plycast convert examples/input/nhat-ky-nu-phap-y-c1.txt \
  -s vi -t en -o dist/examples \
  --translator llm --llm-model gpt-4o-mini \
  --tts parler --parler-voice laura --parler-gender female --audio-format mp3
```

```bash
# Machine-readable result (paths and metadata as JSON on stdout)
plycast convert article.md -s en -t de -o dist --json
```

## `plycast translate`

**Flow:** read input → translate → write **`<stem>.<target>.txt`** only (no audio).

**Arguments:** `INPUT_PATH` (same as **convert**).

**Options**

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--source-lang` | `-s` | *(required)* | Source language. |
| `--target-lang` | `-t` | *(required)* | Target language. |
| `--output-dir` | `-o` | `dist` | Output directory. |
| `--translator` | | `libretranslate` | `identity` \| `libretranslate` \| `llm` |
| `--base-url` | | *(env)* | See **convert**. |
| `--api-key` | | *(env)* | See **convert**. |
| `--llm-model` | | `gpt-4o-mini` | With **`llm`**. |
| `--llm-provider` | | *(inferred)* | `openai` \| `anthropic` |
| `--max-chunk-chars` | | `1500` | Translation chunk size. |
| `--json` | | off | JSON result. |

### Examples (`translate`)

```bash
# Text only: writes dist/article.de.txt (no audio)
plycast translate article.md --source-lang en --target-lang de --output-dir dist
```

```bash
# Short flags; uses default LibreTranslate unless you set --base-url / env
plycast translate notes.txt -s vi -t en -o out
```

```bash
# No API: “translate” by copying (identity) — output still named with target lang
plycast translate raw.txt -s en -t en --translator identity -o dist
```

```bash
plycast translate book.txt -s fr -t en --json
```

## `plycast tts`

**Flow:** read input → synthesize speech (no translation). The text language is **`--lang`**.

**Arguments:** `INPUT_PATH`.

**Options**

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--lang` | `-l` | *(required)* | Language of the **source text** (passed to the TTS engine). |
| `--output-dir` | `-o` | `dist` | Output directory. |
| `--tts` | | *(platform)* | `system_say` \| `espeak` \| `parler` \| `text_file` |
| `--voice` | | | Engine-specific voice (see **Voices.md**). |
| `--parler-voice` | | | Parler seed name. |
| `--parler-gender` | | | `female` \| `male` |
| `--parler-seed` | | | Custom seed JSON path. |
| `--audio-format` | | `mp3` | `mp3` \| `wav` \| `aiff` \| `m4a` |
| `--json` | | off | JSON result. |

Audio file name uses **`<stem>.<lang>.<ext>`** (e.g. **`book.vi.mp3`**).

### Examples (`tts`)

```bash
# Speak existing text as-is (language must match the text). Default TTS is platform-dependent.
plycast tts speech.txt --lang en --output-dir dist
```

```bash
# Short flag; force espeak on Linux (install espeak-ng)
plycast tts speech.txt -l en --tts espeak -o dist
```

```bash
# macOS say with a named voice (see Voices.md)
plycast tts examples/input/nhat-ky-nu-phap-y-c1.txt -l vi --tts system_say --voice Linh -o dist
```

```bash
# English neural TTS (Parler); pip install 'plycast[parler]'
plycast tts chapter.en.txt -l en --tts parler --parler-voice laura --parler-gender female -o dist
```

```bash
# CI / no audio codec: writes a .txt placeholder instead of sound
plycast tts notes.txt -l en --tts text_file -o dist --json
```

## `plycast inspect`

**Flow:** show path, suffix, size, optional character count and text preview (ingest debugging).

**Arguments:** `INPUT_PATH`.

**Options**

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--source-lang` | `-s` | *(none)* | For **images**, OCR language hint. |
| `--preview-chars` | | `240` | Max characters in preview. |
| `--json` | | off | JSON result. |

### Examples (`inspect`)

```bash
# Path, suffix, size, character count, and text preview (first ~240 chars)
plycast inspect document.txt
```

```bash
# PDF or docx: preview shows extracted plain text when supported
plycast inspect report.pdf
```

```bash
# Image ingest: --source-lang is the Tesseract language hint (e.g. eng, vie)
plycast inspect scan.png --source-lang eng --preview-chars 400
```

```bash
plycast inspect notes.md --json
```

## Translators (`--translator`)

| Value | When to use |
|-------|-------------|
| **`libretranslate`** | Default. Set **`--base-url`** to your instance (or rely on defaults / env). Self-host: **[QuickStart → Docker](QuickStart.md#self-hosted-libretranslate-docker)**. |
| **`identity`** | Copy-through (no translation). Useful to test **TTS** or file ingest. |
| **`llm`** | OpenAI or Anthropic. Set **`OPENAI_API_KEY`** or **`ANTHROPIC_API_KEY`** (or **`--api-key`**). **`--llm-model`** required; **`--llm-provider`** optional if the model name implies the vendor. |

## TTS backends (`--tts`)

| Value | Platform / notes |
|-------|------------------|
| **`system_say`** | **macOS** **`say`**. |
| **`espeak`** | **`espeak-ng`** or **`espeak`** on `PATH`. |
| **`parler`** | Neural TTS; install **`pip install 'plycast[parler]'`**. **English-centric** for reliable quality. |
| **`text_file`** | Writes a **`.txt`** artifact instead of audio (CI / quick checks). |

Default when **`--tts`** is omitted is chosen at runtime (see **`default_tts_backend`** in code): typically **`system_say`** on macOS, else **parler** if importable, else **espeak**.

## JSON output (`--json`)

With **`--json`**, the command prints one JSON object (UTF-8, indented) suitable for scripting. Fields match the corresponding result dataclass (`ConvertResult`, `TranslateResult`, `TtsResult`, `InspectResult`).

```bash
plycast inspect input.txt --json
plycast translate input.txt -s en -t es -o dist --json
plycast tts input.txt -l en -o dist --json
plycast convert input.txt -s en -t fr -o dist --json
```

---

**More recipes (Vietnamese sources, Parler, Python):** **[examples/README.md](../examples/README.md)**.
