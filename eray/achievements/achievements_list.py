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

        objs = get_module_classes(__name__, 'title')
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


class BasePointsAchievement():
    """Base class for handling achievements awarded based on number of points
    """

    only_award_once = True # flag controlling if users can only gain the achievement once
    slug = None

    @classmethod
    def grant_achievement(cls, sender, instance, created, **kwargs):
        """Adds the Achievement to the User's profile achievements list
        """
        achievement = Achievement.objects.get(slug=cls.slug)
        vote_parent = instance.parent.get_parent_obj()
        profile = vote_parent.user.profile

        # user meets the criteria for awarding the achievement
        profile_points = profile.get_points()
        if profile_points and profile_points > cls.points_limit:
            # achievement can be awarded multiple times or it was not yet awarded
            if cls.only_award_once or not profile.achievements.filter(pk=achievement.pk).exists():
                profile.achievements.add(achievement)


class AchievementPrivate(BasePointsAchievement):
    title = 'Private'
    description = 'Earn 1 point'
    slug = 'private'
    points_limit = 1

    @classmethod
    def listener(cls):
        post_save.connect(AchievementPrivate.grant_achievement, sender=BaseVote, dispatch_uid='eray.achievements.AchievementPrivate')


class AchievementCorporal(BasePointsAchievement):
    title = 'Corporal'
    description = 'Earn 50 points'
    slug = 'corporal'
    points_limit = 50

    @classmethod
    def listener(cls):
        post_save.connect(AchievementCorporal.grant_achievement, sender=BaseVote, dispatch_uid='eray.achievements.AchievementCorporal')


class AchievementSergeant(BasePointsAchievement):
    title = 'Sergeant'
    description = 'Earn 100 points'
    slug = 'sergeant'
    points_limit = 100

    @classmethod
    def listener(cls):
        post_save.connect(AchievementSergeant.grant_achievement, sender=BaseVote, dispatch_uid='eray.achievements.AchievementSergeant')    