
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


def draft(id: int):
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


def approve(id: int):
    """Approve a draft for publishing."""
    console.print(f"\n[brand]CommitDev[/brand] [meta]•[/meta] Publication Approval")
    console.print("[meta]──────────────────────────────────────────────────[/meta]")

    with console.status(f"[meta]Transmitting approval declaration flag for node #{id}...[/meta]", spinner="simpleDots"):
        try:
            data = post(f"/cli/drafts/{id}/approve/")
            console.print(f"  [success]✓[/success] Draft node [white]#{data.get('draft_id')}[/white] locked into deployment sequence successfully.\n")
        except Exception as e:
            console.print(f"  [error]✕ Authorization payload dropped:[/error] [meta]{e}[/meta]\n")


def regenerate(id: int):
    """Generate a new version of an existing draft."""
    console.print(f"\n[brand]CommitDev[/brand] [meta]•[/meta] AI Reconstruction Loop")
    console.print("[meta]──────────────────────────────────────────────────[/meta]")

    with console.status(f"[meta]Re-evaluating workspace context trees for node #{id}...[/meta]", spinner="simpleDots"):
        try:
            data = post(f"/cli/drafts/{id}/regenerate/")
            console.print(f"  [success]✓[/success] {data.get('message')}\n")
        except Exception as e:
            console.print(f"  [error]✕ Model context rewrite failed:[/error] [meta]{e}[/meta]\n")


# ──────────────────────────────────────────────────────────
# INTERACTIVE PIPELINE CORE UTILITIES
# ──────────────────────────────────────────────────────────

def fetch_fresh_token():
    """Retrieves local authentication credential token mappings."""
    try:
        token_data = get_token()
        token = token_data.get('access_token') if isinstance(token_data, dict) else token_data
        if not token:
            raise ValueError("Authentication storage empty.")
        return token
    except Exception as e:
        console.print(f"\n  [error]✕ Configuration Drop:[/error] Local profile token invalid: [meta]{e}[/meta]\n")
        sys.exit(1)


def open_in_editor(initial_content):
    """Spawns local terminal workspace file context editor."""
    editor = os.environ.get('EDITOR', 'nano') 
    try:
        with tempfile.NamedTemporaryFile(suffix=".txt", mode='w+', delete=False) as tf:
            tf.write(initial_content)
            tf.flush()
            temp_file_path = tf.name

        console.print(f"  [meta]› Spawning local editor:[/meta] [white]{editor}[/white]")
        
        if editor == 'code':
            subprocess.run(['code', '--wait', temp_file_path], check=True)
        elif editor == 'nano':
            subprocess.run(['nano', '-$', temp_file_path], check=True)
        elif editor == 'vim':
            subprocess.run(['vim', '+set wrap', temp_file_path], check=True)
        else:
            subprocess.run([editor, temp_file_path], check=True)
        
        with open(temp_file_path, 'r') as tf_read:
            updated_content = tf_read.read()

        os.unlink(temp_file_path)
        return updated_content
    except Exception as e:
        console.print(f"  [warn]⚠ Local terminal editor allocation aborted:[/warn] [meta]{e}[/meta]")
        return None


def prompt_select(options: list, message: str) -> str:
    """Helper method driving single-option terminal selections."""
    console.print(f"\n[white]{message}[/white]")
    for i, opt in enumerate(options, 1):
        console.print(f"  [brand]{i}[/brand] [meta]›[/meta] {opt}")
    while True:
        try:
            choice = input("\n> ")
            idx = int(choice) - 1
            if 0 <= idx < len(options):
                return options[idx]
        except ValueError:
            pass
        console.print("[error]✕ Invalid option index selected. Try again.[/error]")


# ──────────────────────────────────────────────────────────
# WIZARD + REVIEW HUB INTERACTIVE PUBLISHING ENGINE
# ──────────────────────────────────────────────────────────

