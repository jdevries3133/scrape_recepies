from ba_crawl import BonApetitCrawler

ba_context = {
    'site name': 'Bon Apetit',
    'cache key': 'BA Cache',
    'url cache key': 'all_urls',
    'read cache': False,
    'debug mode': True,
    'read debug cache': True,
}

crawler = BonApetitCrawler(ba_context)
urls = crawler.get_urls()
url_dict = crawler.make_url_dict()
crawler.cache_recipe_page_responses()