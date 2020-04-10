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




# resps = self.multithread_requests([url])
#         resp, url = resps[0]
#         strainer = SoupStrainer('a', href=True)
#         soup = BeautifulSoup(
#             resp,
#             features='lxml',
#             parse_only=strainer,
#         )
#         hrefs = soup.find_all('a', href=True)

#         rl = []
#         for hr in hrefs:
#             try:
#                 if hr['href'][4] == 's':
#                     if hr['href'][26:33] == 'recipe/':
#                         rl.append(hr.contents[0])
#                 if hr['href'][4] == ':':
#                     if hr['href'][27:34] == 'recipe/':
#                         rl.append(hr.contents[0])
#             except IndexError:
#                 logging.debug(f'href {hr} failed.')









        # for parent_url, urls in lol_parent_children:
        #     logging.debug(f'start case parent_url {parent_url}')
        #     logging.debug(f'startcase urls {urls}')

        #     recipe_urls = [i for i in urls if i[27:34] == 'recipe/']
        #     recipe_page_urls = [i for i in urls if i[27:34] == 'recipes']

        #     logging.debug(f'Recipe urls to start: \n{recipe_urls}')
        #     logging.debug(f'Rec Page URLs to look at: \n{recipe_page_urls}')

        #     for rp_url in recipe_page_urls:
        #         recipe_urls += self.scrape_recipes_from_page(rp_url)
        #         logging.debug(
        #             f'Got some recipe urls from {rp_url}: {recipe_urls}'
        #         )

        #     for index, url in enumerate(recipe_urls):
        #         logging.debug(f'Recipe Found: {url}')
        #         date_string = self.parse_parent(parent_url)
        #         key = date_string + ' ' + str(index)
        #         name = url[34:].replace('-', ' ').title()
        #         logging.debug('indicator')
        #         self.url_dict[key] = {
        #             'name': name,
        #             'url': url,
        #             'neighbors': recipe_urls,
        #             'parent_url': parent_url
        #         }

        # logging.debug(self.url_dict)