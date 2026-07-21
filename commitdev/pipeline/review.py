from rich.panel import Panel

from commitdev.pipeline.utils import prompt_select


class ReviewHub:
    """
    Interactive Review Hub.

    Displays the current publishing state and lets the
    user choose the next action.
    """

    MENU = [
        "Edit Content",
        "Regenerate Draft",
        "Manage Images",
       # "Manage Platforms",
        "Publish",
        "Cancel",
    ]

    def __init__(self, context):
        self.ctx = context

    # --------------------------------------------------
    # Build Summary
    # --------------------------------------------------

    def _platform_summary(self):
        lines = []

        if not self.ctx.staged_platforms:
            return "[red]No target platforms selected[/red]"

        for platform in self.ctx.staged_platforms:

            content = self.ctx.posts_by_platform.get(
                platform.lower(),
                "",
            )

            preview = content.strip()

            if len(preview) > 180:
                preview = preview[:180] + "..."

            lines.append(
                f"[cyan]• {platform}[/cyan]\n"
                f"{preview}\n"
            )

        return "\n".join(lines)

    def _images_summary(self):

        if not self.ctx.attached_images:
            return "None"

        result = []

        for image in self.ctx.attached_images:

            if str(image).startswith("http"):
                result.append("Remote Image")
            else:
                result.append(str(image).split("/")[-1])

        return ", ".join(result)

    # --------------------------------------------------
    # Render
    # --------------------------------------------------

    def render(self):

        summary = (
            f"[white]Repository:[/white] {self.ctx.repository}\n"
            f"[white]Commit:[/white] {self.ctx.commit_message}\n"
            f"[white]Images:[/white] {self._images_summary()}\n\n"
            f"[white]Platform Drafts[/white]\n\n"
            f"{self._platform_summary()}"
        )

        self.ctx.console.print(
            Panel(
                summary,
                title="[brand]POST REVIEW[/brand]",
                border_style="grey39",
            )
        )

    # --------------------------------------------------
    # Ask user
    # --------------------------------------------------

    def prompt(self):

        self.render()

        choice = prompt_select(
            self.MENU,
            "Choose an action:",
        )

        return choice.lower()