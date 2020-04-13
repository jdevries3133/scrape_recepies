"""

This module crawls through websites that have recipes, and caches recipe pages
for later analysis by the html parsers.

Think of init files as exports. The only thing that needs to be sent out of a 
module are the working classes that will be used outside.
"""

from .ba_crawl import BonApetitCrawler

def check_cache(website):
    """
    Quickly check the cache state of any website using pre-configured context
    which will avoid making copious web requests. Outside use-cases can
    determine what criteria they want to use to refresh the cache (age, count,
    etc.)
    """
    if website == 'Bon Apetit':
        ba_context = {
            'site name': 'Bon Apetit',
            'cache key': 'BA Cache',
            'url cache key': 'all_urls',
            'refresh cache': False,
            'debug mode': True,
            'refresh cache': False
        }

        check_inst = BonApetitCrawler(ba_context)
        return check_inst.cache_state()

def cached_sites():
    """
    Returns a list of sites that are in the cache; serving as a key to 
    check_cache().
    """

    return ['Bon Apetit']
