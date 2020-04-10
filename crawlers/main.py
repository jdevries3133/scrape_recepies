from abc import ABC
from copy import copy
from concurrent.futures import ThreadPoolExecutor, as_completed
from io import BytesIO
import logging
import os
import shelve
import time
import re
import sys

import certifi
import pycurl
from bs4 import BeautifulSoup, SoupStrainer

from parsers import Parsers

logging.basicConfig(
    filename='l_main.log',
    level='DEBUG',
    filemode='w',
    format='%(asctime)s %(levelname)-8s %(message)s'
)


class BonApetitScrape:
    """
    Each instance represents a single recipe scraped from the
    bon apetit website.
    """
    def __init__(self, url):

        self.url = url
        self.data = self.gather_data()


    def gather_data(self):
        """
        Act as assistant to the constructor, performing all of the tasks
        that must be performed every time the class is instantiated:

            * make request and soup
            * determine the generation (age) of the soup
            * route the soup to the appropriate parsing function
            * return data structure (dictionary) that includes all the
                information that we will want from the instance:
                        * recipe url
                        * recipe name
                        * recipe author
                        * recipe ingredients
        """
        soup = self.get_page()
        parsed_soup = self.parse(soup)

        return parsed_soup

    def parse(self, soup):
        """
        Determine the generation of the page's soup, and return a
        response code so that the page's soup can be parsed
        appropriately
        """
        # todo determine parser to use

        parse_helper = Parsers(soup)
        parse_helper.bon_apetit_2020()
        return 'response_code'

    def get_page(self):
        """
        Make the request, return the beautifulsoup object.
        """
        response = BonApetitCrawler.make_pycurl_request(self.url)
        self.response = response
        soup = BeautifulSoup(response, features='lxml')
        return soup


class BonApetitCrawler:
    """
    Crawl bon apetit website. Attributes after instantiation are all
    bon appetit recipe urls.
    """
    def __init__(self, read_cache=False, debug_mode=False):
        self.base_url = 'https://www.bonappetit.com/'
        self.sitemap = self.base_url + 'sitemap'

        # define location of the cache
        self.cache_dir = (
            os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                'cache'
            )
        )
        self.cache_path = os.path.join(
            self.cache_dir,
            'bon_apetit_cache'
        )
        # read the cache, if requested
        if read_cache:
            self.url_dict = self.read_cache_func()
        else:
            self.url_dict = {}
            self.recipe_list = self.get_bon_apetit_urls()
            self.write_cache_func()

        if debug_mode:
            self.html_dir = os.path.join(self.cache_dir, 'html_pages')

    def get_bon_apetit_urls(self):
        """
        Recursively crawl through the bon apetit website, and get all
        urls for recipe pages.
        """
        recipe_pages = self.recursive([self.sitemap], cache=True)
        if recipe_pages == []:
            logging.error('recipe pages is empty.')
        return recipe_pages

    def write_cache_func(self):
        with shelve.open(self.cache_path) as db:
            db['cache'] = self.url_dict

    def read_cache_func(self):
        with shelve.open(self.cache_path) as db:
            self.url_dict = db['cache']

    def cache_recipe_page_responses(self):
        """
        Make a request to all the recipe pages, and save them in the
        database.

        Make a locally stored html page for each response, which we can
        use for development.

        '2014_3_week_4.html'
        """
        pass

    def recursive(self, links_to_do, cache=False):
        """
        tuples_found is a list of tuples that we ultimately want.
        These tuples containe two items: the https response from a url,
        and then, the url itself:
            (https_response, url_requested)

        This list of tuples is only appended to if it is a leaf node of
        the sitemap tree.
        """
        if cache:
            lol_parent_children = self.cache_urls(None, use_cache=True)
            return self.sort_base_urls(lol_parent_children)

        log_msg = (str(links_to_do))
        logging.debug('=' * 80)
        logging.debug(log_msg)

        lol_parent_children = []
        next_level = []
        resp_tuples = self.multithread_requests(links_to_do)
        for index, resp_tuple in enumerate(resp_tuples):
            resp, url = resp_tuple
            logging.debug(f'Processed {index} of {len(resp_tuples)} responses.')

            # make the soup, searches the soup
            strainer = SoupStrainer('a', class_='sitemap__link', href=True)
            soup = BeautifulSoup(resp, features='html.parser', parse_only=strainer)
            hrefs = soup.find_all(
                name='a',
                href=True,
                class_='sitemap__link',
            )

            try:
                hrefs[0].contents[0][0]
            except IndexError:
                continue

            if hrefs[0].contents[0][0] != '/':
                # url is a strng; the parent url.
                # hrefs is a list; the list of children of that parent
                lol_parent_children.append(
                    (
                        url,
                        [
                            'https://www.bonappetit.com/' + href_tag.contents[0]
                            for href_tag
                            in hrefs
                        ]
                    )
                )

            if hrefs[0].contents[0][0] == '/':
                links_found = [
                    'https://www.bonappetit.com'
                    + i.contents[0]
                    for i
                    in hrefs
                ]
                next_level += links_found

            logging.debug('NEXT_LEVEL_CALLED')
            logging.debug(next_level[:200])

        if next_level:
            logging.debug(f'Called self.recursive.')
            return self.recursive(next_level)

        if not next_level:
            logging.debug(
                'entered if not. Parents and Children:'
                f'\n{lol_parent_children}'
            )
            return self.sort_base_urls(lol_parent_children)

    def sort_base_urls(self, lol_parent_children, shitlist_mode=False, use_cache=False):
        """
        What we're getting:

        list of these guys:
            (parent_url, children_urls)

        What we need to do:

            Sort recepie urls only from the parent url

        We really need any string that contains '/recipe/'
        """
        self.cache_urls(lol_parent_children, use_cache)

        ol = []
        shitlist = []
        for parent_url, child_urls in lol_parent_children:
            for url in child_urls:
                if '/recipe/' in url:
                    ol.append((parent_url, url))
                else:
                    shitlist.append((parent_url, url))

        if shitlist_mode:
            return shitlist

        return ol

    def cache_urls(self, lol_parent_children, use_cache: bool):
        if not use_cache:
            with shelve.open(self.cache_path) as db:
                db['all_urls'] = lol_parent_children
        if use_cache:
            with shelve.open(self.cache_path) as db:
                lol_parent_children = db['all_urls']
        return lol_parent_children

    def scrape_recipes_from_page(self, url):
        """
        Possibly get more recipies out of the the recipe slideshow
        pages, and other pages that contain recipe links
        """
        return None

    def parse_parent(self, parent_url):
        # get year, month, and date from sitemap url
        pattern = (r'(\d\d\d\d)&month=(\d+)&week=(\d)')
        url_param_regex = re.compile(pattern)
        mo = re.search(url_param_regex, parent_url[40:])
        year, month, week = mo[1], mo[2], mo[3]
        date_string = f'{year}_{month}_week_{week}'

        return date_string

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


if __name__ == '__main__':

    crawler = BonApetitCrawler(read_cache=False, debug_mode=True)
    breakpoint()
    logging.debug(crawler.url_dict)
