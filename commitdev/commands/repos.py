import typer
from rich.console import Console
from rich.theme import Theme
from commitdev.api import get, post

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


def repos():
    """
    List all repositories connected to your CommitDev account.

    Displays every synchronized repository, including its
    ID, name, and current sync status.
    """
    console.print("\n[brand]CommitDev[/brand] [meta]•[/meta] Tracked Codebases")
    console.print("[meta]──────────────────────────────────────────────────[/meta]")

    with console.status("[meta]Loading connected repository mappings...[/meta]", spinner="simpleDots"):
        try:
            repositories = get("/cli/repos/")
        except Exception as e:
            console.print(f"  [error]✕ History mapping aborted:[/error] [meta]{e}[/meta]\n")
            return

    if not repositories:
        console.print("  [meta]- No codebase source points linked to this profile[/meta]\n")
        return

    for repo in repositories:
        status = repo.get('status', '').upper()
        status_style = "success" if status in ["ACTIVE", "SYNCED", "OK"] else "warn"

        console.print(
            f"  [meta]›[/meta] ID: [white]{repo.get('id'):<4}[/white] "
            f"[meta]│[/meta] Context: [white]{repo.get('name'):<24}[/white] "
            f"[meta]│[/meta] State: [{status_style}]{status}[/{status_style}]"
        )

    console.print("[meta]──────────────────────────────────────────────────[/meta]\n")


def repo(id: int):
    """
    Show detailed information about a connected repository.

    Displays repository statistics including its current
    status, total commits processed, drafts generated,
    and published posts.
    """
    console.print(f"\n[brand]CommitDev[/brand] [meta]•[/meta] Repository Node #{id}")
    console.print("[meta]──────────────────────────────────────────────────[/meta]")

    with console.status(f"[meta]Extracting telemetry matrix for node #{id}...[/meta]", spinner="simpleDots"):
        try:
            data = get(f"/cli/repos/{id}/")
        except Exception as e:
            console.print(f"  [error]✕ Telemetry extraction failed:[/error] [meta]{e}[/meta]\n")
            return

    status = data.get('status', '').upper()
    status_style = "success" if status in ["ACTIVE", "SYNCED", "OK"] else "warn"

    console.print(f"  [meta]›[/meta] Node ID         [meta]›[/meta] [white]{data.get('id')}[/white]")
    console.print(f"  [meta]›[/meta] Repository Name [meta]›[/meta] [white]{data.get('name')}[/white]")
    console.print(f"  [meta]›[/meta] Status State    [meta]›[/meta] [{status_style}]{status}[/{status_style}]")
    
    console.print("\n[white]Activity Counters[/white]")
    console.print(f"  Commits Checked  [meta]›[/meta] {data.get('commits', 0)}")
    console.print(f"  Drafts Staged    [meta]›[/meta] {data.get('drafts', 0)}")
    console.print(f"  Published Posts  [meta]›[/meta] [success]{data.get('posts', 0)}[/success]")
    console.print("[meta]──────────────────────────────────────────────────[/meta]\n")


def sync(id: int):
    """
    Synchronize a repository with CommitDev.

    Fetches the latest repository information from GitHub
    and updates CommitDev with any new commits, branches,
    or metadata.
    """
    console.print(f"\n[brand]CommitDev[/brand] [meta]•[/meta] Workspace Sync Pipeline")
    console.print("[meta]──────────────────────────────────────────────────[/meta]")

    with console.status(f"[meta]Re-indexing GitHub reference graphs for node #{id}...[/meta]", spinner="simpleDots"):
        try:
            result = post(f"/cli/repos/{id}/sync/")
            console.print(f"  [success]✓[/success] [white]{result.get('message', 'Synchronization finalized.')}[/white]\n")
        except Exception as e:
            console.print(f"  [error]✕ Synchronization transaction dropped:[/error] [meta]{e}[/meta]\n")
