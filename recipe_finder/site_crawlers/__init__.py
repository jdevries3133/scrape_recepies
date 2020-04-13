"""

This module crawls through websites that have recipes, and caches recipe pages
for later analysis by the html parsers.

Think of init files as exports. The only thing that needs to be sent out of a 
module are the working classes that will be used outside.
"""

from .ba_crawl import BonApetitCrawler

class DebugContext:
    ba_context = {
        'site name': 'Bon Apetit',
        'cache key': 'BA Cache',
        'url cache key': 'all_urls',
        'read cache': False,
        'debug mode': True,
        'read debug cache': True,
    }
