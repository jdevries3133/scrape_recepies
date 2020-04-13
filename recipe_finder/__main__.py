"""

This module does all of the finding of recipes from other sites. It has three
modules that do three important things:

    Site crawlers looks for web pages that contain recipes. It also caches
    the initial html responses of those websites.

    Html_parsers looks through the cache created by site crawlers, and it looks
    for distinct recipe objects. At a minimum, it finds a recipe's name and
    ingredient list. It may also find the recipe's author, prep time,
    difficulty, or other optional attributes.

    Recipe objects recieves the recipe objects and stores them in a relational
    database using django models.

Each website has its own cralwer, parser, and object instantiator, which area
derived from abstract classes, and which posess as much similarity as possible.
At the very least, every crawler, parser, and instantiator, respectively, have
the same attributes and methods.

"""
from site_crawlers import BonApetitCrawler, DebugContext
from html_parsers import BonApetitParser

# ba_crawler dev block
ba_crawler = BonApetitCrawler(DebugContext.ba_context)

ba_cache_state = ba_crawler.cache_state()
