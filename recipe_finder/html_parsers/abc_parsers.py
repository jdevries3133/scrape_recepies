from abc import ABC, abstractmethod


class Parser(ABC):
    def __init__(self, cache_info):
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