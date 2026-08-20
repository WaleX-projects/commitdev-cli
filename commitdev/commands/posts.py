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

app = typer.Typer(help="Manage published posts")

@app.command("list")
def list_posts():
    """
    List your published CommitDev posts.

    Displays a history of published posts, including their
    ID, publishing status, and the platforms where each post
    was successfully delivered.
    """
    console.print("\n[brand]CommitDev[/brand] [meta]•[/meta] Publication Ledger")
    console.print("[meta]──────────────────────────────────────────────────[/meta]")

    with console.status("[meta]Loading published historical logs...[/meta]", spinner="simpleDots"):
        try:
            data = get("/cli/posts/")
        except Exception as e:
            console.print(f"  [error]✕ History retrieval aborted:[/error] [meta]{e}[/meta]\n")
            return

    if not data:
        console.print("  [meta]- No published historical entries found on this profile[/meta]\n")
        return

    for post in data:
        post_id = post.get('id')
        status = post.get('overall_status', '-').upper()
        platforms = post.get('published_platforms', [])
        
        platform_str = ", ".join(platforms) if platforms else "None"
        status_style = "success" if status in ["POSTED", "PUBLISHED", "SUCCESS"] else "warn"

        console.print(
            f"  [meta]›[/meta] ID: [white]{post_id:<4}[/white] "
            f"[meta]│[/meta] Status: [{status_style}]{status:<8}[/{status_style}] "
            f"[meta]│[/meta] Distribution: [white]{platform_str}[/white]"
        )

    console.print("[meta]──────────────────────────────────────────────────[/meta]\n")

@app.command("show")
def post(id: int):
    """
    Show the details and performance of a published post.

    Displays the full content of a published post, its
    publishing status, delivery platforms, and engagement
    metrics such as likes, comments, and shares.
    """
    console.print(f"\n[brand]CommitDev[/brand] [meta]•[/meta] Historical Node #{id}")
    console.print("[meta]──────────────────────────────────────────────────[/meta]")

    with console.status(f"[meta]Extracting content and analytics for node #{id}...[/meta]", spinner="simpleDots"):
        try:
            data = get(f"/cli/posts/{id}/")
        except Exception as e:
            console.print(f"  [error]✕ Metrics extraction failed:[/error] [meta]{e}[/meta]\n")
            return

    status = data.get('overall_status', '-').upper()
    status_style = "success" if status in ["POSTED", "PUBLISHED", "SUCCESS"] else "warn"
    
    platforms_list = data.get('platforms', [])
    platform_names = [p.get('provider') for p in platforms_list]
    platform_str = ", ".join(platform_names) if platform_names else "None"

    console.print(f"  [meta]›[/meta] Node ID         [meta]›[/meta] [white]{data.get('id')}[/white]")
    console.print(f"  [meta]›[/meta] State Flag      [meta]›[/meta] [{status_style}]{status}[/{status_style}]")
    console.print(f"  [meta]›[/meta] Target Channels  [meta]›[/meta] {platform_str}")
    
    console.print("\n[white]Aggregated Visibility Statistics[/white]")
    console.print(f"  Likes            [meta]›[/meta] [white]{data.get('total_likes', 0)}[/white]")
    console.print(f"  Comments         [meta]›[/meta] {data.get('total_comments', 0)}")
    console.print(f"  Shares           [meta]›[/meta] {data.get('total_shares', 0)}")

    # Clean, structural cross-platform breakdown display loop
    if len(platforms_list) > 1:
        console.print("\n[white]Cross-Platform Engagement Breakdown[/white]")
        for p in platforms_list:
            console.print(
                f"  [meta]›[/meta] [white]{p.get('provider'):<12}[/white] "
                f"[meta]│[/meta] Likes: {p.get('likes', 0):<3} "
                f"[meta]│[/meta] Comments: {p.get('comments', 0):<3} "
                f"[meta]│[/meta] Shares: [success]{p.get('shares', 0)}[/success]"
            )

    console.print("[meta]──────────────────────────────────────────────────[/meta]")
    console.print("[white]Published Document Content Body:[/white]\n")
    console.print(data.get("final_post_content", "[meta]No text content found inside this artifact entry.[/meta]"))
    console.print("[meta]──────────────────────────────────────────────────[/meta]\n")
