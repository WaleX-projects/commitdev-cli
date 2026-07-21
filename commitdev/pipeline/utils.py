from typing import List

from rich.console import Console
from rich.theme import Theme

# ---------------------------------------------------------
# CommitDev Theme
# ---------------------------------------------------------

commitdev_theme = Theme(
    {
        "brand": "bold spring_green3",
        "success": "spring_green3",
        "meta": "dim grey39",
        "command": "bold white",
        "error": "bold red",
        "warn": "bold yellow",
    }
)

console = Console(
    theme=commitdev_theme,
    highlight=False,
)

# ---------------------------------------------------------
# Menu Helpers
# ---------------------------------------------------------


def prompt_select(options: List[str], message: str) -> str:
    """
    Display a numbered menu and return the selected option.
    """

    console.print(f"\n[white]{message}[/white]\n")

    for index, option in enumerate(options, start=1):
        console.print(
            f"  [brand]{index}[/brand] [meta]›[/meta] {option}"
        )

    while True:
        try:
            value = input("\n> ").strip()

            selected = int(value)

            if 1 <= selected <= len(options):
                return options[selected - 1]

        except ValueError:
            pass

        console.print(
            "[error]✕ Invalid option. Please choose one of the numbers above.[/error]"
        )


# ---------------------------------------------------------
# Printing Helpers
# ---------------------------------------------------------


def divider():
    console.print(
        "[meta]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/meta]"
    )


def section(title: str):
    console.print(f"\n[brand]{title}[/brand]")
    divider()


def success(message: str):
    console.print(f"[success]✓[/success] {message}")


def warning(message: str):
    console.print(f"[warn]⚠[/warn] {message}")


def error(message: str):
    console.print(f"[error]✕[/error] {message}")


def info(message: str):
    console.print(f"[meta]›[/meta] {message}")


# ---------------------------------------------------------
# Formatting Helpers
# ---------------------------------------------------------


def format_platform(platform: str) -> str:
    """
    linkedin -> LinkedIn
    x -> X
    dev.to -> Dev.to
    medium -> Medium
    """

    mapping = {
        "linkedin": "LinkedIn",
        "x": "X",
        "dev.to": "Dev.to",
        "medium": "Medium",
    }

    return mapping.get(platform.lower(), platform.title())


def format_platform_list(platforms: List[str]) -> str:
    if not platforms:
        return "None"

    return ", ".join(
        format_platform(platform)
        for platform in platforms
    )