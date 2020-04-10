from abc import ABC, abstractmethod
from io import BytesIO
import logging
import os
import shelve
from concurrent.futures import ThreadPoolExecutor, as_completed

import pycurl

class Crawler(ABC):
    def __init__(self, sitemap_url, context):
        """
        Things to put in context:
            Site name (string)
            Cache key
        """
        self.sitemap = sitemap_url
        self.context = context

        # there should be a separate cache created for every new child
        self.cache_dir = (
            os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                'cache'
            )
        )

        # all instances will use the same database
        self.cache_path = os.path.join(
            self.cache_dir,
            'crawler_cache'
        )

        if self.context['read cache']:
            self.url_dict = self.read_cache_func()
        else:
            self.url_dict = {}

        if self.context['debug mode']:
            self.html_dir = os.path.join(self.cache_dir, 'html_pages')

    def write_cache_func(self):
        with shelve.open(self.cache_path) as db:
            db[self.context['cache key']] = self.url_dict

    def read_cache_func(self):
        with shelve.open(self.cache_path) as db:
            cached_url_dict = db[self.context['cache key']]
        return cached_url_dict

    def cache_recipe_page_responses(self):
        """
        Make a request to all the recipe pages, and save them in the
        database.

        Make a locally stored html page for each response, which we can
        use for development.

        '2014_3_week_4.html'
        """
        pass

    def cache_urls(self, lol_parent_children, use_cache: bool):
        if not use_cache:
            with shelve.open(self.cache_path) as db:
                db[self.context['url cache key']] = lol_parent_children
        if use_cache:
            with shelve.open(self.cache_path) as db:
                lol_parent_children = db[self.context['url cache key']]
        return lol_parent_children

    def multithread_requests(self, urls):
        response_and_url = []
        with ThreadPoolExecutor(max_workers=200) as executor:
            threads = [
                executor.submit(
                    BonApetitCrawler.make_pycurl_request, url
                )
                for url
                in urls
            ]

            for r in as_completed(threads):
                try:
                    response_and_url.append(r.result())

                except Exception as e:
                    logging.warning(e)

        return response_and_url

    @staticmethod
    def make_pycurl_request(url):
        try:
            buffer = BytesIO()
            crl = pycurl.Curl()
            crl.setopt(crl.URL, url)
            crl.setopt(crl.WRITEDATA, buffer)
            crl.setopt(crl.CAINFO, certifi.where())
            crl.perform()

            crl.close()

            logging.debug(f'response recieved from {url}')

        except Exception as e:
            raise Exception(f'{url} failed because of {e}.')

        return buffer.getvalue().decode(), url

    @abstractmethod
    def get_urls(self):
        """
        Recursively crawl through the site map, and get all
        urls for recipe pages.
        """
        pass

    @abstractmethod
    def cache_recipe_page_responses(self):
        """
        Make a request to all the recipe pages, and save them in the
        database.

        Make a locally stored html page for each response, which we can
        use for development.

        '2014_3_week_4.html'
        """
        pass

    @abstractmethod
    def recursive(self, links_to_do, cache=False):
        """
        Crawl through the sitemap, and get urls
        """
        pass

    @abstractmethod
    def sort_base_urls(self):
        """
        Go through the recursively discovered list of urls, and filter them
        down to what we actually want; urls which are pages of recipes.
        """
        pass
