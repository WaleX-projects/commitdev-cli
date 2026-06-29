import asyncio
import json
import os
import subprocess
import sys
import tempfile
import time
import websockets
import typer
from rich.console import Console
from rich.theme import Theme
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

    for draft in data:
        draft_id = draft.get('id')
        status = draft.get('overall_status', '-').upper()
        platforms = draft.get('staged_platforms', [])
        
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


def fetch_fresh_token():
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
    """Spawns a text editor populated with initial content."""
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
                            post_id = payload.get('post_id')
                            current_content = payload.get('content', '') 

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
                                clean_body = "\n".join([
                                    line for line in edited_result.splitlines() 
                                    if not line.strip().startswith("#")
                                ]).strip()
                                
                                with console.status("[meta]Transmitting dynamic copy modifications back to core pipeline...[/meta]", spinner="simpleDots"):
                                    await ws.send(json.dumps({
                                        "action": "update_draft",
                                        "post_id": post_id,
                                        "content": clean_body
                                    }))
                                    # Tiny back-off cushion for network dispatch execution synchronization
                                    await asyncio.sleep(0.5)
                                    
                                console.print(f"  [success]✓ Deployment updates successfully funneled to pipeline node #{post_id}![/success]")
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
