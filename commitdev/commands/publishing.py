import asyncio
import sys
import typer

from commitdev.config import get_token
from commitdev.api import BASE_URL_WSS
from commitdev.pipeline.context import PipelineContext
from commitdev.pipeline.websocket import WebSocketClient
from commitdev.pipeline.review import ReviewHub
from commitdev.pipeline.draft_flow import DraftFlow
from commitdev.pipeline.images import ImageManager
from commitdev.pipeline.publisher import Publisher
from commitdev.pipeline.console import console



def fetch_fresh_token():
    """Retrieves local authentication credential token mappings."""
    try:
        token_data = get_token()
        token = token_data.get('access_token') if isinstance(token_data, dict) else token_data
        if not token:
            raise ValueError("Authentication storage empty.")
        return token
    except Exception as e:
        console.print(f"\n  [error]✕ Configuration Drop:[/error] Local profile token invalid: [meta]{e}[/meta]\n")
        sys.exit(1)
        

async def run():

    token = fetch_fresh_token()
    WS_URL = f"{BASE_URL_WSS}/drafts/?token={token}"
    
    
    client = WebSocketClient(
        websocket_url=WS_URL,
    )

    await client.connect()

    ctx = PipelineContext()

    client.bind_context(ctx)

    review = ReviewHub(ctx)
    drafts = DraftFlow(ctx)
    images = ImageManager(ctx)
    publisher = Publisher(ctx)

    while True:

        ctx.console.print(
            "\n[brand]Waiting for new drafts or Ctr+C to cancel...[/brand]"
        )

        await client.wait_for_draft()

        while True:

            choice = review.prompt()

            if choice == "edit content":

                await drafts.edit()

            elif choice == "regenerate draft":

                await drafts.regenerate()

            elif choice == "manage images":

                await images.menu()

            elif choice == "manage platforms":

                # we'll add PlatformManager later
                pass

            elif choice == "publish":

                success = await publisher.publish()

                if success:
                    break

            elif choice == "cancel":

                break


def watch():
    """
    Long-running websocket worker.
    """
    asyncio.run(run())