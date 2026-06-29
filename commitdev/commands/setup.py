import os
import sys
import subprocess
import time
from pathlib import Path
import typer
from rich.console import Console
from rich.theme import Theme

# Theme layout system matching Screenshot_2026-06-29-14-47-05-440_com.android.chrome.jpg
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


def setup():
    """Configures Git globally to use the commitdev pre-push hook."""
    console.print("\n[brand]CommitDev[/brand] [meta]•[/meta] CLI Initialization")
    console.print("[meta]──────────────────────────────────────────────────[/meta]")
    
    # 1. Create the global directory
    global_hooks_dir = Path.home() / ".config" / "commitdev" / "hooks"
    global_hooks_dir.mkdir(parents=True, exist_ok=True)
    
    # 2. Extract internal paths
    bundle_dir = get_bundle_path()
    template_path = bundle_dir / "hooks" / "pre-push"
    target_path = global_hooks_dir / "pre-push"
    
    if not template_path.exists():
        console.print(f"  [error]✕ Error:[/error] Internal template profile missing at: {template_path}")
        raise typer.Exit(code=1)
        
    # 3. Write execution blocks inside a quiet spinner environment
    with console.status("[meta]Deploying tracking hooks directly to your profile...[/meta]", spinner="simpleDots"):
        with open(template_path, "r") as src, open(target_path, "w") as dst:
            dst.write(src.read())
        
        # 4. Enforce POSIX execution privileges
        os.chmod(target_path, 0o755)
        time.sleep(0.5)

    # 5. Connect git global tracking configurations
    try:
        subprocess.run(
            ["git", "config", "--global", "core.hooksPath", str(global_hooks_dir)],
            check=True, capture_output=True
        )
        console.print("[success]✓[/success] Active hook wrappers mapped to [meta]~/.config/commitdev[/meta]")
        console.print("[success]✓[/success] Background synchronization engine activated successfully\n")
        
        # Next Steps block matching the premium layout profile
        console.print("[white]Next Steps[/white]")
        console.print("  [meta]›[/meta] Move into an active repository workspace:")
        console.print("    [command]cd[/command] [meta]path/to/your/project[/meta]")
        console.print("  [meta]›[/meta] Run verification tracking sequence:")
        console.print("    [brand]commitdev watch[/brand]\n")
        
    except subprocess.CalledProcessError:
        console.print("  [error]✕ Error:[/error] Core system rejected global git hook updates.")
        raise typer.Exit(code=1)


def uninstall():
    """Removes global commitdev hooks and resets Git configurations."""
    console.print("\n[brand]CommitDev[/brand] [meta]•[/meta] De-registration Sequence")
    console.print("[meta]──────────────────────────────────────────────────[/meta]")
    
    # 1. Clean out core git mappings
    try:
        result = subprocess.run(
            ["git", "config", "--global", "core.hooksPath"],
            capture_output=True, text=True
        )
        current_hooks_path = result.stdout.strip()
        
        if "commitdev" in current_hooks_path:
            with console.status("[meta]Cleaning hooks routing targets...[/meta]", spinner="simpleDots"):
                subprocess.run(["git", "config", "--global", "--unset", "core.hooksPath"], check=True)
            console.print("[success]✓[/success] Global Git hooks runtime configuration reset cleanly")
        else:
            console.print("  [meta]›[/meta] Git engine hooks path was already clean. Skipping.")
    except subprocess.CalledProcessError:
        console.print("  [meta]›[/meta] Git configurations empty or inaccessible.")

    # 2. Clear application cache matrices
    global_hooks_dir = Path.home() / ".config" / "commitdev"
    if global_hooks_dir.exists():
        try:
            with console.status("[meta]Purging profile storage layers...[/meta]", spinner="simpleDots"):
                for item in global_hooks_dir.glob("**/*"):
                    if item.is_file():
                        item.unlink()
                for item in sorted(global_hooks_dir.glob("**/*"), reverse=True):
                    if item.is_dir():
                        item.rmdir()
                global_hooks_dir.rmdir()
                time.sleep(0.4)
            console.print(f"[success]✓[/success] Removed workspace parameters from [meta]{global_hooks_dir}[/meta]")
        except Exception as e:
            console.print(f"  [meta]› Warning: Could not purge file matrix completely: {e}[/meta]")
    else:
        console.print("  [meta]›[/meta] No workspace directory structures found.")

    console.print("[success]✓[/success] CommitDev uninstallation routine finalized safely")
    console.print("  [meta]ℹ Note: To strip the physical binary file, run: sudo rm /usr/local/bin/commitdev[/meta]\n")


if __name__ == "__main__":
    app()
