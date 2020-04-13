from abc import ABC, abstractmethod
import time
from io import BytesIO
import logging
import os
from pathlib import Path
import shelve
from concurrent.futures import ThreadPoolExecutor, as_completed

import certifi
import pycurl

logging.basicConfig(
    filename='abc_crawlers.log',
    level='DEBUG',
    filemode='w',
    format='%(asctime)s %(levelname)-8s %(message)s'
)

class Crawler(ABC):
    def __init__(self, sitemap_url, context):
        """
        Things to put in context:
            Site name (string)
            Cache key

        Important to note: the root_dir variable will break anytime that this
        file is moved relative to the base directory.
        """
        self.sitemap = sitemap_url
        self.context = context

        # there should be a separate cache created for every new child
        root_dir = Path.resolve(Path(__file__)).parent.parent.parent
        self.cache_dir = os.path.join(root_dir, 'web_cache')

        # all instances will use the same database
        self.cache_path = os.path.join(
            self.cache_dir,
            'crawler_cache'
        )

        if self.context['refresh cache']:
            self.url_dict = self.read_cache_func()
        else:
            self.url_dict = {}

        if self.context['debug mode']:
            self.html_dir = os.path.join(self.cache_dir, 'html_pages')

    def write_cache_func(self):
        with shelve.open(self.cache_path, protocol=5) as db:
            db[self.context['cache key']] = self.url_dict

    def read_cache_func(self):
        with shelve.open(self.cache_path, protocol=5) as db:
            cached_url_dict = db[self.context['cache key']]
        return cached_url_dict

    def cache_recipe_page_responses(self):
        """
        Make a request to all the recipe pages, and save them in the
        database.

        Make a locally stored html page for each response, which we can
        use for development.

        '2014_3_week_4.html'

        dict = {
            'url groups': {
                'recipe pages': {
                    'parent url': [child urls],
                    'parent url2': [child urls2],
                }
                'other urls': {
                    'parent url': [other urls],
                    (etc)
                }
            }
        }
        """
        logging.debug('Pulling recipe pages.')
        # dict data => [(url, (context))] --- that'll be var "input_list"
        tuples_for_func = []
        # context = {'supercat': 'super', 'subcat': 'sub'}
        for sg_name, sg_content in self.url_dict['url groups'].items():
            # sg_content will be a dict {'parent': [children]}
            for parent, children in sg_content.items():
                context = {'supercat': sg_name, 'subcat': parent}
                for child in children:
                    tuples_for_func.append(
                        (child, context)
                    )
        logging.debug('Making requests to recipe pages')

        for i in range(0, len(tuples_for_func), 500):
            # run operation on a subset at a time, to avoid memory binding.
            subset = tuples_for_func[i:(i + 500)]
            logging.debug(f'Saving the following pages:\n{subset}')

            # results are going to be (response, url, context)
            results = self.multithread_requests(subset)
            logging.debug(f'Got results: {len(results)}')
            mthr_saves = []
            for result in results:
                # (html, url, context)]
                folder = os.path.join(self.html_dir, result[2]['supercat'])
                if not os.path.exists(folder):
                    os.mkdir(folder)

                # make filename
                fn1 = self.parse_parent(result[2]['subcat'])
                fn2 = self.file_name_from_url(result[1])
                filename = f'{fn1} {fn2}.html'
                path = os.path.join(folder, filename)

                mthr_saves.append((path, result[0]))


            with ThreadPoolExecutor(max_workers=200) as executor:
                threads = executor.map(self.multithreaded_html_save, mthr_saves)

    def cache_state(self):
        """
        walk through cache
        return super-categories
        return length of each
        return average creation date
        """

        supercats = [item for item in os.listdir(self.html_dir) if item [0] != '.']


        return_dict = {'html_dir': self.html_dir, 'supercats': {}}
        creation_dates = []
        for folder in supercats:
            for file in os.listdir(os.path.join(self.html_dir, folder)):
                unix_creation = os.path.getmtime(
                    os.path.join(self.html_dir, folder, file))

                creation_dates.append(unix_creation)

            return_dict['supercats'][folder] = {
                'num_of_files': len(os.listdir(os.path.join(self.html_dir, folder))),
            }

        avg_timestamp = sum(creation_dates) // len(creation_dates)
        cache_age = time.time() - avg_timestamp
        return_dict.setdefault('cache age', cache_age)

        return return_dict


    def multithreaded_html_save(self, tupl):
        path, html = tupl
        with open(path, 'w') as file:
            file.write(html)
        logging.debug(f'Saved {path} to the hard drive.')


    def cache_urls(self):
        # reference 'refresh cache'' attribute
        write_cache = not self.context['refresh cache']

        # read cache
        if not write_cache:
            with shelve.open(self.cache_path, protocol=5) as db:
                self.all_urls = db[self.context['url cache key']]

        # write cache
        if write_cache:

            # check for self.all_urls attribute
            if not hasattr(self, 'all_urls'):
                raise Exception(
                    'Cannot cache urls, because self.get_urls() has '
                    'not yet been called, and self.all_urls is not defined.'
                )

            # write
            with shelve.open(self.cache_path, protocol=5) as db:
                db[self.context['url cache key']] = self.all_urls

        logging.debug(f'lpc: {self.all_urls}')

        return self.all_urls

    def multithread_requests(self, urls):

        if isinstance(urls[0], tuple):
            mode = 'tuples'

        if isinstance(urls[0], str):
            mode = 'regular'

        response_and_url = []
        with ThreadPoolExecutor(max_workers=200) as executor:
            if mode == 'regular':
                threads = [
                    executor.submit(
                        self.make_pycurl_request, url
                    )
                    for url
                    in urls
                ]

            if mode == 'tuples':
                threads = [
                    executor.submit(
                        self.make_pycurl_request, url, context
                    )
                    for url, context
                    in urls
                ]


            for r in as_completed(threads):
                try:
                    response_and_url.append(r.result())

                except Exception as e:
                    logging.warning(e)

        return response_and_url

    def make_pycurl_request(self, url, context=None):
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

        if context:
            return buffer.getvalue().decode(), url, context

        return buffer.getvalue().decode(), url

    @abstractmethod
    def parse_parent(self):
        """
        Parse the parent urls from the standard dict above, so that they
        can be used for folder or file names in the above method.
        """
        pass

    @abstractmethod
    def get_urls(self):
        """
        Recursively crawl through the site map, and get all
        urls for recipe pages.
        """
        pass

    @abstractmethod
    def recursive(self, links_to_do, cache=False):
        """
        Crawl through the sitemap, and get urls
        """
        pass

    @abstractmethod
    def make_url_dict(self):
        """
        Go through the recursively discovered list of urls, and filter them
        down to what we actually want; urls which are pages of recipes.
        """
        pass

    @abstractmethod
    def file_name_from_url(self):
        pass
