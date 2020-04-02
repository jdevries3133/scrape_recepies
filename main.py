from bs4 import BeautifulSoup
import requests

from parsers import Parsers




class BonApetitScrape:
    """
    Each instance represents a single recepie scraped from the
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
                        * recepie url
                        * recepie name
                        * recepie author
                        * recepie ingredients
        """
        soup = self.get_page()
        parsed_soup = self.parse(soup)

        return parsed_soup

    def parse(self, soup):
        """
        Determine the generation of the page's soup, and return a response
        code so that the page's soup can be parsed appropriately
        """
        # todo determine parser to use

        parse_helper = Parsers(soup)
        parse_helper.bon_apetit_2020()  # change to whatever the parser actually should be.
        return 'response_code'

    def get_page(self):
        """
        Make the request, return the beautifulsoup object.
        """
        response = requests.get(self.url)
        self.response = response
        soup = BeautifulSoup(response.text, features='html.parser')
        return soup


if __name__ == '__main__':
    url = 'https://www.bonappetit.com/recipe/roasty-toasty-pecan-caramel-shortbread-cookies'
    ba_scr = BonApetitScrape(url)
