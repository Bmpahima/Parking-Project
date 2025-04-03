import asyncio
import base64
import cv2
from channels.generic.websocket import AsyncWebsocketConsumer
from .shared_frame import latest_processed_frame  # זה המשתנה שמכיל את הפריימים

class VideoConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        print("[WS] Client connected ✅")  # אם התחברו בהצלחה
        asyncio.create_task(self.send_frames())  # הפעלת שליחה של פריימים ברקע

    async def disconnect(self, close_code):
        print("[WS] Client disconnected")

    async def send_frames(self):
        while True:
            frame = latest_processed_frame[0]
            if frame is None:
                print("[WS] No frame available")
                await asyncio.sleep(0.1)  # אם אין פריים, נחכה טיפה וננסה שוב
                continue

            print("[WS] Sending frame...")
            _, buffer = cv2.imencode('.jpg', frame)
            jpg_as_text = base64.b64encode(buffer).decode('utf-8')

            try:
                await self.send(jpg_as_text)  # שלח את התמונה ב־base64
            except Exception as e:
                print(f"[ERROR] Failed to send frame: {e}")
                break  # יציאה מהלולאה אם השידור נכשל או החיבור נסגר

            await asyncio.sleep(0.05)  # כ-20 FPS
