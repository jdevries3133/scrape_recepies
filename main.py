from copy import copy
from bs4 import BeautifulSoup, SoupStrainer

from abc_crawlers import Crawler

logging.basicConfig(
    filename='l_main.log',
    level='DEBUG',
    filemode='w',
    format='%(asctime)s %(levelname)-8s %(message)s'
)


class BonApetitScrape(Crawler):
    """
    Each instance represents a single recipe scraped from the
    bon apetit website.
    """
    def __init__(self, sitemap_url, context):
        super().__init__(sitemap_url, context)

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




if __name__ == '__main__':

    crawler = BonApetitCrawler(read_cache=False, debug_mode=True)
    breakpoint()
    logging.debug(crawler.url_dict)
