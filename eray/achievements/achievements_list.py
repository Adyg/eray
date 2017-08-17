import sys
import inspect

from django.db.models.signals import post_save

from eray.models.achievements import Achievement
from eray.models.content import BaseVote


class BaseAchievement():
    """Base class that all new achievements should inherit from

    It handles populating the database with the Achievements data
    """

    def install_achievements(self):
        """Returns an int (number of achieves installed)

        Parses the current module for any achievement classes and installs them
        """
        for name, obj in inspect.getmembers(sys.modules[__name__]):
            if inspect.isclass(obj):

                # create the Achievement db record
                achievement = Achievement.objects.create(
                    title=obj.title,
                    description=obj.description,
                    slug=obj.slug,
                )

                # callback method after achievement db record is created
                install_method = getattr(obj, 'install', None)
                if callable(install_method):
                    obj.install_self(achievement)


class BasePointAchievement():
    """Base class for achievements based on number of points
    """
    def check_achievement(cls):
        pass

    post_save.connect(check_achievement, BaseVote, weak=False)


class AchievementPrivate(BasePointAchievement):
    title = 'Private'
    description = 'Earn 10 points'
    slug = 'private'

    @classmethod
    def install(cls, achievement):
        pass

    @classmethod
    def award(cls):
        pass


class AchievementCorporal(BasePointAchievement):
    title = 'Corporal'
    description = 'Earn 50 points'
    slug = 'corporal'

    @classmethod
    def install(cls, achievement):
        pass

    @classmethod
    def award(cls):
        pass


class AchievementSergeant(BasePointAchievement):
    title = 'Sergeant'
    description = 'Earn 100 points'
    slug = 'sergeant'

    @classmethod
    def install(cls, achievement):
        pass

    @classmethod
    def award(cls):
        pass        