from abc_crawlers import Crawler
import logging

from bs4 import BeautifulSoup, SoupStrainer

logging.basicConfig(
    filename='ba_crawl.log',
    level='DEBUG',
    filemode='w',
    format='%(asctime)s %(levelname)-8s %(message)s'
)

class BonApetitCrawler(Crawler):
    """
    Crawl bon apetit website. Attributes after instantiation are all
    bon appetit recipe urls.
    """
    def __init__(self, context):
        super().__init__(
            'https://www.bonappetit.com/sitemap',
            context
        )

    def get_urls(self):
        """
        Recursively crawl through the bon apetit website, and get all
        urls for recipe pages.

        Returns (parent_url, recipe_url)
        """

        if self.context['read debug cache']:  # this defniitely works now
            return self.cache_urls(None, write_cache=False)

        recipe_pages = self.recursive([self.sitemap])
        if recipe_pages == []:
            logging.error('recipe pages is empty.')
        return recipe_pages

    def recursive(self, links_to_do):
        """
        tuples_found is a list of tuples that we ultimately want.
        These tuples containe two items: the https response from a url,
        and then, the url itself:
            (https_response, url_requested)

        This list of tuples is only appended to if it is a leaf node of
        the sitemap tree.
        """

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
            soup = BeautifulSoup(
                resp,
                features='html.parser',
                parse_only=strainer
            )
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

    def sort_base_urls(self, lol_parent_children, shitlist_mode=False):
        """
        What we're getting:

        list of these guys:
            (parent_url, children_urls)

        What we need to do:

            Sort recepie urls only from the parent url

        We really need any string that contains '/recipe/'
        """
        write_cache = not self.context['read debug cache']
        self.cache_urls(lol_parent_children, write_cache=write_cache)

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

    def scrape_recipes_from_page(self, url):
        """
        Possibly get more recipies out of the the recipe slideshow
        pages, and other pages that contain recipe links
        """
        pass

    def parse_parent(self, parent_url):
        # get year, month, and date from sitemap url
        pattern = (r'(\d\d\d\d)&month=(\d+)&week=(\d)')
        url_param_regex = re.compile(pattern)
        mo = re.search(url_param_regex, parent_url[40:])
        year, month, week = mo[1], mo[2], mo[3]
        date_string = f'{year}_{month}_week_{week}'

        return date_string

    def cache_recipe_page_responses(self):
        pass
