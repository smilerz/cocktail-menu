class Ingredient:
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




class Recipe:
    def __init__(self, name, base_spirit, cocktail_style, last_made_date, star_rating, unused_count, ingredients):
        self.name = name
        self.base_spirit = base_spirit
        self.cocktail_style = cocktail_style
        self.last_made_date = last_made_date
        self.star_rating = star_rating
        self.unused_count = unused_count
        self.ingredients = ingredients  # List of Ingredient objects

        self.has_perishable = has_perishable
        self.has_uncommon = has_uncommon
        self.has_bitter = has_bitter
        self.has_common = has_common
        self.has_smokey = has_smokey
        self.has_bitter = has_bitter
        self.has_herbal = has_herbal
        self.has_fruit = has_fruit
        self.has_flavored_syrup = has_flavored_syrup

    def classify_recipe(self):
        pass
