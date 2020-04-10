from ba_crawl import BonApetitCrawler

ba_context = {
    'site name': 'Bon Apetit',
    'cache key': 'BA Cache',
    'url cache key': 'all urls',
    'read cache': False,
    'debug mode': True,
    'read debug cache': False,
}

crawler = BonApetitCrawler(ba_context)
crawler.get_urls()
# crawler.write_cache_func()
