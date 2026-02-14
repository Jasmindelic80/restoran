from django.apps import AppConfig


class NarudzbaConfig(AppConfig):
    name = 'narudzba'

    def ready(self):
        import narudzba.signals
