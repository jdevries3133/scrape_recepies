from ba_crawl import BonApetitCrawler

ba_context = {
    'site name': 'Bon Apetit',
    'cache key': 'BA Cache',
    'url cache key': 'all_urls',
    'read cache': False,
    'debug mode': True,
    'read debug cache': False,
}

crawler = BonApetitCrawler(ba_context)
urls = crawler.get_urls()
crawler.cache_urls()
print(urls)
import shelve
with shelve.open(crawler.cache_path) as db:
    test = db['all_urls']