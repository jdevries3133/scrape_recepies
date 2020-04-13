"""

Overall, this module aggregates recipes from all over the place. It will
ultimately return a recipe object instance for each recipe, consisting of the
recipe's name, ingredients, author, prep time, etc.

Think of __init__ as the exports of a module. The only thing that needs to be
in here are the classes that some module froma above might actually want to 
use. The added benefit of __init__ is that you can sort of hide your abstract
classes, or other supporting files that you don't want outsiders to fuck with.

"""

from .site_crawlers import BonApetitCrawler, DebugContext
from .html_parsers import BonApetitParser
# As __main__.py develops, make sure that this file maintains the same import statements
