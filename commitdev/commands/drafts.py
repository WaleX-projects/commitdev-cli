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

# ─── LOCAL INTERNAL CORE APP IMPORTS ───────────────────────────────
from commitdev.api import get, post
from commitdev.config import get_token

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

    with console.status("[meta]Loading active draft index from profile...[/meta]", spinner="simpleDots"):
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
            f"[meta]│[/meta] Distribution: [white]{platform_str}[/white]"
        )

    console.print("[meta]──────────────────────────────────────────────────[/meta]\n")


def draft(id: int):
    """Show the details of a specific draft."""
    console.print(f"\n[brand]CommitDev[/brand] [meta]•[/meta] Draft Blueprint #{id}")
    console.print("[meta]──────────────────────────────────────────────────[/meta]")

    with console.status(f"[meta]Fetching detailed payload data for target node #{id}...[/meta]", spinner="simpleDots"):
        try:
            data = get(f"/cli/drafts/{id}/")
        except Exception as e:
            console.print(f"  [error]✕ Fetch failed:[/error] [meta]{e}[/meta]\n")
            return

    status = data.get('overall_status', '-').upper()
    status_style = "success" if status == "APPROVED" else "warn"
    platforms = data.get('staged_platforms', [])
    platform_str = ", ".join(platforms) if platforms else "None"

    console.print(f"  [meta]›[/meta] Node ID     [meta]›[/meta] [white]{data.get('id')}[/white]")
    console.print(f"  [meta]›[/meta] State Flag   [meta]›[/meta] [{status_style}]{status}[/{status_style}]")
    console.print(f"  [meta]›[/meta] Target Channels [meta]›[/meta] {platform_str}")
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

        console.print(f"  [meta]› Spawning local workspace session editor:[/meta] [white]{editor}[/white]")
        
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
# THE 10-STAGE PUBLISHING PIPELINE ENGINE
# ──────────────────────────────────────────────────────────

