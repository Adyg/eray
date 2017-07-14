from django.apps import AppConfig

class ErayConfig(AppConfig):
    name = 'eray'
    verbose_name = 'Eray'

    def ready(self):
        super(ErayConfig, self).ready()
 
        import signals    