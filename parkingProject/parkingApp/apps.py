from django.apps import AppConfig
import threading

class ParkingAppConfig(AppConfig):
    name = 'parkingApp'

    def ready(self):
        from .main import run
        threading.Thread(target=run, daemon=True).start()
