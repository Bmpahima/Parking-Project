import json
from channels.generic.websocket import AsyncWebsocketConsumer

class VideoConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for handling video streaming via Django Channels.

    This consumer listens for connections on a fixed room group called 'video_stream',
    accepts incoming WebSocket frames (as JSON/text), and broadcasts them to all 
    connected clients in the group.
    """
    async def connect(self):
        """
        Called when a WebSocket connection is established.

        Adds the connection to a channel group ('video_stream') and accepts the WebSocket.
        """
        self.room_group_name = "video_stream"
        # Add this connection to the channel group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        # Accept the WebSocket connection
        await self.accept()
        print("[INFO] WebSocket connected.")

    async def disconnect(self, close_code):
        """
        Called when the WebSocket connection is closed.

        Removes the connection from the channel group.
        """
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        print("[INFO] WebSocket disconnected.")

    async def receive(self, event):
        """
        Called when a message is received from the WebSocket client.

        Forwards the received video frame (text data) back to the client.
        
        Parameters:
        - event: A dictionary containing the 'text_data' field with the frame content.
        """
        frame_data = event.get("text_data")
        
        if frame_data:
            # Send the frame back to the client
            await self.send(text_data=frame_data)
