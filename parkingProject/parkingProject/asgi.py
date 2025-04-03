"""
ASGI config for parkingProject project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os
import django
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application
import parkingApp.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'parkingProject.settings')
django.setup()

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            parkingApp.routing.websocket_urlpatterns  # וודא ש־URLים של ה־WebSocket מקובלים כאן
        )
    ),
})

