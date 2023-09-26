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


class Food(SetEnabledObjects):
    def __init__(self, food_json):
        self.id = food_json['id']
        self.name = food_json['name']
        self.shopping = food_json['shopping']
        self.recipe = food_json['recipe']
        self.onhand = food_json['food_onhand']
        self.ignore_shopping = food_json['ignore_shopping']
        self.substitute_onhand = food_json['substitute_onhand']


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
