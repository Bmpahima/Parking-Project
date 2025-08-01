"""
ASGI config for parkingProject project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""
import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import parkingApp.routing  

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'parkingProject.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            parkingApp.routing.websocket_urlpatterns  
        )
    ),
})


import threading
from parkingApp.main import start_parking_loop  

def run_main():
    start_parking_loop() 

threading.Thread(target=run_main, daemon=True).start()
