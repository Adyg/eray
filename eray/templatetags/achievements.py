from django import template

register = template.Library()


def achievements(context, profile):
    """Output a list of achievements for the Profile
    """
    achievements = profile.achievements.all()

    response = {
        'achievements': achievements,
      }

    return response


register.inclusion_tag('eray/tag_templates/_achievements.html', takes_context=True)(achievements)
