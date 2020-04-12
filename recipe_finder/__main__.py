from site_crawlers import BonApetitCrawler, DebugContext
from html_parsers import BonApetitParser

# ba_crawler dev block
ba_crawler = BonApetitCrawler(DebugContext.ba_context)
ba_cache_state = ba_crawler.cache_state()
