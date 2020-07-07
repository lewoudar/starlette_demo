import asyncio
import typing

from starlette.endpoints import WebSocketEndpoint
from starlette.types import Scope, Receive, Send
from starlette.websockets import WebSocket


class Feed(WebSocketEndpoint):
    encoding = 'json'

    def __init__(self, scope: Scope, receive: Receive, send: Send) -> None:
        super().__init__(scope, receive, send)
        self.channel: typing.Optional[asyncio.Queue] = None
        self.task: typing.Optional[asyncio.Task] = None

    async def reader(self, websocket: WebSocket) -> None:
        while True:
            message = await self.channel.get()
            await websocket.send_json(message)
            self.channel.task_done()

    async def on_connect(self, websocket: WebSocket) -> None:
        self.channel = asyncio.Queue()
        self.scope['app'].state.channels.add(self.channel)
        self.task = asyncio.create_task(self.reader(websocket))
        await websocket.accept()

    async def on_disconnect(self, websocket: WebSocket, close_code: int) -> None:
        self.scope['app'].state.channels.remove(self.channel)
        await self.channel.join()
        self.task.cancel()
        # we want to be sure task is cancelled before leaving the websocket
        await asyncio.gather(self.task, return_exceptions=True)
        await websocket.close()
