# commitdev/console.py

from rich.console import Console
from rich.theme import Theme

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