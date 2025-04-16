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

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        frame = text_data  # מקבלים את הפריים
        await self.send(text_data=json.dumps({
            'frame': frame  # שולחים את הפריים כ־JSON
        }))
