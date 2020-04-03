from copy import copy
import re

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


def get_bon_apetit_urls(starter_url):

    def recursive(blacklist, to_do, recepie_list=None):

        if not recepie_list:
            recepie_list = []

        to_do_next = []
        for url in to_do:

            # make request and makes the soup, searches the soup
            resp = requests.get(url)
            soup = BeautifulSoup(resp.text)
            hrefs = soup.find_all(
                name='a',
                href=True,
                class_='sitemap__link',
            )

            # creates to_do_next
            for i in hrefs:
                print(i.contents)
                concatenated_url = 'https://www.bonappetit.com' + i.contents[0]
                to_do_next.append(copy(concatenated_url))

            # grows the master list by append to_do_next
            recipe_regex = re.compile(r'https://www.bonappetit.com/recipe/(.*)')
            slideshow_regex = re.compile(r'https://www.bonappetit.com/recipes/slideshow/(.*)')

            for item in to_do_next:

                if item in blacklist:
                    continue

                item = 'https://www.bonappetit.com/recipes/slideshow/anchovy-sardine-recipes'

                # process recepie
                mo_recepie = re.search(recipe_regex, item)
                if mo_recepie:
                    recepie_extension = mo_recepie[1]
                    recepie_list.append(recepie_extension)
                    breakpoint()
                    blacklist.append(item)
                    continue

                # process slideshow
                mo_slideshow = re.search(slideshow_regex, item)
                breakpoint()
                if mo_slideshow:
                    response = requests.get(item)
                    soup = BeautifulSoup(response.text)
                    hrefs = soup.find_all(
                        'a',
                        href=True,
                    )

                    # append hrefs that match the recepie regex
                    for i in hrefs:
                        if not re.search(recipe_regex, i.content):
                            recepie_list.append(i)

                blacklist.append(item)


            # exit statement, leave recursion
            if not to_do_next:
                print('empty list')
                breakpoint()

        breakpoint()

        return recursive(blacklist, to_do_next, recepie_list)

    recipe_pages = recursive([starter_url], [starter_url])



    return hrefs, get_bon_apetit_urls(hrefs)


if __name__ == '__main__':


    # going away soon
    import os
    base_dir = os.path.dirname(os.path.abspath(__file__))

    urls = [
        'https://www.bonappetit.com/recipe/vegetarian-ramen',
        'https://www.bonappetit.com/recipe/grilled-sardines-with-aioli',  # slideshow conversion done manually
        'https://www.bonappetit.com/recipe/roasty-toasty-pecan-caramel-shortbread-cookies',
    ]

    # call new url iterator function
    urls = get_bon_apetit_urls('https://www.bonappetit.com/sitemap')



    import sys
    sys.exit()


    for url in urls:
        ba_scr = BonApetitScrape(url)
        file_path = os.path.join(
            base_dir,
            'sample_pages',
            '2020',
            f'{url[34:]}.html',
        )
        break
        # with open(file_path, 'w') as html:
        #     html.write(ba_scr.response.text)