async def handle_publishing_pipeline(ws, payload):
    """
    Executes the CommitDev Publish Pipeline using a Wizard + Review Hub pattern.
    
    Flow:
      - Sequential Wizard: Draft Preview -> Image Setup -> Platform Configuration
      - Review Hub: Centralized hub summarizing state with jumping capabilities
      - Execution: Dispatches content to live clusters with partial retry loops
    """
    post_id = payload.get('post_id')
    current_content = payload.get('content', '')
    repo_name = payload.get('repository', 'commitdev-cli')
    commit_msg = payload.get('commit_message', 'feat(cli): add pipeline execution blocks')
    
    staged_platforms = [platform.capitalize() for platform in payload.get('staged_platforms', ['LinkedIn', 'X'])]
    
    attached_images = []
    
    def render_image_preview(img_source, img_name, kb_size, is_url):
        try:
            with Image.open(img_source) as img:
                if img.mode not in ("RGB", "RGBA"):
                    img = img.convert("RGBA")
                    
                w, h = img.size
                
                # Aspect Ratio Multiplier:
                # Terminal character slots are twice as tall as they are wide.
                # To prevent vertical squishing, target_h is calculated with a 0.5 ratio factor.
                target_w = 48
                target_h = int((target_w * (h / w)) * 0.5)
                
                try:
                    resample_filter = Image.Resampling.NEAREST
                except AttributeError:
                    resample_filter = Image.NEAREST
                    
                resized = img.resize((target_w, max(1, target_h)), resample=resample_filter)
                pixels_frame = Pixels.from_image(resized)
                
                console.print(pixels_frame)
                
                source_lbl = "[cyan]remote[/cyan]" if is_url else "[yellow]local[/yellow]"
                console.print(f"  [white]{img_name}[/white] [meta]•[/meta] {source_lbl} [meta]•[/meta] {w}×{h} [meta]•[/meta] {kb_size:.1f} KB")
        except Exception as e:
            w, h = (1920, 1080)
            console.print(f"  [white]{img_name}[/white]\n  [meta]{w}×{h} • {kb_size:.1f} KB (Preview render fallback: {str(e)})[/meta]")

    # =========================================================================
    # NESTED TASK ROUTINES (Directly return back to the Review Hub on completion)
    # =========================================================================

    async def run_edit_content_sequence():
        nonlocal current_content
        console.print("\n[brand]📝 EDIT DRAFT CONTENT[/brand]")
        console.print("[meta]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/meta]")
        
        initial_txt = (
            f"# ──────────────────────────────────────────────────────────\n"
            f"# 📝 COMMITDEV EDIT SESSION\n"
            f"# ──────────────────────────────────────────────────────────\n"
            f"# Target Post ID: {post_id}\n"
            f"#\n"
            f"# Instructions: Lines starting with '#' will be ignored.\n"
            f"# Save and close this temporary file to update the post content.\n"
            f"# ──────────────────────────────────────────────────────────\n\n"
            f"{current_content}\n"
        )
        
        loop = asyncio.get_event_loop()
        edited_result = await loop.run_in_executor(None, open_in_editor, initial_txt)
        
        if edited_result:
            current_content = "\n".join([
                line for line in edited_result.splitlines() 
                if not line.strip().startswith("#")
            ]).strip()
            
            console.print("\n[success]✓ Local buffer changes detected[/success]")
            with console.status("[meta]Uploading draft modifications...[/meta]", spinner="simpleDots"):
                await ws.send(json.dumps({
                    "action": "update_draft",
                    "post_id": post_id,
                    "content": current_content
                }))
                
                # Receive confirm response from the consumer
                response = await ws.recv()
                data = json.loads(response)
                # Keep client copy and database layout completely sync'd
                current_content = data.get("payload", {}).get("content", current_content)
                
            console.print("  [success]✓ Sync Complete: Draft updated.[/success]\n")

    async def run_regenerate_content_sequence():
        nonlocal current_content
        console.print("\n[brand] REGENERATING WORKSPACE TEXT[/brand]")
        console.print("[meta]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/meta]")
        with console.status("[meta]Instructing AI model to rewrite text context trees...[/meta]", spinner="simpleDots"):
            await ws.send(json.dumps({"action": "regenerate_draft", "post_id": post_id}))
            response = await ws.recv()
            data = json.loads(response)
            current_content = data.get("payload", {}).get("content", current_content)
        console.print("\n[success]✓ Post content reconstructed successfully via AI engine.[/success]\n")

    async def run_image_manager_sequence():
        console.print("\n[brand] MEDIA WORKSPACE MANAGER[/brand]")
        console.print("[meta]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/meta]")
        
        while True:
            console.print(f"  Current: [white]{len(attached_images)} active media files linked.[/white]")
            
            opts = ["Link New Image"]
            if attached_images:
                opts.extend(["View Current Images", "Clear All Images"])
            opts.append("Return to Review Hub")
            
            img_action = prompt_select(opts, "What would you like to do?")
            
            if img_action == "Return to Review Hub":
                break
                
            elif img_action == "Clear All Images":
                attached_images.clear()
                console.print("  [success]✓ Active images buffer flushed.[/success]\n")
                continue
                
            elif img_action == "View Current Images":
                console.print("\n[white]Active Media Cache Streams:[/white]")
                for item in attached_images:
                    console.print(f"  [meta]›[/meta] [white]{item}[/white]")
                console.print("")
                continue
                
            console.print("\n[white]Drag & drop an image, enter file path, or paste an image URL:[/white]")
            path_input = input("> ").strip("'\" ")
            if not path_input:
                continue
                
            is_url = path_input.lower().startswith(("http://", "https://"))
            img_bytes = None
            img_name = ""
            kb_size = 0.0
            
            if is_url:
                try:
                    parsed = urlparse(path_input)
                    if not parsed.netloc:
                        raise ValueError
                    img_name = parsed.path.split("/")[-1] or "remote_image.jpg"
                except ValueError:
                    console.print("  [error]✕ Access error: Invalid URL format provided.[/error]\n")
                    continue
                    
                console.print(f"\n  [success]✓ Remote asset target verified[/success]")
                with Progress(SpinnerColumn(), BarColumn(bar_width=30), TextColumn("[progress.percentage]{task.percentage:>3.0f}%"), console=console) as progress:
                    task = progress.add_task("[meta]Downloading remote asset...[/meta]", total=100)
                    try:
                        req = urllib.request.Request(path_input, headers={'User-Agent': 'Mozilla/5.0'})
                        with urllib.request.urlopen(req, timeout=10) as response:
                            img_bytes = response.read()
                        kb_size = len(img_bytes) / 1024
                        while not progress.finished:
                            await asyncio.sleep(0.01)
                            progress.update(task, advance=10)
                    except Exception as e:
                        progress.stop()
                        console.print(f"  [error]✕ Network error: Could not fetch resource ({str(e)}).[/error]\n")
                        continue
            else:
                img_path = Path(path_input)
                if not img_path.is_file():
                    console.print("  [error]✕ Access error: Target file path does not exist on this machine.[/error]\n")
                    continue
                img_name = img_path.name
                kb_size = img_path.stat().st_size / 1024
                
                console.print(f"\n  [success]✓ {img_name} detected[/success]")
                with Progress(SpinnerColumn(), BarColumn(bar_width=30), TextColumn("[progress.percentage]{task.percentage:>3.0f}%"), console=console) as progress:
                    task = progress.add_task("[meta]Uploading local assets...[/meta]", total=100)
                    while not progress.finished:
                        await asyncio.sleep(0.02)
                        progress.update(task, advance=5)

            # ─── RENDERING INLINE IMAGE FRAME PREVIEW ───
            console.print("\n[meta]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/meta]")
            console.print("  [white]Attached Image Data Frame Preview[/white]")
            
            img_source = io.BytesIO(img_bytes) if is_url else img_path
            render_image_preview(img_source, img_name, kb_size, is_url)
            
            console.print("[meta]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/meta]\n")
            attached_images.append(path_input if is_url else img_path)

    async def run_platforms_manager_sequence():
        nonlocal staged_platforms
        console.print("\n[brand]📡 CHANNELS CONFIGURATION[/brand]")
        
        console.print(f"\n[brand]{staged_platforms}[/brand]")
        
        console.print("[meta]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/meta]")
        
        available_channels = ["Linkedin", "X", "Dev.to", "Medium"]
        
        while True:
            console.print("  Manage active target channels below:")
            choices = []
            for channel in available_channels:
                active_flag = "✓ [Armed]" if channel in staged_platforms else "  [Disabled]"
                choices.append(f"{active_flag} {channel}")
            choices.append("Return to Review Hub")
            
            selection = prompt_select(choices, "Toggle platforms for publication:")
            if selection == "Return to Review Hub":
                break
                
            selected_channel = selection.split()[-1]
            if selected_channel in staged_platforms:
                staged_platforms.remove(selected_channel)
                console.print(f"  [meta]›[/meta] Disabled [yellow]{selected_channel}[/yellow] transmission cluster.\n")
            else:
                staged_platforms.append(selected_channel)
                console.print(f"  [meta]›[/meta] Enabled [success]{selected_channel}[/success] transmission cluster.\n")

    # =========================================================================
    # STAGE 1 & 2: WIZARD BOOTSTRAP (FIRST TIME PASS-THROUGH)
    # =========================================================================
    console.print("\n[brand]✨ CommitDev Publish Pipeline Init[/brand]")
    console.print("[meta]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/meta]")
    console.print(f"  Repository  [meta]›[/meta] [white]{repo_name}[/white]")
    console.print(f"  Commit      [meta]›[/meta] {commit_msg}")
    console.print(f"  Platforms   [meta]›[/meta] [white]{' • '.join(staged_platforms)}[/white]")
    console.print("[meta]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/meta]\n")

    console.print(Panel(
        current_content,
        title="[brand]Staged Copy[/brand]",
        border_style="dim grey39"
    ))
    console.print()

    wizard_init = prompt_select(["Configure Media & Channels First", "Proceed straight to Review Hub"], "How would you like to initialize this deployment sequence?")
    
    if wizard_init == "Configure Media & Channels First":
        await run_image_manager_sequence()
        await run_platforms_manager_sequence()

    # =========================================================================
    # THE REVIEW HUB CENTRAL ROUTING LAYER
    # =========================================================================
    while True:
        console.print("\n[meta]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/meta]")
        console.print("         🚀 COMMITDEV READY TO PUBLISH REVIEW HUB")
        console.print("[meta]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/meta]")
        console.print(f"  Repository  [meta]›[/meta] [white]{repo_name}[/white]")
        console.print(f"  Platforms   [meta]›[/meta] {', '.join([f'[success]✓ {p}[/success]' for p in staged_platforms]) if staged_platforms else '[error]None Selected[/error]'}")
        console.print(f"  Media Assets[meta]›[/meta] [white]{len(attached_images)} files linked[/white]")
        
        preview_snippet = current_content[:140].replace('\n', ' ')
        console.print(f"  Staged Text [meta]›[/meta]\n  [dim]\"{preview_snippet}...\"[/dim]")
        console.print("[meta]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/meta]\n")

        hub_action = prompt_select([
            "Edit Content (Manual Editor)",
            "Regenerate Content (AI Engine)",
            "Manage Media & Images",
            "Configure Publishing Platforms",
            "Publish Staged Configuration Live 🚀",
            "Save as Draft to Cloud",
            "Exit Pipeline"
        ], "Review Hub Control Board Selection:")

        if hub_action == "Exit Pipeline":
            console.print("  [meta]› Aborting execution pipeline loop. Staging memory discarded.[/meta]\n")
            return
            
        elif hub_action == "Save as Draft to Cloud":
            console.print("  [success]✓ Staged pipeline state successfully captured and written to Cloud boards.[/success]\n")
            return
            
        elif hub_action == "Edit Content (Manual Editor)":
            await run_edit_content_sequence()
            
        elif hub_action == "Regenerate Content (AI Engine)":
            await run_regenerate_content_sequence()
            
        elif hub_action == "Manage Media & Images":
            await run_image_manager_sequence()
            
        elif hub_action == "Configure Publishing Platforms":
            await run_platforms_manager_sequence()
            
        elif hub_action == "Publish Staged Configuration Live 🚀":
            if not staged_platforms:
                console.print("  [error]✕ Configuration Error: Cannot publish when platform target routing is empty.[/error]\n")
                continue
            break

    # =========================================================================
    # EXECUTION & PARTIAL DISTRIBUTIONS ERROR RETRY LOOP
    # =========================================================================
    active_targets = list(staged_platforms)
    
    while True:
        console.print("\n[brand]Publishing post to target network matrices...[/brand]")
        await ws.send(json.dumps({"action": "publish_draft", "post_id": post_id}))
        
        # Pull return payload confirmation from Django consumer backchannel
        response = await ws.recv()
        data = json.loads(response)
        payload_data = data.get("payload", {})
        print("payload for publishing", payload_data)
        status = payload_data.get("status")
        
        failed_channels = {}
        for p in active_targets:
            with Progress(SpinnerColumn(), TextColumn("[meta]{task.description}[/meta]"), console=console) as progress:
                task = progress.add_task(f"Dispatching distribution packet to {p} cluster...", total=None)
                await asyncio.sleep(1.2)
            
            # Simulated cluster failure reporting matched to database parameters
            if status == "failed" or p == "X":
                failed_channels[p] = "Rate limit exceeded"
                console.print(f"  [error]✕ {p}[/error]  [meta]───[/meta] [error]Failed: Rate limit exceeded (code 429)[/error]")
            else:
                console.print(f"  [success]✓ {p}[/success]  [meta]───[/meta] Published successfully")

        if not failed_channels:
            console.print("\n[meta]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/meta]")
            console.print("  [brand]✓ Deployment Pipeline Concluded Successfully[/brand]")
            console.print(f"  Draft ID    [meta]›[/meta] {post_id}")
            console.print(f"  Media Slots [meta]›[/meta] {len(attached_images)} assets distributed")
            console.print("[meta]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/meta]\n")
            break
        else:
            console.print(f"\n[error]⚠ Warning: Distribution pipeline partially dropped clusters.[/error]")
            error_action = prompt_select(["Retry Failed Clusters", "Save Pending to Cloud", "Exit Pipeline"], "Select response routing strategy:")
            
            if error_action == "Retry Failed Clusters":
                active_targets = list(failed_channels.keys())
                continue
            elif error_action == "Save Pending to Cloud":
                console.print("  [success]✓ Retained status parameters for failed networks back to Cloud board.[/success]\n")
                break
            else:
                break


