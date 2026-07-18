
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

# Initialize Typer App CLI Router
app = typer.Typer(help="CommitDev CLI Drafts Controller Management Console")


# ──────────────────────────────────────────────────────────
# STANDARD CLI COMMAND HANDLERS
# ──────────────────────────────────────────────────────────


def drafts():
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

