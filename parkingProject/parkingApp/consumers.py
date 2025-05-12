import json
from channels.generic.websocket import AsyncWebsocketConsumer

class VideoConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = "video_stream"

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
        print("[INFO] WebSocket connected.")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        print("[INFO] WebSocket disconnected.")

    async def receive(self, event):
        print("[INFO] Message received in WebSocket:")
        frame_data = event.get("text_data")
        
        if frame_data:
            await self.send(text_data=frame_data)
            print("[INFO] Frame sent to client.")
