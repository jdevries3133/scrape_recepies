def better_recursive():

    """
    What will we always do?
        take a url
        get all the sitemap urls

    request sitemap page
    get the first list
    give each list it's own process (multiprocessing)


    ** func base
    1. start with list of sitemap links (top level)
    2. make a request to it
    3. get all the sitemap links
        repeat

    exit case: there are no sitemap links



    *** func base exit
    1. we start with a list of urls which are not sitemap links
    for link in links:
        if recipe link --> store it
        *** func extension: outside funcif slideshow link --> request it --> get recipe links --> store them
        else pass
    """

first_call_links = # all the sitmap year links, which come from the top level

def recursive(self, links_to_do, links_found):
    log_msg = (
        '\n\n\n'
        + links_to_do
        + '\n\n\n'
        + links_found
        + '\n\n\n'
        + self.url_dict
        + '\n\n\n'
    )
    logging.debug('=' * 80)
    logging.debug(log_msg)

    for url in links_to_do:

        # make request and makes the soup, searches the soup
        resp = BonApetitCrawler.make_pycurl_request(url)
        strainer = SoupStrainer('a', class_='sitemap__link', href=True)
        soup = BeautifulSoup(resp, features='html.parser', parse_only=strainer)
        hrefs = soup.find_all(
            name='a',
            href=True,
            class_='sitemap__link',
        )

        if hrefs[0].contents[0][0] == '/':
            links_found = [
                'https://www.bonappetit.com'
                + i.contents[0]
                for i
                in hrefs
            ]
            return BonApetitCrawler.recursive(links_found, [])
        else:

            return ['https://www.bonappetit.com/' + i.contents[0] for i in hrefs]

def sort_base_urls(self, urls, parent_url):

    recipe_urls = [i for i in urls if i[27:36] == 'recipe/']
    recipe_page_urls = [i for i in urls if i[27:36] == 'recipes']
    recipe_urls += scrape_recipes_from_page(recipe_page_urls)

    for url in recipe_urls:
        date_string = parse_parent(parent_url)
        name = url[37:].replace('-', ' ').title()
        self.url_dict[date_string] = {
            'name': name,
            'url': url,
            'neighbors': recipe_urls,
            'parent_url': parent_url
        }
    return

def scrape_recipes_from_page(self, url):
    resp = BonApetitCrawler.make_pycurl_request(url)
    strainer = SoupStrainer('a', href=True)
    soup = BeautifulSoup(
        resp,
        features='lxml',
        parse_only=strainer,
    )
    hrefs = soup.find_all('a', href=True)
    return ['https://www.bonappetit.com/' + i.contents[0] for i in hrefs]

def parse_parent(self, parent_url)
    # get year, month, and date from sitemap url
    pattern = (r'(\d\d\d\d)&month=(\d+)&week=(\d)')
    url_param_regex = re.compile(pattern)
    mo = re.search(url_param_regex, parent_url[40:])
    year, month, week = mo[1], mo[2], mo[3]
    date_string = f'{year}_{month}_week_{week}'

    return date_string
