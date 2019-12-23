from channels.consumer import AsyncConsumer
from channels.db import database_sync_to_async


class VisualCellEditConsumer(AsyncConsumer):

    """A websocket means of updating neighbours on edits in real time."""

    async def connect(self, event):
        """Manage connecting cell neighbours."""
        print('connected', event)
        await self.send({
            "type": "websocket.accept"
        })
        await self.send({
            "type": "websocket.send",
            "text": "Hello world"
        })

    async def recieve(self, event):
        """Manage messages sent to cell neighbours."""
        print('recieve', event)

    async def disconnect(self, event):
        """Manage connecting cell neighbours."""
        print('disconnected', event)
