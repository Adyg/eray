from urllib.parse import urlparse

from django.shortcuts import reverse
    

def pluralize(count, singular, plural):
    """Determine is the singular or plural form of a word should be used

    Parameters
    ----------
    count: int
    singular: str
    plural: str
    """
    if count == 1:
        return singular

    return plural