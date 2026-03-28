# TTS voices (`--tts`, `--voice`)

plycast supports:

| `--tts` | Platform | Engine |
|---------|----------|--------|
| **`system_say`** (default on **macOS**) | macOS | Built-in **`say`** |
| **`parler`** (default on **Linux** / Windows when installed) | Linux, Windows, macOS | **[Parler-TTS](https://github.com/huggingface/parler-tts)** — **English speech only** for reliable quality (neural; GPU/MPS/CPU) |
| **`espeak`** (fallback on **Linux** / Windows if Parler is not installed) | Linux, Windows, macOS | **`espeak-ng`** or **`espeak`** on `PATH` |
| **`text_file`** | Any | No audio; writes a text artifact |

Use **`--voice`** with **`system_say`** (macOS voice name), **`espeak`** (espeak `-v` voice), or **`parler`** (optional full English **description** override—see below). If you omit **`--voice`**, espeak picks a voice from **`--target-lang`**. For **Parler**, use **English** as **`--target-lang`** for intelligible audio; voices come from a **JSON seed**: **`--parler-voice`** (name) and **`--parler-gender`** (`female` / `male`). If you omit **`--parler-voice`**, the seed key defaults from **`--target-lang`** (normalization only—does not add true multilingual TTS). Override with **`--voice`** or **`PLYCAST_PARLER_DESCRIPTION`** (env).

---

## Neural TTS: `parler` (Parler-TTS)

**Important:** The default Parler checkpoint in plycast is **English-trained**. Use **`--target-lang en`** (and English translated text) for speech that sounds correct. Other languages are **not supported** for reliable TTS; the CLI prints a **stderr warning** if you use Parler with a non-English **`--target-lang`**. Seed names like **`vi`** or **`es`** are only **English prompt wording** for style—they do **not** make the model speak Vietnamese or Spanish well.

Install the optional stack (large download on first run for model weights):

```bash
pip install 'plycast[parler]'
```

**ffmpeg** is still recommended for **mp3 / m4a / aiff** (WAV works without it).

**Device:** CUDA is used when available, else Apple **MPS** on macOS, else **CPU**. Override with env **`PLYCAST_PARLER_DEVICE`** (e.g. `cuda:0`, `mps`, `cpu`). Model id: **`PLYCAST_PARLER_MODEL`** (default `parler-tts/parler-tts-mini-v1`).

**Seed file:** `plycast/providers/tts/seeds/parler_voices.json` (also bundled in the wheel). Each **voice name** has a **female** and **male** English Parler description. Override the file path with **`--parler-seed /path/to/parler_voices.json`** or **`PLYCAST_PARLER_SEED`**.

**Seed “language” names** (English description hints for audiobook *style*; **spoken text should still be English**):

| Voice name | Prompt theme (not spoken language) |
|------------|-------------------------------------|
| `en` | General English audiobook (fallback if unknown) |
| `es` | Style hint “Spanish-related” in the English prompt |
| `fr` | French-themed prompt wording |
| `de` | German-themed prompt wording |
| `zh` | Chinese-themed prompt wording |
| `ja` | Japanese-themed prompt wording |
| `ko` | Korean-themed prompt wording |
| `vi` | Vietnamese-themed prompt wording |
| `pt` | Portuguese-themed prompt wording |
| `it` | Italian-themed prompt wording |

**Persona-style names** (same seed; examples):

| Voice name | Notes |
|------------|--------|
| `laura` | Warm expressive audiobook-style |
| `jon` | Parler-style “Jon” delivery (see upstream docs) |
| `gary` | Steady warm narrator |

**Typical CLI** (English output; explicit seed voice + gender):

```bash
plycast ... --tts parler --target-lang en --parler-voice en --parler-gender female
```

**Default seed key from `--target-lang`** (omit **`--parler-voice`**; still use **`en`** for reliable speech):

```bash
plycast ... --tts parler --target-lang en --parler-gender male
```

Omit **`--parler-gender`** to use **`PLYCAST_PARLER_GENDER`** or **`female`**. Set **`--parler-voice`** via **`PLYCAST_PARLER_VOICE`** when you prefer env.

**Custom description:** pass a full English Parler prompt as **`--voice`** (overrides seed and env description):

```bash
plycast ... --tts parler --voice "Jon's voice is monotone yet slightly fast in delivery, with a very close recording that almost has no background noise."
```

See the [Parler-TTS README](https://github.com/huggingface/parler-tts) for prompt tips. Programmatic API: **`parler_voice_description(name, gender)`**, **`parler_seed_voice_names()`**, **`load_parler_voice_seed()`** in **`plycast.providers.tts.parler_voices`** (aliases **`parler_preset_description`** / **`parler_preset_languages`** remain for compatibility).

---

## Linux and Windows: `espeak` / `espeak-ng`

Install **`espeak-ng`** (recommended) or legacy **`espeak`**:

- **Debian/Ubuntu:** `sudo apt install espeak-ng`
- **Fedora:** `sudo dnf install espeak-ng`
- **macOS (optional):** `brew install espeak-ng`
- **Windows:** install [espeak-ng releases](https://github.com/espeak-ng/espeak-ng/releases) and ensure `espeak-ng.exe` is on `PATH`

List available voices:

```bash
espeak-ng --voices
```

Pick a **voice name** from the second column (e.g. `vi`, `cmn`, `en-gb`) and pass it as **`--voice`**:

```bash
plycast ... --tts espeak --voice vi --target-lang vi
```

Test without plycast:

```bash
espeak-ng -v vi "Xin chào."
```

**ffmpeg** is still needed for **mp3 / m4a / aiff** output (WAV works without ffmpeg).

---

## macOS: `say` (`--tts system_say`)

When you use **`--tts system_say`**, plycast calls the macOS **`say`** command. **Voice names depend on your Mac** (macOS version and installed voice packs).

In **Terminal**:

```bash
say -v '?'
```

Use the **first column** as **`--voice`** (e.g. `--voice "Linh"`).

### Filter by language

```bash
say -v '?' | grep -i vi
```

Match the voice to your **`--target-lang`**. Install more voices: **System Settings → Accessibility → Spoken Content → System Voice → Manage Voices**.

### Example macOS voice names (illustrative)

| `--target-lang` | Example voices |
|-----------------|----------------|
| English | `Alex`, `Samantha`, … |
| Vietnamese | `Linh` |
| Chinese | `Ting-Ting`, … |

Always use **`say -v '?'`** on your machine as the source of truth.

---

## Not using speech?

Use **`--tts text_file`** for translated text only, or implement a custom **`TTSProvider`** in Python.

---

## See also

- [QuickStart](QuickStart.md) — `--tts`, `--voice`, `--audio-format`
- `man say` (macOS), `man espeak-ng` (Linux)
