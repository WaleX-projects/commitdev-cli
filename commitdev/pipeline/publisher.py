import json

from commitdev.pipeline.context import PipelineContext


class Publisher:
    """
    Handles publishing the current draft.
    """

    def __init__(self, ctx: PipelineContext):
        self.ctx = ctx

    async def publish(self) -> bool:
        """
        Publish the current draft.

        Returns:
            True if publishing succeeded.
            False otherwise.
        """

        console = self.ctx.console

        console.print(
            "\n[brand]🚀 TRANSMITTING DEPLOYMENT[/brand]"
        )

        #
        # STEP 1
        # Queue publishing
        #

        try:

            with console.status(
                "[meta]Dispatching publish task...[/meta]"
            ):

                await self.ctx.ws.send(
                    json.dumps(
                        {
                            "action": "publish_draft",
                            "post_id": self.ctx.post_id,
                        }
                    )
                )

                response = json.loads(
                    await self.ctx.ws.recv()
                )

        except Exception as exc:

            console.print(
                f"\n[error]✕ Queue failed:[/error] {exc}\n"
            )

            return False

        payload = response.get("payload", {})

        if payload.get("status") != "publishing_started":

            console.print(
                "\n[error]✕ Server rejected publish request.[/error]\n"
            )

            return False

        console.print(
            "[success]✓ Publishing task queued.[/success]"
        )

        #
        # STEP 2
        # Wait until Celery finishes
        #

        try:

            with console.status(
                "[meta]Publishing...[/meta]"
            ):

                response = json.loads(
                    await self.ctx.ws.recv()
                )

        except Exception as exc:

            console.print(
                f"\n[error]✕ Connection lost:[/error] {exc}\n"
            )

            return False

        payload = response.get("payload", {})

        #
        # STEP 3
        #

        if payload.get("status") != "published":

            console.print(
                "\n[error]✕ Publishing failed.[/error]"
            )

            if payload.get("error"):
                console.print(payload["error"])

            return False

        self._display_results(payload)

        return True

    def _display_results(self, payload):

        console = self.ctx.console

        console.print(
            f"\n[success]✓ Draft #{self.ctx.post_id} published.[/success]\n"
        )

        successful = payload.get(
            "platforms",
            [],
        )

        failed = payload.get(
            "failed_platforms",
            [],
        )

        urls = payload.get(
            "urls",
            {},
        )

        if successful:

            console.print(
                "[bold green]Successful Platforms[/bold green]"
            )

            for platform in successful:

                url = urls.get(platform)

                if url:

                    console.print(
                        f"  • {platform.upper()}"
                    )

                    console.print(
                        f"    {url}"
                    )

                else:

                    console.print(
                        f"  • {platform.upper()}"
                    )

        if failed:

            console.print(
                "\n[bold red]Failed Platforms[/bold red]"
            )

            for platform in failed:

                console.print(
                    f"  • {platform.upper()}"
                )

        console.print("")
        
        
        
        
        