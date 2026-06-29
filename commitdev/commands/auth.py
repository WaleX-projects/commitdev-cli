import sys
import time
import typer
from rich.console import Console
from rich.theme import Theme
from commitdev.config import (
    save_token,
    clear_token,
    get_token,
)
from commitdev.api import get, post

# CommitDev color landscape matching your dashboard layout
commitdev_theme = Theme({
    "brand": "bold spring_green3",   # Signature mint/emerald color
    "success": "spring_green3",
    "meta": "dim grey39",            # Secondary dark slate gray text
    "command": "bold white",
    "error": "bold red",
    "warn": "bold yellow"
})

console = Console(theme=commitdev_theme, highlight=False)

def login():
    """
    Log in to your CommitDev account.

    Opens the device login flow and saves your account
    so you can use CommitDev from the CLI.
    """
    console.print("\n[brand]CommitDev[/brand] [meta]•[/meta] Authentication")
    console.print("[meta]──────────────────────────────────────────────────[/meta]")

    with console.status("[meta]Requesting secure authentication codes...[/meta]", spinner="simpleDots"):
        try:
            data = post("/cli/auth/device/start/")
        except Exception as e:
            console.print(f"  [error]✕ Connection Failed:[/error] Could not contact backend server: {e}\n")
            return

    device_code = data["device_code"]
    interval = data.get("interval", 5)

    console.print(f"  [meta]›[/meta] Visit URL   [meta]›[/meta] [white]{data['verification_uri']}[/white]")
    console.print(f"  [meta]›[/meta] Enter Code [meta]›[/meta] [brand]{data['user_code']}[/brand]\n")

    # Interactive polling loading context wrapper
    with console.status("[meta]Awaiting secure authorization from browser...[/meta]", spinner="simpleDots"):
        while True:
            try:
                result = post("/cli/auth/device/poll/", {"device_code": device_code})
                
                if result.get("authenticated"):
                    save_token(result)
                    console.print(f"\n[success]✓[/success] Authorization confirmed. Welcome back, [white]{result['user']['username']}[/white]!\n")
                    break
                    
                if result.get("error") == "slow_down":
                    interval += 5
                    
            except Exception:
                interval = min(interval + 2, 30) 

            time.sleep(interval)


def logout():
    """
    Log out of your CommitDev account.

    Removes your saved login from this computer.
    """
    console.print("\n[brand]CommitDev[/brand] [meta]•[/meta] De-authentication")
    console.print("[meta]──────────────────────────────────────────────────[/meta]")
    
    clear_token()
    
    console.print("[success]✓[/success] Clear-out sequence verified. Local access token purged.\n")


def whoami():
    """
    Show information about the currently logged-in user.

    Displays your CommitDev account details.
    """
    console.print("\n[brand]CommitDev[/brand] [meta]•[/meta] Active Profile")
    console.print("[meta]──────────────────────────────────────────────────[/meta]")

    auth = get_token()

    if not auth:
        console.print("  [warn]⚠ No active credentials profile found. Run 'commitdev login' to authenticate.[/warn]\n")
        return

    user = auth["user"]
    console.print(f"  [meta]›[/meta] Account User [meta]›[/meta] [white]{user.get('username', 'N/A')}[/white]")                     
    console.print(f"  [meta]›[/meta] GitHub ID    [meta]›[/meta] {user.get('github_id', 'N/A')}\n")                   


def doctor():
    """Diagnose your CommitDev installation."""
    try:
        data = get("/cli/doctor/")

        console.print("\n[brand]CommitDev[/brand] [meta]•[/meta] Diagnostics")
        console.print("[meta]──────────────────────────────────────────────────[/meta]")

        auth_val = "[success]YES[/success]" if data["user"]["authenticated"] else "[error]NO[/error]"
        gh_val = "[success]CONNECTED[/success]" if data["github"]["connected"] else "[error]NOT CONNECTED[/error]"

        console.print(f"Core Service   [meta]›[/meta] [success]ONLINE[/success]")
        console.print(f"Session Auth   [meta]›[/meta] {auth_val}")
        console.print(f"Active Account [meta]›[/meta] [white]{data['user']['username']}[/white]")
        console.print(f"GitHub Sync    [meta]›[/meta] {gh_val}")

        console.print("\n[white]Repositories[/white]")
        console.print(f"  Total Tracks [meta]›[/meta] {data['repositories']['total']}")
        console.print(f"  Active Hubs  [meta]›[/meta] {data['repositories']['active']}")

        console.print("\n[white]Content Artifacts[/white]")
        console.print(f"  Staged Draft [meta]›[/meta] {data['posts']['drafts']}")
        console.print(f"  Published    [meta]›[/meta] {data['posts']['published']}")

        console.print("\n[white]Integrations[/white]")
        integrations = data["integrations"]
        providers = integrations["connected_providers"]
        
        if not integrations["has_targets"]:
            console.print("  Distribution [meta]›[/meta] [warn]WARNING: NO TARGET DUCTS LINKED[/warn]")
        else:
            console.print(f"  Distribution [meta]›[/meta] [success]LINKED[/success] [meta]({', '.join(providers)})[/meta]")
            
        if integrations["expired_tokens"] > 0:
            console.print(f"  Token Health [meta]›[/meta] [error]CRITICAL: RE-AUTH REQUIRED[/error]")
        else:
            console.print("  Token Health [meta]›[/meta] [success]ALL CHANNELS ACTIVE[/success]")

        console.print("[meta]──────────────────────────────────────────────────[/meta]")

        # Evaluate the healthy layout parameters cleanly
        if (
            data["user"]["authenticated"]
            and data["github"]["connected"]
            and integrations["has_targets"]
            and integrations["expired_tokens"] == 0
        ):
            console.print("[success]✓ Everything looks great. Local engine is ready to sync pushes.[/success]\n")
        else:
            console.print("[warn]⚠ Action recommended. Some diagnostic rules flagged structural drops.[/warn]\n")

    except Exception as e:
        console.print(f"\n[error]✕ Doctor check aborted:[/error] [meta]{e}[/meta]\n")