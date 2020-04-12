from abc import ABC, abstractmethod

class Recipes:
    def __init__(self, title, ingredients, extra_info=None):
        """
        Each recipe object represents one single recipe, from any given site.
        If this were developed into a django web app, this class would probably
        be altered into a model, which would store its instances in a database,
        and be drawn on by the front end.

        Important attributes for each recipe are:
            name
            author
            url
            ***ingredient list***
            prep time
        """
        # these are the only two mandatory attributes
        self.title = title
        self.ingredients = ingredients

        # extra_info may include author, prep time, maybe others?
        if extra_info:
            for key, value in extra_info.items():
                setattr(self, key, value)
