import asyncio
import io
import json
import urllib.request
from pathlib import Path
from urllib.parse import urlparse

from PIL import Image
from rich.progress import (
    Progress,
    SpinnerColumn,
    BarColumn,
    TextColumn,
)
from rich_pixels import Pixels

from commitdev.pipeline.context import PipelineContext
from commitdev.pipeline.utils import (
    console,
    prompt_select,
    success,
    error,
    info,
    section,
)


class ImageManager:

    def __init__(self, ctx: PipelineContext):
        self.ctx = ctx

    async def menu(self):
        """
        Interactive image manager.
        """

        while True:

            section("MEDIA MANAGER")

            console.print(
                f"Attached Images: [white]{self.ctx.image_count}[/white]\n"
            )

            options = [
                "Add Image",
            ]

            if self.ctx.image_count:
                options.extend(
                    [
                        "View Images",
                        "Clear Images",
                    ]
                )

            options.append("Back")

            action = prompt_select(
                options,
                "Choose an action:",
            )

            if action == "Back":
                return

            elif action == "Add Image":
                await self.add_image()

            elif action == "View Images":
                self.view_images()

            elif action == "Clear Images":
                self.ctx.clear_images()
                success("Images cleared.")

    async def add_image(self):

        console.print(
            "\nPaste an image URL or local file path:\n"
        )

        value = input("> ").strip()

        if not value:
            return

        if value.startswith(("http://", "https://")):
            await self._download_remote(value)
        else:
            await self._use_local(Path(value))

    async def _use_local(self, path: Path):

        if not path.exists():
            error("File does not exist.")
            return

        self.preview(path)

        await self.upload(str(path))

        self.ctx.add_image(path)

        success("Image attached.")

    async def _download_remote(self, url: str):

        try:

            parsed = urlparse(url)

            if not parsed.netloc:
                raise ValueError

        except Exception:

            error("Invalid URL.")

            return

        with Progress(
            SpinnerColumn(),
            BarColumn(),
            TextColumn(
                "[progress.percentage]{task.percentage:>3.0f}%"
            ),
            console=console,
        ) as progress:

            task = progress.add_task(
                "Downloading...",
                total=100,
            )

            req = urllib.request.Request(
                url,
                headers={
                    "User-Agent": "Mozilla/5.0"
                },
            )

            with urllib.request.urlopen(req) as response:

                image_bytes = response.read()

            while not progress.finished:
                await asyncio.sleep(0.01)
                progress.update(task, advance=10)

        self.preview(io.BytesIO(image_bytes))

        await self.upload(url)

        self.ctx.add_image(url)

        success("Remote image attached.")

    async def upload(self, image):

        await self.ctx.ws.send(
            json.dumps(
                {
                    "action": "upload_images",
                    "post_id": self.ctx.post_id,
                    "image": image,
                }
            )
        )

        response = await self.ctx.ws.recv()

        self.ctx.last_server_payload = json.loads(response)

    def view_images(self):

        section("ATTACHED IMAGES")

        if not self.ctx.attached_images:

            info("No images attached.")

            return

        for image in self.ctx.attached_images:

            console.print(f"• {image}")

    def preview(self, source):

        try:

            image = Image.open(source)

            if image.mode not in ("RGB", "RGBA"):
                image = image.convert("RGBA")

            width = 48

            ratio = image.height / image.width

            height = max(
                1,
                int(width * ratio * 0.5),
            )

            image = image.resize((width, height))

            console.print(Pixels.from_image(image))

        except Exception:

            info("Preview unavailable.")