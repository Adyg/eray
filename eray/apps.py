from django.apps import AppConfig
from django.db.models.signals import post_migrate

class ErayConfig(AppConfig):
    name = 'eray'
    verbose_name = 'Eray'

    def ready(self):
        from eray.achievements.achievements_list import BaseAchievement
        import eray.signals.handlers

        super(ErayConfig, self).ready()

        post_migrate.connect(BaseAchievement.install_achievements, dispatch_uid='eray.achievements.install_achievements')
