import sys
from importlib.metadata import version, PackageNotFoundError

import typer
from rich.console import Console
from rich.theme import Theme

# ==========================================
# CommitDev Theme
# ==========================================
commitdev_theme = Theme({
    "brand": "bold spring_green3",
    "success": "spring_green3",
    "meta": "dim grey39",
    "command": "bold white",
    "error": "bold red",
    "warn": "bold yellow",
})

console = Console(
    theme=commitdev_theme,
    highlight=False,
)

# ==========================================
# CommitDev Version
# ==========================================
try:
    __version__ = version("commitdev")
except PackageNotFoundError:
    __version__ = "development"


def version_callback(value: bool):
    """Display the installed CommitDev version."""
    if value:
        console.print(
            f"[brand]CommitDev[/brand] "
            f"[meta]CLI[/meta] "
            f"[success]v{__version__}[/success]"
        )
        raise typer.Exit()


# ==========================================
# Global Error Handler
# ==========================================
def commitdev_exception_handler(exc_type, exc_value, exc_traceback):
    """Intercept raw exceptions and display a clean CommitDev error."""

    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    console.print(
        "\n[error]✕ System Error Blocked Command Sequence[/error]"
    )
    console.print(
        f"  [meta]Reason ›[/meta] [white]{exc_value}[/white]"
    )
    console.print(
        "[meta]──────────────────────────────────────────────────[/meta]\n"
    )

    sys.exit(1)


sys.excepthook = commitdev_exception_handler

# ==========================================
# Commands
# ==========================================
from commitdev.commands.auth import (
    login,
    logout,
    whoami,
    doctor 
)

from commitdev.commands.status import (
    status,
    activity,
    
)

""""from commitdev.commands.drafts import (
    drafts,
    draft,
    approve,
    regenerate,
    listen_for_drafts,
)
"""
from commitdev.commands.posts import (
    posts,
    post,
)

from commitdev.commands.repos import (
    repos,
    repo,
    sync,
)

from commitdev.commands.setup import (
    setup,
    uninstall,
)

from commitdev.commands.analytics import analytics
from commitdev.commands.integrations import integrations

from commitdev.commands.drafter import (
    #drafts,
    #draft,
    #approve,
   # regenerate,
   listen_for_drafts
)

# ==========================================
# CLI
# ==========================================
app = typer.Typer(
    no_args_is_help=True,
    add_completion=False,
)


@app.callback()
def main(
    version: bool = typer.Option(
        False,
        "--version",
        "-v",
        help="Show the installed CommitDev version.",
        callback=version_callback,
        is_eager=True,
    ),
):
    """
    CommitDev CLI
    """
    pass


# ==========================================
# Authentication
# ==========================================
app.command()(login)
app.command()(logout)
app.command()(whoami)
app.command()(doctor)

# ==========================================
# Status
# ==========================================
app.command()(status)
app.command()(activity)


# ==========================================
# Drafts
# ==========================================

#app.command()(drafts)
#app.command()(draft)
#app.command()(approve)
#app.command()(regenerate)
app.command()(listen_for_drafts)

# ==========================================
# Posts
# ==========================================
app.command()(posts)
app.command()(post)

# ==========================================
# Repositories
# ==========================================
app.command()(repos)
app.command()(repo)
app.command()(sync)

# ==========================================
# Analytics
# ==========================================
app.command()(analytics)

# ==========================================
# Integrations
# ==========================================
app.command()(integrations)

# ==========================================
# Setup & Uninstall
# ==========================================
app.command()(setup)
app.command()(uninstall)

# ==========================================
# Entry Point
# ==========================================
if __name__ == "__main__":
    app()