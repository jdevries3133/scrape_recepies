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
        urls.

        *** this now returns ALL urls, unsorted.***
        """

        if self.context['read debug cache']:
            return self.cache_urls()

        all_urls = self.recursive([self.sitemap])
        if all_urls == []:
            logging.error('recipe pages is empty.')

        self.all_urls = all_urls
        return all_urls

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
            return lol_parent_children

    def make_url_dict(self):
        """
        Sort the urls into a dict that can interact with the abstract base class
        again.

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

        note: this function must be called from outside, and we are not calling
        it, so the fact that it is unfinished does not affect our ability to get
        urls.
        """
        # write to the cache, only if we are not already reading from it.
        if self.context['debug mode']:
            self.cache_urls()

        if not hasattr(self, 'all_urls'):
            raise Exception(
                'Cannot sort urls, because self.get_urls has not '
                'been called, and self.all_urls attribute is not yet defined.'
            )

        'need to rewrite to output new data structure.'
        output_dict = {
            'url groups': {'recipe pages': {}, 'other urls': {}}

        }
        for parent_url, child_urls in self.all_urls:
            output_dict['url groups']['recipe pages'].update(
                {parent_url:
                    [url for url in child_urls if '/recipe/' in url]}
            )
            output_dict['url groups']['other urls'].update(
                {parent_url:
                    [url for url in child_urls if '/recipe/' not in url]}
            )

        self.url_dict = output_dict
        return output_dict

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