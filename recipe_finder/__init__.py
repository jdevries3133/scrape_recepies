"""

Overall, this module aggregates recipes from all over the place. It will
ultimately return a recipe object instance for each recipe, consisting of the
recipe's name, ingredients, author, prep time, etc.

"""

from .site_crawlers import BonApetitCrawler
from .html_parsers import BonApetitParser

