from abc import ABC, abstractmethod


class Parser(ABC):
    def __init__(self, cache_info, context):
        """
        Cache info comes in from the site crawler module. It tells this module:

            *   where to find html pages to parse
            *   what are the broad categories that it has pre-sorted html pages
                    into (ideally, recipe pages, and not recipe pages)
            *   when was the cache last downloaded.

        This information comes in via a dictionary; for example:

        {'html_dir': the directory
         'supercats': {'other urls': {'avg_creation_date': datetime object
                                      'num_of_files': 3390},
                       'recipe pages': {'avg_creation_date': datetime object,
                                        'num_of_files': 8550}}}
        """
        self.cache_info = cache_info

    def assess_cache_quality(self):
        """
        Compares date of the cache to the current date. Will automatically
        remove and replace a cache older than a certain time period, unless
        debug mode is set to true.

        It'll ultimately return codes that indicate the quality of the cache.
        0 means good, 1 means the cache should be replaced because it's older
        than a month. If debug mode is on, it'll always return zero.
        """
        if self.context['debug mode']:
            return 0
