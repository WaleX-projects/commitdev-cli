
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
            
            targets = data.get("targets", [])
            if targets:
                console.print("[meta]Deployment Targets:[/meta]")
                for target in targets:
                    platform = target.get("platform", "Unknown").title()
                    status = target.get("status", "pending")
                    url = target.get("url")
                    
                    if status == "success" and url:
                        console.print(f"  • [green]{platform}[/green]: [link={url}]{url}[/link]")
                    elif status == "failed":
                        console.print(f"  • [red]{platform}[/red]: ✕ Failed to publish")
                    else:
                        console.print(f"  • [yellow]{platform}[/yellow]: Processing ({status})")
                console.print("")
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
    repo_name = payload.get('repository', 'commitdev-cli')
    commit_msg = payload.get('commit_message', 'feat(cli): add pipeline execution blocks')
    
    # Store drafts in a dictionary mapping {provider: content}
    posts_by_platform = payload.get('posts_by_platform', {})
    staged_platforms = [p.capitalize() for p in payload.get('staged_platforms', ['LinkedIn', 'X'])]
    
    # Backfill platform content if missing from payload
    for platform in staged_platforms:
        p_lower = platform.lower()
        if p_lower not in posts_by_platform:
            posts_by_platform[p_lower] = payload.get('content', '')

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
    # NESTED TASK ROUTINES
    # =========================================================================

    async def run_edit_content_sequence():
        nonlocal posts_by_platform
        if not staged_platforms:
            console.print("\n  [error]✕ Edit Aborted:[/error] No target platforms are active to edit.\n")
            return

        # Let user choose which specific copy platform to edit
        edit_target = prompt_select(staged_platforms, "Which platform draft do you want to edit?")
        platform_key = edit_target.lower()
        current_content = posts_by_platform.get(platform_key, "")

        console.print(f"\n[brand]📝 EDITING DRAFT FOR {edit_target.upper()}[/brand]")
        console.print("[meta]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/meta]")
        
        initial_txt = (
            f"# ──────────────────────────────────────────────────────────\n"
            f"# 📝 COMMITDEV EDIT SESSION - {edit_target.upper()}\n"
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
            sanitized_content = "\n".join([
                line for line in edited_result.splitlines() 
                if not line.strip().startswith("#")
            ]).strip()
            
            console.print("\n[success]✓ Local buffer changes detected[/success]")
            with console.status("[meta]Uploading draft modifications...[/meta]", spinner="simpleDots"):
                await ws.send(json.dumps({
                    "action": "update_draft",
                    "post_id": post_id,
                    "platform": platform_key,
                    "content": sanitized_content
                }))
                
                # Receive payload wrapper: {"type": "send_private_message", "payload": {...}}
                response = await ws.recv()
                data = json.loads(response)
                payload_data = data.get("payload", {})
                
                # Sync internal state using consumer keys
                posts_by_platform[platform_key] = payload_data.get("content", sanitized_content)
                
            console.print(f"  [success]✓ Sync Complete: {edit_target} draft updated.[/success]\n")

    async def run_regenerate_content_sequence():
        nonlocal posts_by_platform
        if not staged_platforms:
            console.print("\n  [error]✕ Regeneration Aborted:[/error] No target platforms are active to regenerate.\n")
            return

        target_to_regen = prompt_select(staged_platforms, "Which platform draft would you like to regenerate?")
        platform_key = target_to_regen.lower()

        console.print(f"\n[brand] REGENERATING {target_to_regen.upper()} WORKSPACE TEXT[/brand]")
        console.print("[meta]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/meta]")
        with console.status("[meta]Instructing AI model to rewrite text context trees...[/meta]", spinner="simpleDots"):
            await ws.send(json.dumps({
                "action": "regenerate_draft", 
                "post_id": post_id, 
                "platform": platform_key
            }))
            response = await ws.recv()
            data = json.loads(response)
            payload_data = data.get("payload", {})
            
            posts_by_platform[platform_key] = payload_data.get("content", posts_by_platform.get(platform_key, ""))
        console.print(f"\n[success]✓ {target_to_regen} copy reconstructed successfully via AI engine.[/success]\n")

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

            # ─── RENDERING INLINE IMAGE FRAME PREVIEW AND UPLODING TO THE BACKEND ───
            console.print("\n[meta]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/meta]")
            console.print("  [white]Attached Image Data Frame Preview[/white]")
            
            img_source = io.BytesIO(img_bytes) if is_url else img_path
            render_image_preview(img_source, img_name, kb_size, is_url)
            
            with console.status("[meta] Image uploading...[/meta]", spinner="simpleDots"):
                # Notice we matches the plural 'upload_images' payload action now
                await ws.send(json.dumps({
                    "action": "upload_images", 
                    "post_id": post_id,
                    "image": str(path_input)
                }))
                response = await ws.recv()
                data = json.loads(response)
                console.print("\n[success]✓ Image Linked Successfully[/success]\n")
            
            console.print("[meta]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/meta]\n")
            attached_images.append(path_input if is_url else img_path)

    async def run_platforms_manager_sequence():
        nonlocal staged_platforms
        console.print("\n[brand]📡 CHANNELS CONFIGURATION[/brand]")
        console.print(f"\n[brand]Currently Armed: {staged_platforms}[/brand]")
        console.print("[meta]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/meta]")
        
        available_channels = ["LinkedIn", "X", "Dev.to", "Medium"]
        
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
                # Initialize template layout if empty
                p_key = selected_channel.lower()
                if p_key not in posts_by_platform:
                    posts_by_platform[p_key] = f"New Draft for {selected_channel} from: '{commit_msg}'"
                console.print(f"  [meta]›[/meta] Enabled [success]{selected_channel}[/success] transmission cluster.\n")

    # =========================================================================
    # THE INTERACTIVE REVIEW HUB STATE MACHINE LOOP
    # =========================================================================
    while True:
        console.print("\n[brand]CommitDev[/brand] [meta]•[/meta] Interactive Review Hub")
        console.print("[meta]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/meta]")
        
        # Format list of images for clean layout view
        attached_desc = ", ".join([
            str(p).split('/')[-1] if not str(p).startswith("http") else "Remote Asset" 
            for p in attached_images
        ]) if attached_images else "None"
        
        # Build platform summaries
        platform_copies = ""
        for platform in staged_platforms:
            p_key = platform.lower()
            content_preview = posts_by_platform.get(p_key, "[dim italic]Empty copy draft[/dim italic]")
            # Indent each target copy text for legibility
            formatted_preview = "\n".join([f"    {line}" for line in content_preview.splitlines()])
            platform_copies += f"  [cyan]• {platform.upper()}:[/cyan]\n{formatted_preview}\n\n"

        hub_summary = (
            f"[white]Repository:[/white] {repo_name}\n"
            f"[white]Commit Msg:[/white] {commit_msg}\n"
            f"[white]Media files:[/white] {attached_desc}\n"
            f"[meta]──────────────────────────────────────────────────[/meta]\n"
            f"[white]Platform Target Specifications:[/white]\n\n"
            f"{platform_copies or '  [red]No Target Platforms Enabled[/red]\n'}"
        )
        
        console.print(Panel(hub_summary, title="[brand]POST SPECIFICATION[/brand]", border_style="grey39"))
        
        # Menu Selection Loop
        hub_options = [
            " Edit Content",
            " Regenerate (AI Rewrite)",
            " Manage Media Attachments (expermental)",
            " Toggle Target Channels",
            " 🚀 Deploy & Publish Now",
            " Cancel / Abort Deployment"
        ]
        
        selection = prompt_select(hub_options, "Select action cluster to execute:")
        
        if "Edit" in selection:
            await run_edit_content_sequence()
        elif " Regenerate" in selection:
            await run_regenerate_content_sequence()
        elif "Manage Media" in selection:
            await run_image_manager_sequence()
        elif " Toggle" in selection:
            await run_platforms_manager_sequence()
        elif "Deploy" in selection:
            if not staged_platforms:
                console.print("\n  [error]✕ Transmission Aborted:[/error] At least one platform target must be active.\n")
                continue
                
            console.print("\n[brand]🚀 TRANSMITTING CORE DEPLOYMENT TARGETS[/brand]")
            console.print("[meta]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/meta]")
            
            # Send publish action
            with console.status("[meta]Enqueuing publishing workers on server cluster...[/meta]", spinner="simpleDots"):
                try:
                    await ws.send(json.dumps({
                        "action": "publish_draft",
                        "post_id": post_id
                    }))
                    
                    # 1. First response back: Immediate acknowledgment that task is queued.
                    response = await ws.recv()
                    ack_result = json.loads(response)
                    payload_data = ack_result.get("payload", {})
                    
                    if payload_data.get("status") == "publishing_started":
                        console.print("  [meta]🚀 Task accepted by queue. Awaiting provider feedback...[/meta]")
                    else:
                        raise ValueError("No queuing task confirmation received.")
                        
                except Exception as e:
                    console.print(f"  [error]✕ Queue dispatch failed:[/error] [meta]{e}[/meta]\n")
                    break
            
            # 2. Block until the Celery task fires `publish_completed` broadcast back over the socket connection
            with console.status("[meta]Waiting for API providers response tokens...[/meta]", spinner="simpleDots"):
                try:
                    completed_response = await ws.recv()
                    result = json.loads(completed_response)
                    payload = result.get("payload", {})
                except Exception as e:
                    console.print(f"  [error]✕ Connection closed or timed out before completion feedback: {e}[/error]\n")
                    break

            if payload.get("status") == "published":
                console.print(f"\n  [success]✓ Deployment complete for node #{post_id}! [/success]\n")
                
                # Check successes
                successful = payload.get("platforms", [])
                failed = payload.get("failed_platforms", [])
                urls = payload.get("urls", {})
                
                if successful:
                    console.print("[meta]Successful Transmissions:[/meta]")
                    for platform in successful:
                        url = urls.get(platform, "No live link provided by provider")
                        console.print(f"  • [green]{platform.upper()}[/green]: [link={url}]{url}[/link]")
                        
                if failed:
                    console.print("\n[meta]Failed Transmissions:[/meta]")
                    for platform in failed:
                        console.print(f"  • [red]{platform.upper()}[/red]: Server-side interface failed.")
                console.print("")
                break
            else:
                error_msg = payload.get("error", "The operations queue returned zero success confirmations.")
                console.print(f"  [error]✕ Transmission Failed:[/error] [meta]{error_msg}[/meta]\n")
                break
                
        elif "Cancel" in selection:
            console.print("\n[warn]⚠ Deployment sequence aborted by operator.[/warn]\n")
            break

# ──────────────────────────────────────────────────────────
# CLI ENTRYPOINT ROUTINE
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
        



