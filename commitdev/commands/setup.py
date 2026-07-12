import os
import sys
import time
import shutil
from pathlib import Path
import typer
from rich.console import Console
from rich.theme import Theme
import subprocess 
commitdev_theme = Theme({
    "brand": "bold spring_green3",
    "success": "spring_green3",
    "meta": "dim grey39",
    "command": "bold white",
       "warn": "bold yellow",
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

# Specifically look for [post] or post (case-insensitive)
if echo "$commit_msg" | grep -iq "\\[post\\]"; then
    echo -e ""
    echo -e "\\033[1;35m✨ Hey! CommitDev here.\\033[0m"
    echo -e "\\033[1;36mI spotted your \\033[1m[post]\\033[22m tag. We've locked onto this commit and armed your pipeline.\\033[0m"
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
        
        # 2. Check explicitly for [post] right after upload completes
        if [ $? -eq 0 ]; then
            if echo "$commit_msg" | grep -iq "\\[post\\]"; then
                echo -e "\\n\\033[1;35m📡 Code is safe on GitHub. Time to tell the story...\\033[0m"
                commitdev listen-for-drafts
            else
                echo -e "\\n Normal push complete."
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
    console.print(f"    [brand]source {active_profile}[/brand]\n")
    




def uninstall():
    """Completely uninstall CommitDev from the current machine."""

    console.print("\n[brand]CommitDev[/brand] [meta]•[/meta] Uninstall")
    console.print("[meta]──────────────────────────────────────────────────[/meta]")

    home = Path.home()

    shell_profiles = [
        home / ".bashrc",
        home / ".bash_profile",
        home / ".zshrc",
    ]

    config_path = home / ".commitdev.json"

    # Remove configuration
    console.print("\n[white]• Removing local configuration...[/white]")

    try:
        if config_path.exists():
            config_path.unlink()
            console.print(
                "  [success]✓[/success] Removed CommitDev configuration."
            )
        else:
            console.print(
                "  [meta]› No configuration found."
            )

    except Exception as e:
        console.print(
            f"  [error]✕ Failed to remove configuration:[/error] {e}"
        )


    # Clean shell profiles
    console.print("\n[white]• Cleaning shell environment...[/white]")

    try:
        for profile in shell_profiles:

            if not profile.exists():
                continue

            lines = profile.read_text(
                encoding="utf-8"
            ).splitlines()

            cleaned = []
            skip = False

            for line in lines:

                if ">>> commitdev" in line or ">>> cdv" in line:
                    skip = True
                    continue

                if "<<< commitdev" in line or "<<< cdv" in line:
                    skip = False
                    continue

                if not skip:
                    cleaned.append(line)

            profile.write_text(
                "\n".join(cleaned) + "\n",
                encoding="utf-8",
            )

        console.print(
            "  [success]✓[/success] Shell configuration restored."
        )

    except Exception as e:
        console.print(
            f"  [error]✕ Failed to clean shell environment:[/error] {e}"
        )


    # Remove git hooks
    console.print("\n[white]• Checking Git integration...[/white]")

    hook = Path.cwd() / ".git" / "hooks" / "pre-push"

    if hook.exists():

        try:
            content = hook.read_text(
                encoding="utf-8"
            )

            if "CommitDev" in content or "cdv" in content:

                hook.unlink()

                console.print(
                    "  [success]✓[/success] Removed CommitDev Git hook."
                )

            else:
                console.print(
                    "  [meta]› No CommitDev hook detected."
                )

        except Exception as e:
            console.print(
                f"  [error]✕ Failed removing Git hook:[/error] {e}"
            )

    else:
        console.print(
            "  [meta]› No Git hook found."
        )


    # Remove executable
    console.print("\n[white]• Removing CommitDev executable...[/white]")

    binary_path = None

    for binary in (
        "commitdev",
        "commitdev.exe",
        "cdv",
        "cdv.exe",
    ):

        binary_path = shutil.which(binary)

        if binary_path:
            break


    if binary_path:

        if sys.platform == "win32":

            try:

                install_dir = str(Path(binary_path).parent)

                cleanup_script = (
                    f'Start-Sleep -Seconds 2; '
                    f'Remove-Item -LiteralPath "{binary_path}" -Force; '
                    f'if (Test-Path "{install_dir}") {{ '
                    f'if ((Get-ChildItem "{install_dir}" | Measure-Object).Count -eq 0) {{ '
                    f'Remove-Item "{install_dir}" -Force }} }}'
                )

                subprocess.Popen(
                    [
                        "powershell",
                        "-NoProfile",
                        "-ExecutionPolicy",
                        "Bypass",
                        "-Command",
                        cleanup_script,
                    ],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )

                console.print(
                    "  [success]✓[/success] Scheduled executable removal."
                )

            except Exception as e:
                console.print(
                    f"  [error]✕ Failed removing executable:[/error] {e}"
                )

        else:

            try:

                subprocess.run(
                    [
                        "sudo",
                        "rm",
                        binary_path
                    ],
                    check=True
                )

                console.print(
                    f"  [success]✓[/success] Removed {binary_path}"
                )

            except Exception:

                console.print(
                    "  [warn]› Administrator privileges required."
                )

                console.print(
                    f"  Run: [command]sudo rm \"{binary_path}\"[/command]"
                )

    else:

        console.print(
            "  [meta]› CommitDev executable not found."
        )


    console.print(
        "\n[meta]──────────────────────────────────────────────────[/meta]"
    )

    console.print(
        "[success]✓[/success] CommitDev has been uninstalled."
    )

    if sys.platform == "win32":

        console.print(
            "[meta]Restart PowerShell or Windows Terminal to refresh PATH.[/meta]"
        )

    else:

        console.print(
            "[meta]Restart your terminal session to complete removal.[/meta]"
        )


if __name__ == "__main__":
    app()