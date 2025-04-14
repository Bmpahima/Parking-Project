from django.urls import re_path, path
from .consumers import VideoConsumer

# websocket_urlpatterns = [
#     re_path(r'ws/video/$', VideoConsumer.as_asgi()),
# ]

websocket_urlpatterns = [
    path('ws/video/', VideoConsumer.as_asgi()),
]
