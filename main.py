from copy import copy
import logging
import os
import shelve
import re

from bs4 import BeautifulSoup
import requests

from parsers import Parsers

logging.basicConfig(filename='main.log', level='DEBUG', filemode='w')


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
    """
    Recursively crawl through the bon apetit website, and get all urls for recepie pages.

    """

    def recursive(blacklist, to_do, recepie_list=None):

        logging.debug(('=' * 80))

        to_do_next = []
        for url in to_do:
            log_msg = (
                '\n\n\n'
                + url
                + '\n\n\n'
                + str(len(to_do))
                + '\n\n\n'
                + str(recepie_list)
                + '\n\n\n'
            )
            logging.debug(log_msg)
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
                concatenated_url = 'https://www.bonappetit.com/' + i.contents[0]
                to_do_next.append(copy(concatenated_url))


            # grows the master list by append to_do_next
            recipe_regex = re.compile(r'https://www.bonappetit.com/recipe/(.*)')
            slideshow_regex = re.compile(r'https://www.bonappetit.com/recipes/slideshow/(.*)')

            for item in to_do_next:

                if item in blacklist:
                    continue

                # process recepie
                mo_recepie = re.search(recipe_regex, item)
                logging.debug(item)
                if mo_recepie:
                    recepie_extension = mo_recepie[1]
                    recepie_list.append(recepie_extension)
                    logging.debug(f'recepie:   {recepie_extension}')
                    blacklist.append(item)
                    continue

                # process slideshow
                mo_slideshow = re.search(slideshow_regex, item)
                if mo_slideshow:
                    resp = requests.get(item)
                    soup = BeautifulSoup(resp.text)
                    for a in soup.find_all('a', href=True):
                        mo = re.search(recipe_regex, a['href'])
                        if mo:
                            recepie_list.append(mo[1])
                            logging.debug(('*' * 80))
                        else:
                            logging.debug(
                                f'href in slideshow page {item} is '
                                f'not a recepie: {a}'
                                )

                blacklist.append(item)

                # whenever we get to 10k recepies, that's good enough!
                if len(recepie_list) > 10000:
                    return recepie_list


        return recursive(blacklist, to_do_next, recepie_list)

    recipe_pages = recursive([starter_url], [starter_url], [])

    return recipe_pages

def cache_pages_at_urls(urls):
    """
    Cache the html pages that come from each url.
    """

    base_dir = os.path.dirname(os.path.abspath(__file__))

    for url in urls:
            ba_scr = BonApetitScrape(url)
            file_path = os.path.join(
                base_dir,
                'sample_pages',
                '2020',
                f'{url[34:]}.html',
            )
            break
            with open(file_path, 'w') as html:
                html.write(ba_scr.response.text)

    return 0

def cache_urls(urls):
    """
    Cache the urls themselves, both in a txt file, and in a shelve
    database
    """
    db = shelve.open('url_database')
    db['url_list'] = urls
    db.close()

    with open('url_list.txt', 'w') as file:
        for url in urls:
            file.write(f'{url}\n\n')

    return 0



if __name__ == '__main__':


    # call new url iterator function
    urls = get_bon_apetit_urls('https://www.bonappetit.com/sitemap')

    cache_urls(urls)
    cache_pages_at_urls(urls)

