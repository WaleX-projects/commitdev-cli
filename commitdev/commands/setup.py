import os
import sys
import subprocess
from pathlib import Path
import typer

app = typer.Typer()

def get_bundle_path():
    """Finds where PyInstaller extracted your files at runtime."""
    if hasattr(sys, '_MEIPASS'):
        return Path(sys._MEIPASS)
    # Fallback for local development
    return Path(__file__).parent.parent

def setup():
    """Configures Git globally to use the commitdev pre-push hook."""
    typer.echo("⚙️ Setting up global commitdev hooks...")
    
    # 1. Create the global directory where your hooks will live permanently
    global_hooks_dir = Path.home() / ".config" / "commitdev" / "hooks"
    global_hooks_dir.mkdir(parents=True, exist_ok=True)
    
    # 2. Extract the pre-push script embedded inside your binary
    bundle_dir = get_bundle_path()
    template_path = bundle_dir  / "hooks" / "pre-push"
    target_path = global_hooks_dir / "pre-push"
    
    if not template_path.exists():
        typer.echo(f"❌ Error: Internal template not found at {template_path}")
        raise typer.Exit(code=1)
        
    # 3. Write the pre-push script to the global config folder
    with open(template_path, "r") as src, open(target_path, "w") as dst:
        dst.write(src.read())
        
    # 4. Make it executable (crucial for Unix/Linux/macOS)
    os.chmod(target_path, 0o755)
    
    # 5. Tell Git to globally look at this folder for hooks
    try:
        subprocess.run(
            ["git", "config", "--global", "core.hooksPath", str(global_hooks_dir)],
            check=True
        )
        typer.echo("✨ Successfully activated global pre-push hooks!")
        typer.echo("🚀 commitdev will now monitor your pushes automatically.")
    except subprocess.CalledProcessError:
        typer.echo("❌ Failed to update your global git config.")
        raise typer.Exit(code=1)




def uninstall():
    """Removes global commitdev hooks and resets Git configurations."""
    typer.echo("🗑️ Starting commitdev uninstallation...")
    
    # 1. Unset Git's global hooks path configuration
    try:
        # Check if the config is actually pointing to commitdev before unsetting
        result = subprocess.run(
            ["git", "config", "--global", "core.hooksPath"],
            capture_output=True, text=True
        )
        current_hooks_path = result.stdout.strip()
        
        if "commitdev" in current_hooks_path:
            subprocess.run(["git", "config", "--global", "--unset", "core.hooksPath"], check=True)
            typer.echo("✅ Reset global Git hooks path configuration.")
        else:
            typer.echo("ℹ️ Git core.hooksPath wasn't pointed to commitdev. Skipping reset.")
    except subprocess.CalledProcessError:
        typer.echo("⚠️ Could not alter Git configuration (it might already be clean).")

    # 2. Safely remove the global configuration folder (~/.config/commitdev)
    global_hooks_dir = Path.home() / ".config" / "commitdev"
    if global_hooks_dir.exists():
        try:
            # Recursively delete files inside the folder
            for item in global_hooks_dir.glob("**/*"):
                if item.is_file():
                    item.unlink()
            # Delete directories
            for item in sorted(global_hooks_dir.glob("**/*"), reverse=True):
                if item.is_dir():
                    item.rmdir()
            global_hooks_dir.rmdir()
            typer.echo(f"✅ Removed configuration folder at {global_hooks_dir}")
        except Exception as e:
            typer.echo(f"⚠️ Warning: Could not completely remove configuration directory: {e}")
    else:
        typer.echo("ℹ️ Configuration directory not found. Already clean!")

    typer.echo("✨ commitdev hooks have been successfully uninstalled.")
    typer.echo("ℹ️ Note: To completely remove the binary, run: sudo rm /usr/local/bin/commitdev")
    