# ─── STANDARD LIBRARY IMPORTS ───────────────────────────────────────
import asyncio
import io
import json
import os
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path
from urllib.parse import urlparse

# ─── THIRD PARTY IMPORTS ────────────────────────────────────────────
from PIL import Image
import typer
import websockets
from rich.console import Console
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn
from rich.theme import Theme
from rich_pixels import Pixels
from rich.panel import Panel

# ─── LOCAL INTERNAL CORE APP IMPORTS ───────────────────────────────
from commitdev.api import get, post
from commitdev.config import get_token

import shutil
from rich.text import Text
from rich.style import Style

# Official CommitDev layout configurations matching your product dashboard theme
commitdev_theme = Theme({
    "brand": "bold spring_green3",   # Signature mint/emerald color
    "success": "spring_green3",
    "meta": "dim grey39",            # Secondary layout dark slate grey text
    "command": "bold white",
    "error": "bold red",
    "warn": "bold yellow"
})

console = Console(theme=commitdev_theme, highlight=False)
app = typer.Typer(help="Manage AI-generated drafts")


# ──────────────────────────────────────────────────────────
# STANDARD CLI COMMAND HANDLERS
# ──────────────────────────────────────────────────────────

@app.command("list")
def list_draft():
    """List all of your CommitDev drafts."""
    console.print("\n[brand]CommitDev[/brand] [meta]•[/meta] Staged Drafts")
    console.print("[meta]──────────────────────────────────────────────────[/meta]")

    with console.status("[meta]Loading active drafts...[/meta]", spinner="simpleDots"):
        try:
            data = get("/cli/drafts/")
        except Exception as e:
            console.print(f"  [error]✕ Request failed:[/error] [meta]{e}[/meta]\n")
            return

    if not data:
        console.print("  [meta]- No active drafts waiting for publication review[/meta]\n")
        return

    for draft_item in data:
        draft_id = draft_item.get('id')
        status = draft_item.get('overall_status', '-').upper()
        platforms = draft_item.get('staged_platforms', [])
        
        platform_str = ", ".join(platforms) if platforms else "None"
        status_style = "success" if status == "APPROVED" else "warn"

        console.print(
            f"  [meta]›[/meta] ID: [white]{draft_id:<4}[/white] "
            f"[meta]│[/meta] Status: [{status_style}]{status:<8}[/{status_style}] "
            f"[meta]│[/meta] Platform: [white]{platform_str}[/white]"
        )

    console.print("[meta]──────────────────────────────────────────────────[/meta]\n")

@app.command("show")
def show_draft(id: int):
    """Show the details of a specific draft."""
    console.print(f"\n[brand]CommitDev[/brand] [meta]•[/meta] Draft Blueprint #{id}")
    console.print("[meta]──────────────────────────────────────────────────[/meta]")

    with console.status(f"[meta]Fetching details for draft #{id}...[/meta]", spinner="simpleDots"):
        try:
            data = get(f"/cli/drafts/{id}/")
        except Exception as e:
            console.print(f"  [error]✕ Fetch failed:[/error] [meta]{e}[/meta]\n")
            return

    status = data.get('overall_status', '-').upper()
    status_style = "success" if status == "APPROVED" else "warn"
    platforms = data.get('staged_platforms', [])
    platform_str = ", ".join(platforms) if platforms else "None"

    console.print(f"  [meta]›[/meta]  ID     [meta]›[/meta] [white]{data.get('id')}[/white]")
    console.print(f"  [meta]›[/meta] State  [meta]›[/meta] [{status_style}]{status}[/{status_style}]")
    console.print(f"  [meta]›[/meta] Platform [meta]›[/meta] {platform_str}")
    console.print("[meta]──────────────────────────────────────────────────[/meta]")
    console.print("[white]Staged Copy Artifact:[/white]\n")
    console.print(data.get("generated_post", "[meta]No generated content body available.[/meta]"))
    console.print("[meta]──────────────────────────────────────────────────[/meta]\n")


@app.command("approve")
def approve_draft(id: int):
    """Approve a draft for publishing."""
    console.print(f"\n[brand]CommitDev[/brand] [meta]•[/meta] Publication Approval")
    console.print("[meta]──────────────────────────────────────────────────[/meta]")

    with console.status(f"[meta]Transmitting approval declaration flag for node #{id}...[/meta]", spinner="simpleDots"):
        try:
            data = post(f"/cli/drafts/{id}/approve/")
            console.print(f"  [success]✓[/success] Draft node [white]#{data.get('draft_id')}[/white] locked into deployment sequence successfully.\n")
        except Exception as e:
            console.print(f"  [error]✕ Authorization payload dropped:[/error] [meta]{e}[/meta]\n")

@app.command("regenerate")
def regenerate_draft(id: int):
    """Generate a new version of an existing draft."""
    console.print(f"\n[brand]CommitDev[/brand] [meta]•[/meta] AI Reconstruction Loop")
    console.print("[meta]──────────────────────────────────────────────────[/meta]")

    with console.status(f"[meta]Re-evaluating workspace context trees for node #{id}...[/meta]", spinner="simpleDots"):
        try:
            data = post(f"/cli/drafts/{id}/regenerate/")
            console.print(f"  [success]✓[/success] {data.get('message')}\n")
        except Exception as e:
            console.print(f"  [error]✕ Model context rewrite failed:[/error] [meta]{e}[/meta]\n")



#Note: Add a new command NAMED: edit_draft for editing draft