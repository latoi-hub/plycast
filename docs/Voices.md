# macOS `say` voices (`--voice`)

When you use **`--tts system_say`**, plycast calls the macOS **`say`** command. **Voice names and languages depend on your Mac** (macOS version and which voice packs are installed). plycast does not ship a fixed list.

---

## Not using macOS? (Linux, Windows, cloud)

**`system_say` only works on macOS** (the `say` binary). On **Linux** or **Windows**, the default **`--tts system_say`** will fail when the pipeline tries to run `say`.

**What to use instead:**

| Goal | What to do |
|------|------------|
| **Get translated text only** (no audio) | **`--tts text_file`**. You still get `dist/<stem>.<target>.txt`; the “audio” step writes a small text placeholder instead of sound. |
| **Produce real audio on your OS** | Take the **translated `.txt`** from `dist/` and feed it to another tool: e.g. **espeak-ng**, **Piper**, **Coqui**, cloud TTS, or a screen reader — not built into plycast’s CLI today. |
| **Integrate in Python** | Implement **`TTSProvider`** (see `plycast.providers.base`) with your engine, then **`PlycastPipeline(..., tts=YourTTS())`**. |

So: **ingest + translate** is cross-platform; **built-in speech synthesis** in this repo is currently **macOS `say` only**. The rest of this page applies only if you run plycast on a Mac.

---

## List voices on your machine (macOS)

In **Terminal**, run:

```bash
say -v '?'
```

Each line is typically:

`VoiceName    locale    # sample phrase`

Examples of output shape (yours will differ):

```text
Alex                en_US    # Most people recognize me by my voice.
Samantha            en_US    # Hello! My name is Samantha.
Linh                vi_VN    # Xin chào, tôi tên là Linh.
```

Use the **first column** as **`--voice`** (e.g. `--voice "Linh"`).

### Filter by language or locale

```bash
say -v '?' | grep -i vi      # Vietnamese
say -v '?' | grep -i zh      # Chinese
say -v '?' | grep -i en      # English
say -v '?' | grep -i ja      # Japanese
```

Match the voice to your **`--target-lang`** (and the script of the translated text). A mismatched voice may mispronounce or spell out characters.

---

## Map `target-lang` to a voice (workflow)

1. Translate to your target language (e.g. **`--target-lang vi`**).
2. Pick a voice whose **locale** fits that language (e.g. `vi_VN`).
3. Pass **`--voice "VoiceName"`** from the first column of `say -v '?'`.

There is no separate “language” flag for `say` in plycast beyond choosing the voice; the **`language`** field on the TTS layer is reserved for future use and does not change `say` today.

---

## Example voice names (illustrative only)

These **may or may not exist** on your Mac—always use **`say -v '?'`** as the source of truth.

| Target language (typical `--target-lang`) | Example voice names (if installed) | Notes |
|-------------------------------------------|-------------------------------------|--------|
| English (`en`) | `Alex`, `Samantha`, `Victoria`, … | Many `en_US`, `en_GB`, `en_AU`, … |
| Vietnamese (`vi`) | `Linh` | Often `vi_VN` |
| Chinese (`zh`) | `Ting-Ting`, `Sin-Ji`, … | Simplified vs traditional locales differ |
| Japanese (`ja`) | `Kyoko`, `Otoya`, … | |
| Spanish (`es`) | `Jorge`, `Monica`, `Paulina`, … | |
| French (`fr`) | `Thomas`, `Amelie`, `Daniel`, … | |
| German (`de`) | `Anna`, `Markus`, … | |

Install extra voices: **System Settings → Accessibility → Spoken Content → System Voice → Manage Voices** (wording varies by macOS version).

---

## CLI examples

```bash
plycast ... --tts system_say --voice "Samantha"
plycast ... --tts system_say --voice "Linh"
```

Test a voice without plycast:

```bash
say -v "Linh" "Xin chào."
```

---

## See also

- [QuickStart](QuickStart.md) — `--tts`, `--voice`, `--audio-format`
- `man say` on macOS
