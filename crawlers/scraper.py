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
    filename='l_scraper.log',
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

class Crawler(ABC):
    """
    Take in a sitemap, crawl through that sitemap.
    """
    def __init__(self, sitemap_url, site_definition, read_cache=False):
        self.sitemap_url = sitemap_url

        # information to get_leaves_from_node
        self.definition = site_definition

    def write_cache(self):
            with shelve.open(self.cache_path) as db:
                db['cache'] = self.recipe_list

    def read_cache(self):
        with shelve.open(self.cache_path) as db:
            self.recipe_list = db['cache']

    def cache_recipe_page_responses(self):
        """
        Make a request to all the recipe pages, and save them in the
        database.

        Make a locally stored html page for each response, which we can
        use for development.
        """
        pass

    def tree_traverse(self, node, data=None):  # node = base url of the sitemap (to start)
        """
        1. what are the critera for the sitemap links on each sitemap
        page (hopefully universal)

        2. what is the exit case, where we assume all the links we have
        are page links, not sitemap links
        """
        if is_leaf_node(node):
            data = self.get_node_data(node)
            return [data]

        children = get_children_from_node(node)
        tup_new_nodes = multithread_requests(children)
        html_from_response, parent_url = tup_new_nodes

        children = self.parse_html(html_from_response, node)

        return children

    @abstractmethod
    def parse_html(self, child, parent):
        """
        control what the final data structure will be, either a big ass
        list, or a dictionary which perservers the original tree
        structure.
        """
        pass

    @abstractmethod
    def is_leaf_node(self):
        """
        The leaf node is the very bottom of a tree.
        """
        pass

    @abstractmethod
    def get_children_from_node(self):
        """
        Get information that the recursive function will use to traverse
        the tree.
        """
        pass

    @abstractmethod
    def scrape_from_page(self):
        pass

    def multithread_requests(self, urls):
        """
        Call the recursive function again i

        for each child, spawn a new thread that is executing the
        recuriive function.
        """
        response_and_url = []
        with ThreadPoolExecutor(max_workers=200) as executor:
            threads = [
                executor.submit(
                    self.make_pycurl_request, url
                )
                for url
                in urls
            ]

            for r in as_completed(threads):
                try:
                    response_and_url.append(r.result())

                except Exception as e:
                    logging.warning(
                        f'{r} generated an exception: {e}.'
                    )
                    logging.warning(dir(r))

        return response_and_url

    @staticmethod
    def make_pycurl_request(url):
        buffer = BytesIO()
        crl = pycurl.Curl()
        crl.setopt(crl.URL, url)
        crl.setopt(crl.WRITEDATA, buffer)
        crl.setopt(crl.CAINFO, certifi.where())
        crl.perform()

        crl.close()

        logging.debug(f'response recieved from {url}')

        return buffer.getvalue().decode(), url


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
            self.recipe_list = self.read_cache_func()

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
        recipe_pages = self.recursive([self.sitemap], [])
        return recipe_pages

    def recursive(self, links_to_do, links_found):
        log_msg = (
            '\n\n\n'
            + str(links_to_do)
            + '\n\n\n'
            + str(links_found)
            + '\n\n\n'
            + str(self.url_dict)
            + '\n\n\n'
        )
        logging.debug('=' * 80)
        logging.debug(log_msg)

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

            if hrefs[0].contents[0][0] == '/':
                links_found = [
                    'https://www.bonappetit.com'
                    + i.contents[0]
                    for i
                    in hrefs
                ]
                next_level += links_found

        if next_level:
            logging.debug(f'Called self.recursive.')
            return self.recursive(next_level, [])

        if not next_level:
            return self.sort_base_urls(
                [
                    'https://www.bonappetit.com/'
                    + i.contents[0]
                    for i
                    in hrefs
                ],
                url,
            )

    def sort_base_urls(self, urls, parent_url):

        recipe_urls = [i for i in urls if i[27:36] == 'recipe/']
        recipe_page_urls = [i for i in urls if i[27:36] == 'recipes']
        for rp_url in recipe_page_urls:
            recipe_urls += self.scrape_recipes_from_page(rp_url)

        for url in recipe_urls:
            date_string = parse_parent(parent_url)
            name = url[37:].replace('-', ' ').title()
            self.url_dict[date_string] = {
                'name': name,
                'url': url,
                'neighbors': recipe_urls,
                'parent_url': parent_url
            }
        return

    def scrape_recipes_from_page(self, url):
        resp = BonApetitCrawler.make_pycurl_request(url)
        strainer = SoupStrainer('a', href=True)
        soup = BeautifulSoup(
            resp,
            features='lxml',
            parse_only=strainer,
        )
        hrefs = soup.find_all('a', href=True)
        return ['https://www.bonappetit.com/' + i.contents[0] for i in hrefs]

    def parse_parent(self, parent_url):
        # get year, month, and date from sitemap url
        pattern = (r'(\d\d\d\d)&month=(\d+)&week=(\d)')
        url_param_regex = re.compile(pattern)
        mo = re.search(url_param_regex, parent_url[40:])
        year, month, week = mo[1], mo[2], mo[3]
        date_string = f'{year}_{month}_week_{week}'

        return date_string





if __name__ == '__main__':

    crawler = BonApetitCrawler(debug_mode=True)
