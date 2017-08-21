import sys
import inspect
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

def get_module_classes(module, required_property=False):
    """Return all classes defined in the current module
    If required_propery is passed, only classes that hasattr(cls, required_property) will be returned

    Parameters
    ----------
    module: str
    required_property: str
    """

    classes = []
    for name, obj in inspect.getmembers(sys.modules[module], lambda member: inspect.isclass(member) and member.__module__ == module and (required_property==False or hasattr(member, required_property))):
        classes.append(obj)

    return classes