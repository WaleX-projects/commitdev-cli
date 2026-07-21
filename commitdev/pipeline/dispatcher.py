import json

from commitdev.pipeline.context import PipelineContext


class EventDispatcher:
    """
    Routes websocket events to the correct pipeline handler.
    """

    def __init__(self, ctx: PipelineContext):
        self.ctx = ctx

    async def receive(self):
        """
        Wait for the next websocket message.
        """

        raw = await self.ctx.ws.recv()

        data = json.loads(raw)

        self.ctx.last_server_payload = data

        return await self.dispatch(data)

    async def dispatch(self, message: dict):
        """
        Dispatch a websocket message.
        """

        payload = message.get("payload", {})

        status = payload.get("status")

        if status == "draft_saved":
            return self._draft_saved(payload)

        elif status == "draft_updated":
            return self._draft_updated(payload)

        elif status == "draft_regenerated":
            return self._draft_regenerated(payload)

        elif status == "image_uploaded":
            return self._image_uploaded(payload)

        elif status == "publishing_started":
            return self._publishing_started(payload)

        elif status == "published":
            return self._published(payload)

        return payload

    # ----------------------------------------------------
    # Handlers
    # ----------------------------------------------------

    def _draft_saved(self, payload):

        self.ctx.post_id = payload["post_id"]

        self.ctx.posts_by_platform = payload.get(
            "posts_by_platform",
            {},
        )

        self.ctx.staged_platforms = payload.get(
            "staged_platforms",
            [],
        )

        return payload

    def _draft_updated(self, payload):

        platform = payload["platform"]

        self.ctx.posts_by_platform[
            platform
        ] = payload["content"]

        return payload

    def _draft_regenerated(self, payload):

        platform = payload["platform"]

        self.ctx.posts_by_platform[
            platform
        ] = payload["content"]

        return payload

    def _image_uploaded(self, payload):

        return payload

    def _publishing_started(self, payload):

        return payload

    def _published(self, payload):

        return payload