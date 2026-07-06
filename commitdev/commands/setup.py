import os
import sys
import subprocess
import time
import shutil
from pathlib import Path
import typer
from rich.console import Console
from rich.theme import Theme

# Theme layout system matching your design profile
commitdev_theme = Theme({
    "brand": "bold spring_green3",   # Primary mint/emerald signature hue
    "success": "spring_green3",
    "meta": "dim grey39",            # Dark slate grey for secondary structural logs
    "command": "bold white",
    "error": "bold red"
})

app = typer.Typer()
console = Console(theme=commitdev_theme, highlight=False)

def get_bundle_path():
    """Finds where PyInstaller extracted your files at runtime."""
    if hasattr(sys, '_MEIPASS'):
        return Path(sys._MEIPASS)
    return Path(__file__).parent.parent

def get_platform_config_dir():
    """Returns system-appropriate global data directory structures."""
    if sys.platform == "win32":
        # Windows standard: C:\Users\User\AppData\Roaming\commitdev
        base_dir = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
        return base_dir / "commitdev"
    else:
        # macOS/Linux standard: ~/.config/commitdev
        return Path.home() / ".config" / "commitdev"

def setup():
    """Configures Git globally to use the commitdev pre-push hook across Windows, Mac, and Linux."""
    console.print("\n[brand]CommitDev[/brand] [meta]•[/meta] CLI Initialization")
    console.print("[meta]──────────────────────────────────────────────────[/meta]")
    
    # 1. Resolve cross-platform configuration directory paths
    global_dir = get_platform_config_dir()
    global_hooks_dir = global_dir / "hooks"
    global_hooks_dir.mkdir(parents=True, exist_ok=True)
    
    # 2. Extract internal paths safely from compiled binary tree
    bundle_dir = get_bundle_path()
    template_path = bundle_dir / "commitdev" / "hooks" / "pre-push"
    target_path = global_hooks_dir / "pre-push"
    
    if not template_path.exists():
        console.print(f"  [error]✕ Error:[/error] Internal template profile missing at: {template_path}")
        raise typer.Exit(code=1)
        
    # 3. Write file bytes inside a smooth spinner environment
    with console.status("[meta]Deploying tracking hooks directly to your profile...[/meta]", spinner="simpleDots"):
        try:
            with open(template_path, "r", encoding="utf-8", newline="\n") as src, open(target_path, "w", encoding="utf-8", newline="\n") as dst:
                dst.write(src.read())
            
            # 4. Enforce POSIX execution privileges (Ignored gracefully by Windows filesystem layers)
            if sys.platform != "win32":
                os.chmod(target_path, 0o755)
            time.sleep(0.5)
        except Exception as e:
            console.print(f"  [error]✕ Error:[/error] Failed writing file assets: {e}")
            raise typer.Exit(code=1)

    # 5. Connect git global tracking configurations safely
    try:
        # Git internally expects forward slashes for hooksPath configurations even on Windows environments
        git_friendly_path = str(global_hooks_dir).replace("\\", "/")
        
        subprocess.run(
            ["git", "config", "--global", "core.hooksPath", git_friendly_path],
            check=True, capture_output=True
        )
        
        # Format the display output path depending on terminal system properties
        display_path = "~\\AppData\\Roaming\\commitdev" if sys.platform == "win32" else "~/.config/commitdev"
        console.print(f"[success]✓[/success] Active hook wrappers mapped to [meta]{display_path}[/meta]")
        console.print("[success]✓[/success] Background synchronization engine activated successfully\n")
        
        # Next Steps block matching the premium layout profile
        console.print("\n[white]Next Steps[/white]")
        console.print("  [meta]›[/meta] Move into an active repository workspace:")
        console.print("    [command]cd[/command] [meta]path/to/your/project[/meta]")
        console.print("  [meta]›[/meta] Run the login command:")
        console.print("    [brand]commitdev login[/brand]\n")
                
    except subprocess.CalledProcessError:
        console.print("  [error]✕ Error:[/error] Core system rejected global git hook updates.")
        raise typer.Exit(code=1)


def uninstall():
    """Removes global commitdev hooks and resets Git configurations safely across all operating systems."""
    console.print("\n[brand]CommitDev[/brand] [meta]•[/meta] De-registration Sequence")
    console.print("[meta]──────────────────────────────────────────────────[/meta]")
    
    # 1. Clean out core git mappings
    try:
        result = subprocess.run(
            ["git", "config", "--global", "core.hooksPath"],
            capture_output=True, text=True
        )
        current_hooks_path = result.stdout.strip()
        
        if "commitdev" in current_hooks_path.lower():
            with console.status("[meta]Cleaning hooks routing targets...[/meta]", spinner="simpleDots"):
                subprocess.run(["git", "config", "--global", "--unset", "core.hooksPath"], check=True)
            console.print("[success]✓[/success] Global Git hooks runtime configuration reset cleanly")
        else:
            console.print("  [meta]›[/meta] Git engine hooks path was already clean. Skipping.")
    except subprocess.CalledProcessError:
        console.print("  [meta]›[/meta] Git configurations empty or inaccessible.")

    # 2. Clear application cache matrices cleanly using native directory purges
    global_dir = get_platform_config_dir()
    if global_dir.exists():
        try:
            with console.status("[meta]Purging profile storage layers...[/meta]", spinner="simpleDots"):
                # Use shutil to eliminate os-specific looping quirks or system hidden files
                shutil.rmtree(global_dir)
                time.sleep(0.4)
            console.print(f"[success]✓[/success] Removed workspace parameters from [meta]{global_dir}[/meta]")
        except Exception as e:
            console.print(f"  [meta]› Warning: Could not purge file matrix completely: {e}[/meta]")
    else:
        console.print("  [meta]›[/meta] No workspace directory structures found.")

    # 3. Dynamic binary removal message depending on platform
    console.print("[success]✓[/success] CommitDev uninstallation routine finalized safely")
    if sys.platform == "win32":
        console.print("  [meta]ℹ Note: To strip the physical binary file, remove commitdev.exe from your WindowsApps location.[/meta]\n")
    else:
        console.print("  [meta]ℹ Note: To strip the physical binary file, run: sudo rm /usr/local/bin/commitdev[/meta]\n")


if __name__ == "__main__":
    app()
