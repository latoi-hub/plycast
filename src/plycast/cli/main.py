"""
Typer CLI: thin wrapper over :mod:`plycast.pipeline.convert`.

Commands map to ``convert_book``, ``translate_book``, ``synthesize_book``, ``inspect_book``.
"""

from __future__ import annotations

from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.console import Console

from plycast.pipeline.convert import (
    convert_book,
    inspect_book,
    result_to_json,
    synthesize_book,
    translate_book,
)
from plycast.pipeline.wiring import default_tts_backend

app = typer.Typer(
    name="plycast",
    no_args_is_help=True,
    help="Ingest text/PDF/docx/images, translate, and synthesize audio. "
    "Same behavior as ``from plycast import convert_book``.",
)
console = Console(stderr=True)


@app.command("convert")
def cmd_convert(
    input_path: Annotated[Path, typer.Argument(help="Input file path")],
    source_lang: Annotated[str, typer.Option("--source-lang", "-s", help="Source language code")],
    target_lang: Annotated[str, typer.Option("--target-lang", "-t", help="Target language code")],
    output_dir: Annotated[Path, typer.Option("--output-dir", "-o", help="Output directory")] = Path(
        "dist"
    ),
    translator: Annotated[
        str,
        typer.Option(help="identity | libretranslate | llm"),
    ] = "libretranslate",
    base_url: Annotated[Optional[str], typer.Option(help="LibreTranslate or LLM API base URL")] = None,
    api_key: Annotated[Optional[str], typer.Option(help="API key when required")] = None,
    llm_model: Annotated[str, typer.Option(help="With --translator llm")] = "gpt-4o-mini",
    llm_provider: Annotated[
        Optional[str],
        typer.Option(help="openai | anthropic (else inferred from model)"),
    ] = None,
    tts: Annotated[
        Optional[str],
        typer.Option(help="system_say | espeak | parler | text_file (default: platform)"),
    ] = None,
    voice: Annotated[Optional[str], typer.Option(help="Voice / Parler raw description")] = None,
    parler_voice: Annotated[Optional[str], typer.Option(help="Parler seed voice name")] = None,
    parler_seed: Annotated[Optional[Path], typer.Option(help="Custom parler_voices.json")] = None,
    parler_gender: Annotated[
        Optional[str],
        typer.Option(help="female | male (Parler seed)"),
    ] = None,
    max_chunk_chars: Annotated[int, typer.Option(help="Translation chunk size")] = 1500,
    audio_format: Annotated[str, typer.Option(help="mp3 | wav | aiff | m4a")] = "mp3",
    json_out: Annotated[bool, typer.Option("--json", help="Print machine-readable JSON")] = False,
) -> None:
    """Read → translate → TTS (full pipeline)."""
    r = convert_book(
        input_path,
        source_lang=source_lang,
        target_lang=target_lang,
        output_dir=output_dir,
        translator=translator,
        base_url=base_url,
        api_key=api_key,
        llm_model=llm_model,
        llm_provider=llm_provider,
        tts=tts,
        voice=voice,
        parler_voice=parler_voice,
        parler_gender=parler_gender,
        parler_seed=str(parler_seed) if parler_seed else None,
        max_chunk_chars=max_chunk_chars,
        audio_format=audio_format,
    )
    if json_out:
        typer.echo(result_to_json(r))
    else:
        console.print(f"[green]Translated text:[/green] {r.translated_text_path}")
        console.print(f"[green]Audio file:[/green] {r.audio_path}")


@app.command("translate")
def cmd_translate(
    input_path: Annotated[Path, typer.Argument(help="Input file path")],
    source_lang: Annotated[str, typer.Option("--source-lang", "-s")],
    target_lang: Annotated[str, typer.Option("--target-lang", "-t")],
    output_dir: Annotated[Path, typer.Option("--output-dir", "-o")] = Path("dist"),
    translator: Annotated[str, typer.Option()] = "libretranslate",
    base_url: Annotated[Optional[str], typer.Option()] = None,
    api_key: Annotated[Optional[str], typer.Option()] = None,
    llm_model: Annotated[str, typer.Option()] = "gpt-4o-mini",
    llm_provider: Annotated[Optional[str], typer.Option()] = None,
    max_chunk_chars: Annotated[int, typer.Option()] = 1500,
    json_out: Annotated[bool, typer.Option("--json")] = False,
) -> None:
    """Read → translate only (writes ``<stem>.<target>.txt``)."""
    r = translate_book(
        input_path,
        source_lang=source_lang,
        target_lang=target_lang,
        output_dir=output_dir,
        translator=translator,
        base_url=base_url,
        api_key=api_key,
        llm_model=llm_model,
        llm_provider=llm_provider,
        max_chunk_chars=max_chunk_chars,
    )
    if json_out:
        typer.echo(result_to_json(r))
    else:
        console.print(f"[green]Translated text:[/green] {r.translated_text_path}")


@app.command("tts")
def cmd_tts(
    input_path: Annotated[Path, typer.Argument(help="Input file path")],
    tts_lang: Annotated[str, typer.Option("--lang", "-l", help="Language of text to speak")],
    output_dir: Annotated[Path, typer.Option("--output-dir", "-o")] = Path("dist"),
    tts: Annotated[Optional[str], typer.Option(help="system_say | espeak | parler | text_file")] = None,
    voice: Annotated[Optional[str], typer.Option()] = None,
    parler_voice: Annotated[Optional[str], typer.Option()] = None,
    parler_seed: Annotated[Optional[Path], typer.Option()] = None,
    parler_gender: Annotated[Optional[str], typer.Option()] = None,
    audio_format: Annotated[str, typer.Option()] = "mp3",
    json_out: Annotated[bool, typer.Option("--json")] = False,
) -> None:
    """Read → TTS only (no translation)."""
    backend = tts if tts is not None else default_tts_backend()
    r = synthesize_book(
        input_path,
        tts_language=tts_lang,
        output_dir=output_dir,
        tts=backend,
        voice=voice,
        parler_voice=parler_voice,
        parler_gender=parler_gender,
        parler_seed=str(parler_seed) if parler_seed else None,
        audio_format=audio_format,
    )
    if json_out:
        typer.echo(result_to_json(r))
    else:
        console.print(f"[green]Audio file:[/green] {r.audio_path}")


@app.command("inspect")
def cmd_inspect(
    input_path: Annotated[Path, typer.Argument(help="Input file path")],
    source_lang: Annotated[Optional[str], typer.Option("--source-lang", "-s")] = None,
    preview_chars: Annotated[int, typer.Option(help="Max preview characters")] = 240,
    json_out: Annotated[bool, typer.Option("--json")] = False,
) -> None:
    """Show format, size, and optional text preview (debugging)."""
    r = inspect_book(input_path, source_language=source_lang, preview_chars=preview_chars)
    if json_out:
        typer.echo(result_to_json(r))
    else:
        console.print(f"[cyan]path[/cyan]       {r.path}")
        console.print(f"[cyan]suffix[/cyan]     {r.suffix}")
        console.print(f"[cyan]size[/cyan]       {r.size_bytes} bytes")
        console.print(f"[cyan]chars[/cyan]      {r.text_char_count}")
        if r.preview:
            console.print(f"[cyan]preview[/cyan]\n{r.preview}")


def main() -> None:
    app()


if __name__ == "__main__":
    main()
