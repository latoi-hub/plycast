# TTS voices (`--tts`, `--voice`)

plycast supports:

| `--tts` | Platform | Engine |
|---------|----------|--------|
| **`system_say`** (default on **macOS**) | macOS | Built-in **`say`** |
| **`espeak`** (default on **Linux** / non-macOS) | Linux, Windows, macOS | **`espeak-ng`** or **`espeak`** on `PATH` |
| **`text_file`** | Any | No audio; writes a text artifact |

Use **`--voice`** with **`system_say`** (macOS voice name) or **`espeak`** (espeak `-v` voice). If you omit **`--voice`**, espeak picks a voice from **`--target-lang`** (e.g. `vi` → Vietnamese, `zh` → Mandarin `cmn`).

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
