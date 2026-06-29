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


def status():
    """
    Show the status of your most recent CommitDev deployment.

    Displays the latest repository, commit, overall publishing status,
    commit SHA, and the delivery status for every connected platform.
    """
    console.print("\n[brand]CommitDev[/brand] [meta]•[/meta] Pipeline Status")
    console.print("[meta]──────────────────────────────────────────────────[/meta]")

    with console.status("[meta]Loading latest deployment parameters...[/meta]", spinner="simpleDots"):
        try:
            data = get("/cli/status/")
        except Exception as e:
            console.print(f"  [error]✕ Status retrieval aborted:[/error] [meta]{e}[/meta]\n")
            return

    if data.get("status") == "no_posts":
        console.print("  [meta]- No deployment history found for this account[/meta]\n")
        return

    sha_suffix = f" [meta]({data.get('commit_sha')})[/meta]" if data.get('commit_sha') else ""
    console.print(f"Repository   [meta]›[/meta] [white]{data.get('repository', '-')}[/white]{sha_suffix}")
    console.print(f"Last Commit  [meta]›[/meta] {data.get('last_commit', '-')}")
    
    overall = data.get('overall_status', '-').upper()
    overall_style = "success" if overall in ["POSTED", "PUBLISHED", "SUCCESS"] else "error" if overall == "FAILED" else "warn"
    console.print(f"Pipeline     [meta]›[/meta] [{overall_style}]{overall}[/{overall_style}]")
    console.print("[meta]──────────────────────────────────────────────────[/meta]")
    
    console.print("[white]Platform Deliveries[/white]")
    platforms_list = data.get("platforms", [])

    if not platforms_list:
        console.print("  [meta]- No target delivery nodes linked to this push[/meta]")
    else:
        for p in platforms_list:
            provider = p.get("provider", "-")
            delivery_status = p.get("delivery_status", "-")
            username = p.get("username", "")
            
            user_str = f" [meta]({username})[/meta]" if username else ""
            
            if delivery_status in ["published", "posted"]:
                status_indicator = "[success]✓[/success]"
            elif delivery_status == "failed":
                status_indicator = "[error]✕[/error]"
            else:
                status_indicator = "[warn]•[/warn]"

            console.print(f"  {status_indicator} [white]{provider}[/white]{user_str} [meta]──[/meta] {delivery_status}")
            
            if p.get("error_message"):
                console.print(f"     [error]↳ Error:[/error] [meta]{p['error_message']}[/meta]")

    console.print("[meta]──────────────────────────────────────────────────[/meta]\n")


def activity():
    """
    Show your recent CommitDev publishing activity.

    Lists recent posts and drafts created from your commits,
    including the repository, commit message, commit SHA,
    overall status, and delivery status for each platform.
    """
    console.print("\n[brand]CommitDev[/brand] [meta]•[/meta] Recent Activity")
    console.print("[meta]──────────────────────────────────────────────────[/meta]")

    with console.status("[meta]Loading pipeline activity timeline...[/meta]", spinner="simpleDots"):
        try:
            activities = get("/cli/activity/")
        except Exception as e:
            console.print(f"  [error]✕ Activity stream aborted:[/error] [meta]{e}[/meta]\n")
            return

    if not activities:
        console.print("  [meta]- No historic logs found for active repository context[/meta]\n")
        return

    for act in activities:
        repo = act.get("repository", "-")
        status = act.get("overall_status", "draft").upper()
        commit = act.get("commit_message", "-")
        sha = act.get("commit_sha", "-------")

        status_style = "success" if status == "POSTED" else "error" if status == "FAILED" else "warn"
        status_tag = f"[{status_style}]{status}[/{status_style}]"

        platform_tags = []
        for p in act.get("platforms", []):
            p_provider = p.get("provider", "")
            p_status = p.get("status", "")
            p_style = "success" if p_status == "published" else "error" if p_status == "failed" else "meta"
            platform_tags.append(f"[{p_style}]{p_provider}[/{p_style}]")
        
        platforms_str = f" [meta]•[/meta] {', '.join(platform_tags)}" if platform_tags else ""

        console.print(f"  [meta]›[/meta] {status_tag} [white]{repo}[/white] [meta]({sha})[/meta]{platforms_str}")
        console.print(f"    [meta]↳ {commit.strip()}[/meta]")
        console.print("[meta]──────────────────────────────────────────────────[/meta]")

    console.print()
