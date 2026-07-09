import os
import sys
import time
import shutil
from pathlib import Path
import typer
from rich.console import Console
from rich.theme import Theme

commitdev_theme = Theme({
    "brand": "bold spring_green3",
    "success": "spring_green3",
    "meta": "dim grey39",
    "command": "bold white",
    "error": "bold red"
})

app = typer.Typer()
console = Console(theme=commitdev_theme, highlight=False)

def get_bundle_path():
    if hasattr(sys, '_MEIPASS'):
        return Path(sys._MEIPASS)
    return Path(__file__).parent.parent



def setup():
    """Executes the CommitDev installation sequence step-by-step."""
    console.print("\n[brand]CommitDev[/brand] [meta]•[/meta] Step-by-Step CLI Initialization")
    console.print("[meta]──────────────────────────────────────────────────[/meta]")
    
    home = Path.home()
    bashrc_path = home / ".bashrc"
    bash_profile_path = home / ".bash_profile"
    zshrc_path = home / ".zshrc"

    # ==========================================
    # STEP 1: Deploy Local Repository Pre-Push Hook
    # ==========================================
    console.print("[brand]Step 1:[/brand] [meta]Locating Git repository architecture...[/meta]")
    current_dir = Path.cwd()
    git_dir = current_dir / ".git"
    
    if git_dir.exists() and git_dir.is_dir():
        hooks_dir = git_dir / "hooks"
        hooks_dir.mkdir(exist_ok=True)
        pre_push_target = hooks_dir / "pre-push"
        
        pre_push_ui = """#!/usr/bin/env bash

# Read the last commit message locally
commit_msg=$(git log -1 --format=%s)

# Specifically look for [draft] or post (case-insensitive)
if echo "$commit_msg" | grep -iq "\\[draft\\]"; then
    echo -e ""
    echo -e "\\033[1;35m✨ Hey! CommitDev here.\\033[0m"
    echo -e "\\033[1;36mI spotted your \\033[1m[draft]\\033[22m tag. We've locked onto this commit and armed your pipeline.\\033[0m"
    echo -e "\\033[32mGo ahead and finish the push—I'll drop your live workspace right beneath it when it lands! 🚀\\033[0m"
    echo -e ""
fi

exit 0
"""
        try:
            with open(pre_push_target, "w", encoding="utf-8", newline="\n") as f:
                f.write(pre_push_ui)
            if sys.platform != "win32":
                os.chmod(pre_push_target, 0o755)
            console.print(f"  [success]✓[/success] Local pre-push message engine deployed to [meta].git/hooks/pre-push[/meta]")
        except Exception as e:
            console.print(f"  [meta]› Skipped project hook configuration: {e}[/meta]")
    else:
        console.print("  [meta]› Current directory is not a Git repo root. Skipping local pre-push setup.[/meta]")

    # ==========================================
    # STEP 2: Append Post-Push Intercept to .bashrc
    # ==========================================
    console.print("\n[brand]Step 2:[/brand] [meta]Appending post-push wrapper to profile script bottoms...[/meta]")
    
    git_wrapper_code = """
# >>> commitdev git core hook >>>
git() {
    if [ "$1" = "push" ]; then
        local commit_msg=$(command git log -1 --format=%s)
        
        # 1. Run the native git push
        command git "$@"
        
        # 2. Check explicitly for [draft] right after upload completes
        if [ $? -eq 0 ]; then
            if echo "$commit_msg" | grep -iq "\\[draft\\]"; then
                echo -e "\\n\\033[1;35m📡 Code is safe on GitHub. Spinnaker/Daphne connection spinning up...\\033[0m"
                commitdev listen-for-drafts
            else
                echo -e "\\n✅ Normal push complete."
            fi
        fi
    else
        command git "$@"
    fi
}
# <<< commitdev git core hook <<<
"""

    windows_bridge_code = """
# >>> commitdev windows bridge >>>
if [ -f ~/.bashrc ]; then
    . ~/.bashrc
fi
# <<< commitdev windows bridge <<<
"""

    try:
        # Append to .bashrc
        bashrc_content = bashrc_path.read_text(encoding="utf-8") if bashrc_path.exists() else ""
        if "commitdev git core hook" not in bashrc_content:
            prefix = "\n" if bashrc_content and not bashrc_content.endswith("\n") else ""
            with open(bashrc_path, "a", encoding="utf-8") as f:
                f.write(prefix + git_wrapper_code)
            console.print("  [success]✓[/success] Appended core wrapper directly to bottom of [meta]~/.bashrc[/meta]")
        else:
            console.print("  [meta]ℹ Git wrapper code already exists in your ~/.bashrc[/meta]")

        # Append to Mac .zshrc if it exists
        if sys.platform == "darwin" or zshrc_path.exists():
            zsh_content = zshrc_path.read_text(encoding="utf-8") if zshrc_path.exists() else ""
            if "commitdev git core hook" not in zsh_content:
                prefix = "\n" if zsh_content and not zsh_content.endswith("\n") else ""
                with open(zshrc_path, "a", encoding="utf-8") as f:
                    f.write(prefix + git_wrapper_code)
                console.print("  [success]✓[/success] Appended core wrapper directly to bottom of [meta]~/.zshrc[/meta]")

        # Append Windows Git Bash Bridge
        if sys.platform == "win32" or bash_profile_path.exists():
            profile_content = bash_profile_path.read_text(encoding="utf-8") if bash_profile_path.exists() else ""
            if "commitdev windows bridge" not in profile_content:
                prefix = "\n" if profile_content and not profile_content.endswith("\n") else ""
                with open(bash_profile_path, "a", encoding="utf-8") as f:
                    f.write(prefix + windows_bridge_code)
                console.print("  [success]✓[/success] Fixed cross-platform environment bridge inside [meta]~/.bash_profile[/meta]")

    except Exception as e:
        console.print(f"  [error]✕ Error appending profiles:[/error] {e}")
        raise typer.Exit(code=1)

    # ==========================================
    # STEP 3: Refresh Active Terminal Environment
    # ==========================================
    console.print("\n[brand]Step 3:[/brand] [meta]Environment configuration ready![/meta]")
    console.print("[meta]──────────────────────────────────────────────────[/meta]")
    
    active_profile = "~/.bashrc"
    if sys.platform == "darwin" and zshrc_path.exists():
        active_profile = "~/.zshrc"

    console.print("\n[white]To apply these changes immediately, run this command now:[/white]")
    console.print(f"    [command]source {active_profile}[/command]\n")
    
    console.print("[white]Next Steps[/white]")
    console.print("  [meta]›[/meta] Run the verification login utility:")
    console.print("    [brand]commitdev login[/brand]\n")