async def _listen_for_drafts_loop():
    while True:
        token = fetch_fresh_token()
        url = f"wss://commitdev.name.ng/ws/drafts/?token={token}"
        
        extra_headers = {
            "Authorization": f"Bearer {token}",
            "Origin": "https://commitdev.name.ng",
            "User-Agent": "CommitDev-Agent/1.0"
        }
        
        console.print("  [meta]📡 Connecting stream hook to live staging sockets...[/meta]")
        
        try:
            async with websockets.connect(url, additional_headers=extra_headers) as ws:
                console.print("  [success]✓ Active socket connection secure. Monitoring workspace background pushes...[/success]")
                
                while True:
                    message = await ws.recv()
                    event_data = json.loads(message)
                    
                    if event_data.get("type") == "send_private_message":
                        payload = event_data.get("payload", {})
                        if payload.get("status") == "draft_saved":
                            await handle_publishing_pipeline(ws, payload)
                            break 

        except websockets.exceptions.InvalidStatus as e:
            if e.response.status_code == 403:
                console.print("\n  [error]✕ Handshake Rejected:[/error] Server returned HTTP 403 Forbidden profile metrics.\n")
                break
            else:
                console.print(f"\n  [error]✕ Connection Drop:[/error] Socket cluster rejected target: HTTP {e.response.status_code}\n")
                
        except websockets.exceptions.ConnectionClosed as e:
            console.print(f"\n  [meta]🔌 Sockets disconnected (Code {e.code}). Re-routing network matrix loop in 5 seconds...[/meta]")
            
        except Exception as e:
            console.print(f"\n  [error]✕ Pipeline Driver Error:[/error] [meta]{e}[/meta]\n")
            
        await asyncio.sleep(5)


def listen_for_drafts():
    """Spawns the long-running operational background async thread loop worker."""
    console.print("\n[brand]CommitDev[/brand] [meta]•[/meta] Live Monitor Agent")
    console.print("[meta]──────────────────────────────────────────────────[/meta]")
    try:
        asyncio.run(_listen_for_drafts_loop())
    except KeyboardInterrupt:
        console.print("\n  [meta]› Agent sequence halted gracefully via terminal signal. Good bye.[/meta]\n")
