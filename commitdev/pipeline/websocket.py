import json

import websockets

from commitdev.pipeline.context import PipelineContext
from commitdev.pipeline.dispatcher import EventDispatcher


class WebSocketClient:
    """
    CommitDev websocket client.

    Responsible only for:

    • connecting
    • authenticating
    • receiving events
    • sending events
    """

    def __init__(
        self,
        websocket_url: str,
        
    ):
        self.websocket_url = websocket_url
        

        self.ws = None
        self.dispatcher = None

    # --------------------------------------------------
    # Connection
    # --------------------------------------------------

    async def connect(self):

        self.ws = await websockets.connect(
            self.websocket_url
            
        )

    async def close(self):

        if self.ws:

            await self.ws.close()

    # --------------------------------------------------
    # Context
    # --------------------------------------------------

    def bind_context(
        self,
        context: PipelineContext,
    ):

        context.ws = self.ws

        self.dispatcher = EventDispatcher(context)

    # --------------------------------------------------
    # Messaging
    # --------------------------------------------------

    async def send(self, payload: dict):

        await self.ws.send(
            json.dumps(payload)
        )

    async def receive(self):

        return await self.dispatcher.receive()

    # --------------------------------------------------
    # Wait for next draft
    # --------------------------------------------------

    async def wait_for_draft(self):

        while True:

            payload = await self.receive()

            if payload.get("status") == "draft_saved":
                return payload