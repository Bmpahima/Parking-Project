import asyncio
import base64
import cv2
from channels.generic.websocket import AsyncWebsocketConsumer
from .shared_frame import latest_processed_frame  

class VideoConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        print("Client connected") 
        asyncio.create_task(self.send_frames()) 

    async def disconnect(self, close_code):
        print("Client disconnected")

    async def send_frames(self):
        while True:
            frame = latest_processed_frame[0]
            if frame is None:
                await asyncio.sleep(0.1) 
                continue

            _, buffer = cv2.imencode('.jpg', frame)
            jpg_as_text = base64.b64encode(buffer).decode('utf-8')

            try:
                await self.send(jpg_as_text)  
            except Exception as e:
                break  
            await asyncio.sleep(0.05) 
