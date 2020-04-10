from abc_crawlers import Crawler

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
        # self.base_url = 'https://www.bonappetit.com/'
        # self.sitemap = self.base_url + 'sitemap'

        # define location of the cache


        # read the cache, if requested

    def get_urls(self):
        """
        Recursively crawl through the bon apetit website, and get all
        urls for recipe pages.
        """

        if self.context['read debug cache']:
            recipe_pages = self.cache_urls(None, use_cache=True)

        recipe_pages = self.recursive([self.sitemap], cache=True)
        if recipe_pages == []:
            logging.error('recipe pages is empty.')
        return recipe_pages

    # def write_cache_func(self):
    #     with shelve.open(self.cache_path) as db:
    #         db['cache'] = self.url_dict

    # def read_cache_func(self):
    #     with shelve.open(self.cache_path) as db:
    #         self.url_dict = db['cache']

    def recursive(self, links_to_do, cache=False):
        """
        tuples_found is a list of tuples that we ultimately want.
        These tuples containe two items: the https response from a url,
        and then, the url itself:
            (https_response, url_requested)

        This list of tuples is only appended to if it is a leaf node of
        the sitemap tree.
        """
        if cache:
            lol_parent_children = self.cache_urls(None, use_cache=True)
            return self.sort_base_urls(lol_parent_children)

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

    def sort_base_urls(self, lol_parent_children, shitlist_mode=False, use_cache=False):
        """
        What we're getting:

        list of these guys:
            (parent_url, children_urls)

        What we need to do:

            Sort recepie urls only from the parent url

        We really need any string that contains '/recipe/'
        """
        self.cache_urls(lol_parent_children, use_cache)

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

    # def cache_urls(self, lol_parent_children, use_cache: bool):
    #     if not use_cache:
    #         with shelve.open(self.cache_path) as db:
    #             db['all_urls'] = lol_parent_children
    #     if use_cache:
    #         with shelve.open(self.cache_path) as db:
    #             lol_parent_children = db['all_urls']
    #     return lol_parent_children

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

    # def multithread_requests(self, urls):
    #     response_and_url = []
    #     with ThreadPoolExecutor(max_workers=200) as executor:
    #         threads = [
    #             executor.submit(
    #                 BonApetitCrawler.make_pycurl_request, url
    #             )
    #             for url
    #             in urls
    #         ]

    #         for r in as_completed(threads):
    #             try:
    #                 response_and_url.append(r.result())

    #             except Exception as e:
    #                 logging.warning(e)

    #     return response_and_url

    # @staticmethod
    # def make_pycurl_request(url):
    #     try:
    #         buffer = BytesIO()
    #         crl = pycurl.Curl()
    #         crl.setopt(crl.URL, url)
    #         crl.setopt(crl.WRITEDATA, buffer)
    #         crl.setopt(crl.CAINFO, certifi.where())
    #         crl.perform()

    #         crl.close()

    #         logging.debug(f'response recieved from {url}')

    #     except Exception as e:
    #         raise Exception(f'{url} failed because of {e}.')

    #     return buffer.getvalue().decode(), url
