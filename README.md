# plycast

`plycast` is a Python library + CLI to:

- **Ingest** long text from multiple formats (see below),
- **Translate** from language A to language B,
- **Synthesize** audio from translated text.

Default translator in the CLI: **LibreTranslate** (self-hosted friendly).

## Architecture (layers)

1. **`plycast.providers`** — vendor packages (auth + HTTP client + translator per vendor):
   - `plycast.providers.openai` — `BearerToken`, `OpenAIClient`, `OpenAITranslator`
   - `plycast.providers.anthropic` — `AnthropicClient`, `AnthropicTranslator`
   - `plycast.providers.libretranslate` — `LibreTranslateClient`, `LibreTranslateTranslator`
   - `plycast.providers.tts` — `SystemSayTTS`, `TextFileTTS`, audio conversion helpers
   - `plycast.providers.llm` — `LLMTranslator`, `infer_llm_provider`
   - Shared: `base.py` (protocols), `http.py`, `translation_prompt.py`
   - Legacy aliases: `OpenAIConnector` = `OpenAIClient`, etc.
2. **`plycast.services`** — `TranslateService`, `ReadTextService`, `AudioService`; wire translators/TTS via static methods on those classes.
3. **`plycast.pipelines`** — composed flows: read-only, read→translate, read→translate→audio, read→audio (no translation).
4. **`PlycastPipeline`** + **`plycast.cli`** — convenience wrapper and CLI.

## Features

- **Input formats**
  - **Always:** `.txt`, `.md`, `.markdown`
  - **Optional extras:** `pip install ".[docs]"` for **PDF** (pypdf) and **Word** (python-docx). **Image OCR** uses Pillow + pytesseract (installed with plycast); you still need a **Tesseract** binary on `PATH` (e.g. `brew install tesseract tesseract-lang` on macOS for Chinese `chi_sim`). For images, **`--source-lang`** selects the Tesseract language pack (e.g. `zh` → simplified Chinese).
- Chunk large text for translation
- **Translators:** `IdentityTranslator`, `LibreTranslateTranslator`, `OpenAITranslator`, `AnthropicTranslator`, **`LLMTranslator`** (model + optional provider; infers vendor from model id when omitted)
- **TTS:** `SystemSayTTS` (macOS `say`, optional `ffmpeg` for mp3/wav/m4a), `TextFileTTS` (writes a text artifact instead of audio)
- **CLI:** `python3 -m plycast.cli` or the `plycast` console script

## Install

```bash
python3 -m pip install -e .
# equivalent: pip install -r requirements.txt
```

Dependencies live in **`pyproject.toml`**; **`requirements.txt`** only installs the project in editable mode so you do not duplicate version pins.

Optional capability groups:

```bash
python3 -m pip install -e ".[docs]"  # pdf + docx
python3 -m pip install -e ".[full]" # pdf + docx (same as docs)
```

Dev dependencies (tests):

```bash
python3 -m pip install -e ".[dev]"
python3 -m pytest
```

The CLI loads a `.env` file from the current working directory when present.

## Self-host LibreTranslate (Docker)

```bash
docker compose -f docker-compose.yml up -d
```

Health check:

```bash
curl http://localhost:5001/languages
```

Adjust `LT_LOAD_ONLY` in `docker-compose.yml` for loaded languages, then restart the container.

Example with local LibreTranslate:

```bash
python3 -m plycast.cli \
  --input ./dist/real_test_en.txt \
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

## Smoke test script

```bash
python3 scripts/smoke_test.py
```

Translators supported by the smoke script: `identity`, `libretranslate`.

```bash
python3 scripts/smoke_test.py \
  --translator libretranslate \
  --libretranslate-url http://localhost:5001
```

## CLI usage

```bash
python3 -m plycast.cli \
  --input ./book.txt \
  --output-dir ./dist \
  --source-lang en \
  --target-lang vi \
  --tts system_say
```

Outputs:

- Translated text: `dist/<stem>.<target>.txt`
- Audio (default **mp3**): `dist/<stem>.<target>.mp3`

### Common options

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

### LLM examples

**Unified (`llm`) — provider inferred from model:**

```bash
OPENAI_API_KEY=your_key python3 -m plycast.cli \
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
ANTHROPIC_API_KEY=your_key python3 -m plycast.cli \
  --input ./book.txt \
  --output-dir ./dist \
  --source-lang en \
  --target-lang vi \
  --translator llm \
  --llm-provider anthropic \
  --llm-model claude-3-5-haiku-latest \
  --tts text_file
```

**Chinese → Vietnamese** (`llm` + macOS `say`, Vietnamese voice):

```bash
OPENAI_API_KEY=your_key python3 -m plycast.cli \
  --input dist/real_test_cn.txt \
  --output-dir dist \
  --source-lang zh \
  --target-lang vi \
  --translator llm \
  --llm-model gpt-4o-mini \
  --tts system_say \
  --voice "Linh"
```

(If `OPENAI_API_KEY` is already exported, drop the prefix; or use `--api-key` instead.)

## Library usage

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

**Pipelines without the full class:**

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

## Extending

Implement against:

- `plycast.providers.TranslatorProvider`
- `plycast.providers.TTSProvider`

Outbound HTTP for vendors lives under **`plycast.providers.<vendor>`** (clients + auth).

## Environment variables

| Variable | Used for |
|----------|-----------|
| `OPENAI_API_KEY` | OpenAI / `llm` when routed to OpenAI |
| `ANTHROPIC_API_KEY` | Anthropic / `llm` when routed to Anthropic |
| `LIBRETRANSLATE_API_KEY` | LibreTranslate |

Legacy dotted names (`openai-api-key`, etc.) are still read by the CLI for compatibility.

## Troubleshooting

- **`system_say` spells characters:** pick a voice that matches the target language (e.g. Vietnamese), and avoid mixed-script paragraphs (Chinese + Vietnamese) in one utterance.
- **MP3 output:** `system_say` emits AIFF first; **ffmpeg** is used for conversion. Install with `brew install ffmpeg` on macOS if needed.
