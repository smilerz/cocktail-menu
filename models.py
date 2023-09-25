from datetime import datetime


class SetEnabledObjects:
    def __eq__(self, other):
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)

    def __repr__(self):
        return f'{self.id}: <{self.name}>'

    def __str__(self):
        return self.name


class Ingredient(SetEnabledObjects):
    def __init__(self, name, is_perishable, is_uncommon, is_bitter, is_common, opened_date=None):
        self.id
        self.name = name
        self.is_perishable = is_perishable # list of ingredients
        self.is_uncommon = is_uncommon # list of ingredients
        self.is_bitter = is_bitter # list of ingredients
        self.is_common = is_common # list of ingredients
        self.is_smokey = is_smokey # list of ingredients
        self.is_bitter = is_bitter # list of ingredients
        self.is_herbal = is_herbal # list of ingredients
        self.is_fruit = is_fruit # list of ingredients
        self.is_flavored_syrup = is_flavored_syrup # list of ingredients


class Recipe(SetEnabledObjects):
    def __init__(self, json_recipe, get_food=False):
        self.id = json_recipe['id']
        self.name = json_recipe['name']
        self.description = json_recipe['description']
        self.new = json_recipe['new']
        self.keywords = [kw['id'] for kw in json_recipe['keywords']]
        try:
            self.cookedon = datetime.fromisoformat(json_recipe['last_cooked'])
        except (ValueError, TypeError):
            self.cookedon = None
        self.createdon = datetime.fromisoformat(json_recipe['created_at'])
        self.rating = json_recipe['rating']
        self.ingredients = None  # List of Ingredient objects

    def populate_food(self):
        pass

    @staticmethod
    def recipesWithKeyword(recipes, keywords):
        '''
        filters a list of recipes that contain any of a list of keywords
        recipes: list of Recipes
        keywords: list of Keywords

        Returns:
            filtered list of Recipes
        '''
        return [r for r in recipes if any(k in r.keywords for k in [x.id for x in keywords])]



class Keyword(SetEnabledObjects):
    def __init__(self, json_kw):
        self.id = json_kw['id']
        self.name = json_kw['name']
