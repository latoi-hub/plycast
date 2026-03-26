# plycast

`plycast` is a Python library + CLI to:
- ingest long text content (novels, books, articles),
- translate from language A to language B,
- convert translated text to audio.

Default translator in CLI: `LibreTranslateTranslator` (self-host friendly).

This starter is built with pluggable providers so any app can embed it, and you can also run it manually from terminal.

## Features (starter)
- Read `.txt` and `.md` input files
- Chunk large text into smaller segments for translation
- Provider-based architecture:
  - `TranslatorProvider`: plug any translation engine
  - `TTSProvider`: plug any text-to-speech engine
- Built-in providers:
  - `IdentityTranslator` (dev stub, no translation)
  - `LibreTranslateTranslator` (real translation via HTTP API)
  - `OpenAITranslator` (paid LLM translation)
  - `AnthropicTranslator` (paid LLM translation)
  - `SystemSayTTS` (real audio on macOS using `say`)
  - `TextFileTTS` (dev fallback writes text output; no audio)
- CLI entrypoint: `python3 -m plycast.cli` (recommended)

## Install (editable)
```bash
python3 -m pip install -e .
```

The CLI automatically loads a `.env` file from the current working directory.

## Self-host LibreTranslate (Docker)
Run your own local translation service:

```bash
docker compose -f docker-compose.yml up -d
```

Check service health:

```bash
curl http://localhost:5001/languages
```

To add/remove supported languages, update `LT_LOAD_ONLY` in `docker-compose.yml`
and restart the container.

Use local URL:

```bash
python3 -m plycast.cli \
  --input ./dist/real_test_en.txt \
  --output-dir ./dist \
  --source-lang en \
  --target-lang vi \
  --libretranslate-url http://localhost:5001 \
  --tts text_file
```

Example: Chinese (Mandarin) -> Vietnamese:

```bash
python3 -m plycast.cli \
  --input ./dist/real_test_cn.txt \
  --output-dir ./dist \
  --source-lang zh \
  --target-lang vi \
  --libretranslate-url http://localhost:5001 \
  --tts text_file
```

Stop service:

```bash
docker compose -f docker-compose.yml down
```

## Smoke test script
Run an end-to-end local test (ingest -> translation -> TTS fallback):

```bash
python3 scripts/smoke_test.py
```

This creates test outputs in `dist/` and prints generated file paths.
Default smoke-test translator is `libretranslate` (self-hosted expected at `http://localhost:5001`).
Translator choices in the smoke test are currently limited to: `identity`, `libretranslate`.

Run smoke test with self-hosted LibreTranslate:

```bash
python3 scripts/smoke_test.py \
  --translator libretranslate \
  --libretranslate-url http://localhost:5001
```

## CLI Usage
```bash
python3 -m plycast.cli \
  --input ./book.txt \
  --output-dir ./dist \
  --source-lang en \
  --target-lang vi \
  --tts system_say
```

Output:
- translated text file in `dist/`
- audio file in `dist/` (default format: `.mp3`)

### Useful options
- `--translator libretranslate` to enable real translation
- `--translator identity` to bypass translation (debug mode)
- `--translator openai` to use OpenAI translation
- `--translator anthropic` to use Anthropic translation
- `--libretranslate-url https://libretranslate.com` to set API endpoint
- `--libretranslate-url http://localhost:5001` for local self-hosted Docker service
- `--libretranslate-api-key YOUR_KEY` or env `LIBRETRANSLATE_API_KEY`
- `--openai-api-key YOUR_KEY` or env `OPENAI_API_KEY`
- `--openai-model gpt-4o-mini` and `--openai-base-url ...`
- `--anthropic-api-key YOUR_KEY` or env `ANTHROPIC_API_KEY`
- `--anthropic-model claude-3-5-haiku-latest` and `--anthropic-base-url ...`
- `--tts text_file` to write a `.txt` artifact instead of generating audio
- `--voice "Samantha"` to choose macOS voice
- `--max-chunk-chars 1200` to tune translation chunk size
- `--audio-format mp3|aiff|wav|m4a` to choose audio output format (default: `mp3`)

## LLM translator examples
Use OpenAI:

```bash
OPENAI_API_KEY=your_key python3 -m plycast.cli \
  --input ./book.txt \
  --output-dir ./dist \
  --source-lang en \
  --target-lang vi \
  --translator openai \
  --openai-model gpt-4o-mini \
  --tts text_file
```

Use Anthropic:

```bash
ANTHROPIC_API_KEY=your_key python3 -m plycast.cli \
  --input ./book.txt \
  --output-dir ./dist \
  --source-lang en \
  --target-lang vi \
  --translator anthropic \
  --anthropic-model claude-3-5-haiku-latest \
  --tts text_file
```

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

## Extend with real translation/TTS services
Implement your own classes using:
- `plycast.providers.TranslatorProvider`
- `plycast.providers.TTSProvider`

Then pass them into `PlycastPipeline`.

## Environment variables
You can provide keys in `.env` (project root) or shell env:
- `OPENAI_API_KEY` (also supports legacy `openai-api-key`)
- `ANTHROPIC_API_KEY` (also supports legacy `anthropic-api-key`)
- `LIBRETRANSLATE_API_KEY` (also supports legacy `libretranslate-api-key`)

## Troubleshooting
If `system_say` sounds like it is spelling characters one-by-one, pick a voice that
supports your target language (especially for Vietnamese), and avoid mixed-script
text (e.g. Chinese punctuation + Vietnamese) in the same utterance.