"""

This module is the glue that binds site_crawlers and recipe_objects. Site
crawlers only crawls through the website, and downloads data to the hard disk.
Recipe objects is only a clean object that possesses recipe attributes. For
example, recipe name, recipe ingredients, etc.

This parser module recieves the html pages from the site crawler, and returns
a clean, and uniform data structure which can be passed to recipe_objects.

If this project is developed into a django web app, the database models will
probably be directly hooked to parsers, and updated on a schedule.

Ultimately, from the html mess that site crawlers delivers, this module should
return the following information for each recipe:

    *   Recipe Name
    *   Recipe URL
    *   Recipe Ingredients

Additionally, this module may return some optional information, and downstream
modules should understand that this information may or may not be included for
each recipe:

    *   Recipe Author
    *   Recipe Prep Time
    *   (add add'l optional attributes, if encountered)

"""

from .bon_apetit_parsers import BonApetitParser

class DebugContextParsers:
    ba_context = {
            'debug_mode': True,
        }
