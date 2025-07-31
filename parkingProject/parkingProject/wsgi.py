"""
WSGI config for parkingProject project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application
import threading

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'parkingProject.settings')

def run_main():
    from parkingApp.main import generate_frames
    generate_frames()

thread = threading.Thread(target=run_main)
thread.start()

application = get_wsgi_application()


