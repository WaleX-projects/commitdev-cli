import typer
from rich.console import Console
from rich.theme import Theme
from commitdev.api import get

# Official CommitDev styling engine matching your custom UI
commitdev_theme = Theme({
    "brand": "bold spring_green3",   # Primary mint/emerald color signature
    "success": "spring_green3",
    "meta": "dim grey39",            # Secondary layout accent gray 
    "command": "bold white",
    "error": "bold red",
    "warn": "bold yellow"
})

console = Console(theme=commitdev_theme, highlight=False)

def analytics():
    """Fetches and displays high-level account visibility performance data."""
    console.print("\n[brand]CommitDev[/brand] [meta]•[/meta] Workspace Performance Insights")
    console.print("[meta]──────────────────────────────────────────────────[/meta]")

    with console.status("[meta]Compiling latest account metrics across distribution nodes...[/meta]", spinner="simpleDots"):
        try:
            data = get("/cli/analytics/")
        except Exception as e:
            console.print(f"  [error]✕ Analytics command aborted:[/error] [meta]{e}[/meta]\n")
            return

    # Print out global metric data lines cleanly
    console.print(f"Total Published Artifacts [meta]›[/meta] [white]{data.get('posts', 0)}[/white]")
    console.print(f"Aggregated Impressions    [meta]›[/meta] {data.get('impressions', 0)}")
    console.print(f"Audience Engagement Loop  [meta]›[/meta] {data.get('engagement', 0)}")
    console.print(f"Global Follower Matrix    [meta]›[/meta] [success]{data.get('followers', 0)}[/success]")
    console.print("[meta]──────────────────────────────────────────────────[/meta]")

    console.print("[white]Top Synchronized Repositories[/white]")
    top_repos = data.get("top_repos", [])

    if not top_repos:
        console.print("  [meta]- No codebase data history linked to your profile metrics yet[/meta]\n")
        return

    for repo in top_repos:
        repo_name = repo.get('name', '-')
        # Structured alignment display layout
        console.print(
            f"[meta]›[/meta] [white]{repo_name:<24}[/white] "
            f"[meta]│[/meta] Posts: {repo.get('posts', 0):<3} "
            f"[meta]│[/meta] Engagement: [success]{repo.get('engagement', 0)}[/success]"
        )

    console.print("[meta]──────────────────────────────────────────────────[/meta]\n")
