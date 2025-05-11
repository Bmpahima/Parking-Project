from django.apps import AppConfig
import threading

class ParkingAppConfig(AppConfig):
    name = 'parkingApp'

    def ready(self):
        import time
        from .main import run

        time.sleep(5)
        threading.Thread(target=run, daemon=True).start()
