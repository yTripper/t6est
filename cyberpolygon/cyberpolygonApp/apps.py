from django.apps import AppConfig

class CyberpolygonappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'cyberpolygonApp'

    def ready(self):
        pass
