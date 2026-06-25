#!/usr/bin/env python3
"""
OSINT Username Checker
Cek keberadaan username di 100+ platform secara paralel
"""

import asyncio
import json
import sys
import time
from datetime import datetime
from pathlib import Path

import httpx
import typer
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.progress import BarColumn, MofNCompleteColumn, Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich import print as rprint

from osint.checker import UsernameChecker
from osint.reporter import generate_html_report

app = typer.Typer(
    name="osint-checker",
    help="[bold green]OSINT Username Checker[/bold green] — cek username di 100+ platform",
    add_completion=False,
)
console = Console()


@app.command()
def check(
    username: str = typer.Argument(..., help="Username yang mau dicek"),
    output: str = typer.Option(None, "--output", "-o", help="Simpan hasil ke file JSON"),
    report: bool = typer.Option(False, "--report", "-r", help="Generate HTML report"),
    timeout: int = typer.Option(10, "--timeout", "-t", help="Timeout per request (detik)"),
    concurrency: int = typer.Option(50, "--concurrency", "-c", help="Jumlah request paralel"),
    only_found: bool = typer.Option(False, "--only-found", "-f", help="Tampilkan hanya yang ditemukan"),
):
    """Cek keberadaan [USERNAME] di berbagai platform sosial media & developer tools."""
    asyncio.run(
        _run_check(username, output, report, timeout, concurrency, only_found)
    )


async def _run_check(username, output, report, timeout, concurrency, only_found):
    console.print()
    console.print(Panel(
        f"[bold cyan]Target:[/bold cyan] [yellow]{username}[/yellow]\n"
        f"[bold cyan]Concurrency:[/bold cyan] {concurrency}  "
        f"[bold cyan]Timeout:[/bold cyan] {timeout}s",
        title="[bold green]🔍 OSINT Username Checker[/bold green]",
        border_style="green",
    ))
    console.print()

    checker = UsernameChecker(timeout=timeout, concurrency=concurrency)

    start_time = time.time()
    results = []

    progress = Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        MofNCompleteColumn(),
        TextColumn("[cyan]{task.fields[found]} found"),
        console=console,
    )

    with progress:
        task = progress.add_task(
            f"[green]Scanning {len(checker.platforms)} platforms...",
            total=len(checker.platforms),
            found=0,
        )

        async for result in checker.check_all(username):
            results.append(result)
            found_count = sum(1 for r in results if r["found"])
            progress.update(task, advance=1, found=found_count)

    elapsed = time.time() - start_time
    found = [r for r in results if r["found"]]
    not_found = [r for r in results if not r["found"] and not r.get("error")]
    errors = [r for r in results if r.get("error")]

    # Summary table
    console.print()
    _print_summary(found, not_found, errors, elapsed, only_found)

    # Save JSON
    if output:
        out_path = Path(output)
        out_path.write_text(json.dumps({
            "username": username,
            "scanned_at": datetime.now().isoformat(),
            "elapsed_seconds": round(elapsed, 2),
            "stats": {
                "total": len(results),
                "found": len(found),
                "not_found": len(not_found),
                "errors": len(errors),
            },
            "results": results,
        }, indent=2))
        console.print(f"\n[green]✓[/green] JSON disimpan ke [cyan]{output}[/cyan]")

    # Generate HTML report
    if report:
        report_path = f"report_{username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        generate_html_report(username, results, report_path)
        console.print(f"[green]✓[/green] HTML report: [cyan]{report_path}[/cyan]")

    console.print(
        f"\n[dim]Selesai dalam {elapsed:.2f}s — "
        f"[green]{len(found)} ditemukan[/green] dari {len(results)} platform[/dim]\n"
    )


def _print_summary(found, not_found, errors, elapsed, only_found):
    if found:
        table = Table(
            title=f"[bold green]✓ Ditemukan ({len(found)} platform)[/bold green]",
            border_style="green",
            show_lines=False,
        )
        table.add_column("Platform", style="bold cyan", min_width=20)
        table.add_column("URL", style="blue underline")
        table.add_column("Status", justify="center")

        for r in sorted(found, key=lambda x: x["platform"]):
            table.add_row(r["platform"], r["url"], "[green]✓ Found[/green]")

        console.print(table)

    if not only_found and not_found:
        console.print(
            f"\n[dim]Tidak ditemukan di {len(not_found)} platform. "
            f"Gunakan --only-found untuk sembunyikan.[/dim]"
        )

    if errors:
        console.print(f"[yellow]⚠ {len(errors)} platform gagal dicek (timeout/error)[/yellow]")


@app.command()
def platforms():
    """List semua platform yang didukung."""
    from osint.platforms import PLATFORMS
    table = Table(title="Platform yang Didukung", border_style="cyan")
    table.add_column("No", justify="right", style="dim")
    table.add_column("Platform", style="bold")
    table.add_column("Category", style="cyan")
    table.add_column("URL Pattern")

    for i, (name, data) in enumerate(sorted(PLATFORMS.items()), 1):
        table.add_row(str(i), name, data.get("category", "-"), data["url"].replace("{}", "[yellow]USERNAME[/yellow]"))

    console.print(table)
    console.print(f"\n[dim]Total: {len(PLATFORMS)} platforms[/dim]\n")


if __name__ == "__main__":
    app()