def uninstall():
    """Removes global cdv shell wrappers and completely restores profiles cleanly."""
    console.print("\n[brand]CommitDev[/brand] [meta]•[/meta] De-registration Sequence")
    console.print("[meta]──────────────────────────────────────────────────[/meta]")
    
    home = Path.home()
    targets = [home / ".bashrc", home / ".bash_profile", home / ".zshrc"]
    config_path = home / ".commitdev.json"
    
    # ==========================================
    # STEP 1: Purge Configuration Cache
    # ==========================================
    console.print("[brand]Step 1:[/brand] [meta]Purging authentication credentials cache...[/meta]")
    try:
        if config_path.exists():
            config_path.unlink()
            console.print("  [success]✓[/success] Safely erased local configuration profile state data")
        else:
            console.print("  [meta]› Configuration profile data was already empty or clean.[/meta]")
    except Exception as e:
        console.print(f"  [error]✕ Error clearing configuration profile:[/error] {e}")

    # ==========================================
    # STEP 2: Scrub Terminal Shell Profiles
    # ==========================================
    console.print("\n[brand]Step 2:[/brand] [meta]Cleaning user terminal shell profiles...[/meta]")
    try:
        for target in targets:
            if target.exists():
                lines = target.read_text(encoding="utf-8").splitlines()
                cleaned_lines = []
                skip = False
                
                for line in lines:
                    # Catches both legacy commitdev markers and the new cdv namespace markers
                    if ">>> commitdev" in line or ">>> cdv" in line:
                        skip = True
                        continue
                    if "<<< commitdev" in line or "<<< cdv" in line:
                        skip = False
                        continue
                    if not skip:
                        cleaned_lines.append(line)
                        
                target.write_text("\n".join(cleaned_lines) + "\n", encoding="utf-8")
        console.print("  [success]✓[/success] Removed custom intercept wrappers from shell environments")
    except Exception as e:
        console.print(f"  [error]✕ Error cleaning shell configurations:[/error] {e}")

    # ==========================================
    # STEP 3: Remove Local Git Hook If It Exists
    # ==========================================
    console.print("\n[brand]Step 3:[/brand] [meta]Checking local workspace hooks repository layers...[/meta]")
    current_dir = Path.cwd()
    pre_push_target = current_dir / ".git" / "hooks" / "pre-push"
    
    if pre_push_target.exists():
        try:
            content = pre_push_target.read_text(encoding="utf-8")
            # Catches variations of CommitDev tags or your new automated short signatures
            if "CommitDev" in content or "cdv" in content:
                os.remove(pre_push_target)
                console.print("  [success]✓[/success] Safely removed [meta].git/hooks/pre-push[/meta] tracker file")
            else:
                console.print("  [meta]› Local hook file was modified or custom. Leaving untouched.[/meta]")
        except Exception as e:
            console.print(f"  [meta]› Could not clean project hooks directory: {e}[/meta]")
    else:
        console.print("  [meta]› No active CommitDev hooks found inside current directory architecture.[/meta]")

    # ==========================================
    # STEP 4: Finalize Core Binary Warnings
    # ==========================================
    console.print("\n[brand]Step 4:[/brand] [meta]Finalizing de-registration checks...[/meta]")
    console.print("[meta]──────────────────────────────────────────────────[/meta]")
    console.print("[success]✓[/success] CommitDev uninstallation routine finalized safely")
    
    if sys.platform == "win32":
        console.print("  [meta]ℹ Note: To fully remove the app binary, erase cdv-windows.exe or cdv.exe from your PATH environment locations.[/meta]\n")
    elif sys.platform == "darwin":
        console.print("  [meta]ℹ Note: To fully remove the executable asset binary, run: sudo rm /usr/local/bin/cdv-macos[/meta]\n")
    else:
        console.print("  [meta]ℹ Note: To fully remove the executable asset binary, run: sudo rm /usr/local/bin/cdv-linux[/meta]\n")


if __name__ == "__main__":
    
    app()
