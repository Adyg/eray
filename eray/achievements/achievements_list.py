import sys
import inspect

from django.db.models.signals import post_save

from eray.models.achievements import Achievement
from eray.models.content import BaseVote
from eray.utils import get_module_classes


class BaseAchievement():
    """Base class that all new achievements should inherit from

    It handles populating the database with the Achievements data
    """
    @classmethod
    def install_achievements(cls, sender, **kwargs):
        """Returns an int (number of achieves installed)

        Parses the current module for any achievement classes and installs them
        """
        # only perform the install if called from the Eray config
        if sender.name != 'eray':
            return None

        objs = get_module_classes(__name__)
        for obj in objs:
            if obj != cls:
                achievement = Achievement.objects.filter(slug=obj.slug).count()
                if not achievement:
                    # create the Achievement db record
                    achievement = Achievement.objects.create(
                        title=obj.title,
                        description=obj.description,
                        slug=obj.slug,
                    )


    @classmethod
    def register_achievement_listeners(cls):
        """Parses the current module for any achievement classes and registers their listeners
        """
        objs = get_module_classes(__name__)
        for obj in objs:
            listener_method = getattr(obj, 'listener', None)
            if callable(listener_method):
                obj.listener()


class AchievementPrivate():
    title = 'Private'
    description = 'Earn 10 points'
    slug = 'private'

    @classmethod
    def award(cls, sender, instance, created, **kwargs):
        pass

    @classmethod
    def listener(cls):
        post_save.connect(AchievementPrivate.award, sender=BaseVote, dispatch_uid='eray.achievements.AchievementPrivate')


class AchievementCorporal():
    title = 'Corporal'
    description = 'Earn 50 points'
    slug = 'corporal'

    @classmethod
    def award(cls, sender, instance, created, **kwargs):
        pass

    @classmethod
    def listener(cls):
        post_save.connect(AchievementCorporal.award, sender=BaseVote, dispatch_uid='eray.achievements.AchievementCorporal')


class AchievementSergeant():
    title = 'Sergeant'
    description = 'Earn 100 points'
    slug = 'sergeant'

    @classmethod
    def award(cls, sender, instance, created, **kwargs):
        pass

    @classmethod
    def listener(cls):
        post_save.connect(AchievementCorporal.award, sender=BaseVote, dispatch_uid='eray.achievements.AchievementSergeant')    