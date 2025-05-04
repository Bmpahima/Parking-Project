from django.urls import re_path, path
from .consumers import VideoConsumer, TimerStopConsumer

# websocket_urlpatterns = [
#     re_path(r'ws/video/$', VideoConsumer.as_asgi()),
# ]

websocket_urlpatterns = [
    path('ws/video/', VideoConsumer.as_asgi()),
    re_path(r'ws/stop-timer/(?P<user_id>\d+)/$', TimerStopConsumer.as_asgi())
]
