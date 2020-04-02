from bs4 import BeautifulSoup


class Parsers:
    def __init__(self, soup):
        self.soup = soup

    def bon_apetit_2020(self):
        """
        Parse the newest page as of 4/1/2020 and return the final
        init data structure.
        """
        pass

    def bon_apetit_2010(self):
        """
        Parse the oldest page, circa 2010 and return the final init data
        structure.
        """
        pass

    def bon_apetit_slideshow(self):
        """
        Get all href tags in the slideshow page, sort them with regex,
        send those to be parsed in the right place.
        """
        pass


if __name__ == '__main__':
    pass