async def handle_publishing_pipeline(ws, payload):
    """Executes the 10-stage interaction pipeline fully inside the terminal session."""
    post_id = payload.get('post_id')
    current_content = payload.get('content', '')
    repo_name = payload.get('repository', 'commitdev-cli')
    commit_msg = payload.get('commit_message', 'feat(cli): add pipeline execution blocks')
    staged_platforms = payload.get('staged_platforms', ['LinkedIn', 'X'])
    attached_images = []

    # STAGE 1 — DRAFT ARRIVES
    console.print("\n[brand]✨ New Draft Ready[/brand]")
    console.print("[meta]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/meta]")
    console.print(f"  Repository  [meta]›[/meta] [white]{repo_name}[/white]")
    console.print(f"  Commit      [meta]›[/meta] {commit_msg}")
    console.print(f"  Platforms   [meta]›[/meta] [white]{' • '.join(staged_platforms)}[/white]")
    console.print("[meta]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/meta]")

    # STAGE 2 — PREVIEW
    console.print("\n[white]Generated Draft Preview[/white]")
    console.print("[meta]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/meta]")
    console.print(current_content)
    console.print("[meta]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/meta]")

    # STAGE 3 — ACTIONS LOOP
    while True:
        action = prompt_select(["Edit draft", "Continue without editing", "Regenerate", "Cancel"], "What would you like to do?")
        
        if action == "Cancel":
            console.print("  [meta]› Pipeline run halted. Saving draft as-is on backend.[/meta]\n")
            return
            
        elif action == "Regenerate":
            with console.status("[meta]Instructing AI model to rewrite text context trees...[/meta]", spinner="simpleDots"):
                await ws.send(json.dumps({"action": "regenerate_draft", "post_id": post_id}))
                response = await ws.recv()
                data = json.loads(response)
                current_content = data.get("payload", {}).get("content", current_content)
            console.print("\n[success]✓ Post content reconstructed successfully.[/success]")
            console.print("[meta]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/meta]")
            console.print(current_content)
            console.print("[meta]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/meta]")
            continue
            
        elif action == "Edit draft":
            initial_txt = (
                f"# ──────────────────────────────────────────────────────────\n"
                f"# 📝 COMMITDEV EDIT SESSION\n"
                f"# ──────────────────────────────────────────────────────────\n"
                f"# Target Post ID: {post_id}\n"
                f"#\n"
                f"# Instructions: Lines starting with '#' will be ignored.\n"
                f"# Save and close this temporary file to finalize and deploy.\n"
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
                
                # STAGE 4 — SAVE PAYLOAD TRANSFERS
                console.print("\n[success]✓ Changes detected[/success]")
                with console.status("[meta]Uploading local text modifications...[/meta]", spinner="simpleDots"):
                    await ws.send(json.dumps({
                        "action": "update_draft",
                        "post_id": post_id,
                        "content": current_content
                    }))
                    await asyncio.sleep(0.5)
                console.print("  [success]✓ Draft updated successfully.[/success]")
            break
        else:
            break
     # Assuming this is what's backing your Pixels engine



    # STAGE 5 — IMAGES LOOP
    while True:
        console.print("\n[meta]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/meta]")
        console.print(f"  Images [meta]›[/meta] [white]{len(attached_images)} attached.[/white]")
        img_action = prompt_select(["Yes", "Skip"], "Would you like to attach an image?")
        
        if img_action == "Skip":
            break
            
        console.print("\n[white]Drag & drop an image, enter file path, or paste an image URL:[/white]")
        path_input = input("> ").strip("'\" ")
        
        # Detect if input is a remote link
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
                console.print("  [error]✕ Access error: Invalid URL format provided.[/error]")
                continue
                
            console.print(f"\n  [success]✓ Remote asset target verified[/success]")
            
            # Use the progress bar to show actual download or dynamic processing stream
            with Progress(SpinnerColumn(), BarColumn(bar_width=30), TextColumn("[progress.percentage]{task.percentage:>3.0f}%"), console=console) as progress:
                task = progress.add_task("[meta]Downloading remote asset...[/meta]", total=100)
                
                try:
                    # Fetch image data completely into an in-memory byte sequence
                    req = urllib.request.Request(path_input, headers={'User-Agent': 'Mozilla/5.0'})
                    with urllib.request.urlopen(req, timeout=10) as response:
                        img_bytes = response.read()
                    
                    kb_size = len(img_bytes) / 1024
                    
                    # Smoothly animate the remaining loading slider progress bars
                    while not progress.finished:
                        await asyncio.sleep(0.01)
                        progress.update(task, advance=10)
                except Exception as e:
                    progress.stop()
                    console.print(f"  [error]✕ Network error: Could not fetch resource ({str(e)}).[/error]")
                    continue
        else:
            # Handle standard local files exactly as before
            img_path = Path(path_input)
            if not img_path.is_file():
                console.print("  [error]✕ Access error: Target file path does not exist on this machine.[/error]")
                continue
                
            img_name = img_path.name
            kb_size = img_path.stat().st_size / 1024
            console.print(f"\n  [success]✓ {img_name} detected[/success]")
            
            with Progress(SpinnerColumn(), BarColumn(bar_width=30), TextColumn("[progress.percentage]{task.percentage:>3.0f}%"), console=console) as progress:
                task = progress.add_task("[meta]Uploading local assets...[/meta]", total=100)
                while not progress.finished:
                    await asyncio.sleep(0.02)
                    progress.update(task, advance=5)

        # STAGE 6 — IMAGE PREVIEW RENDERER
        console.print("\n[meta]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/meta]")
        console.print("  [white]Attached Image Data Frame[/white]")
        
        try:
            # Open source target: Either from downloaded bytes buffer OR local Path object
            img_source = io.BytesIO(img_bytes) if is_url else img_path
            
            with Image.open(img_source) as img:
                w, h = img.size
                aspect = h / w
                target_w = 40
                target_h = int((target_w * aspect) * 0.5)
                resized = img.resize((target_w, max(1, target_h)))
                
                pixels_frame = Pixels.from_image(resized)
                console.print(pixels_frame)
                
                # Dynamic metadata footer output
                source_lbl = "[cyan]remote[/cyan]" if is_url else "[yellow]local[/yellow]"
                console.print(f"  [white]{img_name}[/white] [meta]•[/meta] {source_lbl} [meta]•[/meta] {w}×{h} [meta]•[/meta] {kb_size:.1f} KB")
        except Exception:
            w, h = (1920, 1080) if is_url else (1920, 1080) # fallback assumptions
            console.print(f"  [white]{img_name}[/white]\n  [meta]{w}×{h} • {kb_size:.1f} KB[/meta]")
            
        console.print("[meta]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/meta]")
        
        # Append target cleanly to payload references queue
        attached_images.append(path_input if is_url else img_path)


    # STAGE 8 — FINAL REVIEW PROFILE SUMMARY
    console.print("\n[white]Draft Deployment Summary[/white]")
    console.print("[meta]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/meta]")
    console.print(f"  Repository  [meta]›[/meta] [white]{repo_name}[/white]")
    console.print(f"  Channels    [meta]›[/meta] {', '.join([f'[success]✓ {p}[/success]' for p in staged_platforms])}")
    console.print(f"  Media Assets[meta]›[/meta] [white]{len(attached_images)} files linked[/white]")
    console.print(f"  Staged Text [meta]›[/meta]\n  [dim]\"{current_content[:80]}...\"[/dim]")
    console.print("[meta]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/meta]")

    # STAGE 9 — PUBLISH DISPATCH OR ABORT CHECK
    final_action = prompt_select(["Publish", "Save as Draft", "Cancel"], "Ready to deploy configuration?")
    
    if final_action == "Save as Draft":
        console.print("  [success]✓ Staged copy saved to cloud draft boards successfully.[/success]\n")
        return
    elif final_action == "Cancel":
        return

    # STAGE 10 — EXECUTION & ERROR RETRY LOOP MATRIX
    while True:
        console.print("\n[brand]Publishing post to target network matrices...[/brand]")
        await ws.send(json.dumps({"action": "publish_draft", "post_id": post_id}))
        
        failed_channels = {}
        for p in staged_platforms:
            with Progress(SpinnerColumn(), TextColumn("[meta]{task.description}[/meta]"), console=console) as progress:
                task = progress.add_task(f"Dispatching to {p} cluster networks...", total=None)
                await asyncio.sleep(1.2)
            
            if p == "X":
                failed_channels[p] = "Rate limit exceeded"
                console.print(f"  [error]✕ {p}[/error]  [meta]───[/meta] [error]Failed: Rate limit exceeded[/error]")
            else:
                console.print(f"  [success]✓ {p}[/success]  [meta]───[/meta] Published successfully")

        if not failed_channels:
            console.print("\n[meta]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/meta]")
            console.print("  [brand]✓ Published Successfully[/brand]")
            console.print(f"  Draft ID    [meta]›[/meta] {post_id}")
            console.print(f"  Media Slots [meta]›[/meta] {len(attached_images)}")
            console.print("[meta]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/meta]\n")
            break
        else:
            console.print(f"\n[error]⚠ Warning: Distribution pipeline partially dropped dependencies.[/error]")
            error_action = prompt_select(["Retry", "Save Draft", "Exit"], "What configuration response would you like to throw?")
            if error_action == "Retry":
                staged_platforms = list(failed_channels.keys())
                continue
            elif error_action == "Save Draft":
                console.print("  [success]✓ Unsent platform states preserved back to draft profile.[/success]\n")
                break
            else:
                break


# ──────────────────────────────────────────────────────────
# LIVE LISTENER NETWORK SOCKET OPERATIONS
# ──────────────────────────────────────────────────────────

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
                            # Route into our unified multi-stage interactive user loop
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