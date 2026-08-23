# commitdev/pipeline/draft_flow.py

import asyncio
import json

from .editor import open_in_editor
from .utils import prompt_select


class DraftFlow:
    """
    Handles all draft editing operations.
    """

    def __init__(self, ctx):
        self.ctx = ctx

    # --------------------------------------------------
    # Choose Platform
    # --------------------------------------------------

    def choose_platform(self):
        if not self.ctx.staged_platforms:
            self.ctx.console.print(
                "\n[error]No active platforms available.[/error]\n"
            )
            return None

        return prompt_select(
            self.ctx.staged_platforms,
            "Select a platform:"
        )

    # --------------------------------------------------
    # Edit Draft
    # --------------------------------------------------

    async def edit(self,draft_id = None):
        platform = self.choose_platform()

        if platform is None:
            return

        key = platform.lower()

        if draft_id:
            current = 
        current = self.ctx.posts_by_platform.get(key, "")

        template = (
            "# ---------------------------------------------\n"
            "# CommitDev Editor\n"
            "# Lines beginning with # are ignored.\n"
            "# Save and exit when finished.\n"
            "# ---------------------------------------------\n\n"
            f"{current}\n"
        )

        loop = asyncio.get_running_loop()

        edited = await loop.run_in_executor(
            None,
            open_in_editor,
            template,
            self.ctx.console,
        )

        if edited is None:
            return

        edited = "\n".join(
            line
            for line in edited.splitlines()
            if not line.strip().startswith("#")
        ).strip()

        with self.ctx.console.status(
            "[meta]Uploading draft...[/meta]"
        ):

            await self.ctx.ws.send(
                json.dumps(
                    {
                        "action": "update_draft",
                        "post_id": self.ctx.post_id,
                        "platform": key,
                        "content": edited,
                    }
                )
            )

            response = json.loads(await self.ctx.ws.recv())

        payload = response.get("payload", {})

        self.ctx.posts_by_platform[key] = payload.get(
            "content",
            edited,
        )

        self.ctx.console.print(
            f"[success]✓ {platform} draft updated.[/success]"
        )

    # --------------------------------------------------
    # Regenerate Draft
    # --------------------------------------------------

    async def regenerate(self):
        platform = self.choose_platform()

        if platform is None:
            return

        key = platform.lower()

        with self.ctx.console.status(
            "[meta]Regenerating draft...[/meta]"
        ):

            await self.ctx.ws.send(
                json.dumps(
                    {
                        "action": "regenerate_draft",
                        "post_id": self.ctx.post_id,
                        "platform": key,
                    }
                )
            )

            response = json.loads(await self.ctx.ws.recv())

        payload = response.get("payload", {})

        self.ctx.posts_by_platform[key] = payload.get(
            "content",
            self.ctx.posts_by_platform.get(key, ""),
        )

        self.ctx.console.print(
            f"[success]✓ {platform} regenerated.[/success]"
        )

    # --------------------------------------------------
    # Get Draft Content
    # --------------------------------------------------

    def get_content(self, platform):
        return self.ctx.posts_by_platform.get(
            platform.lower(),
            "",
        )

    # --------------------------------------------------
    # Set Draft Content
    # --------------------------------------------------

    def set_content(self, platform, content):
        self.ctx.posts_by_platform[
            platform.lower()
        ] = content