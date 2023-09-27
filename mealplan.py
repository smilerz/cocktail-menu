class MealPlanManager:
    def __init__(self, api, logger):
        self.api = api
        self.logger = logger

    def create_from_recipes(self, recipes, mp_type, date, note):
        for r in recipes:
            self.create(r, mp_type, date, note)

    def cleanup_uncooked(self, date, type):
        pass

    def create(self, recipe, type, date, note):
        self.api.create_meal_plan(
            title = recipe.name,
            recipe = recipe,
            servings = recipe.servings,
            type = type,
            note = note,
            date = date
        )
