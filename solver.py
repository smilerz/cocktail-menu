import random

from pulp import LpMaximize, LpProblem, LpVariable, lpSum, value

from models import Recipe


class RecipePicker:
    solver = None
    recipes = None
    numcriteria = 0
    logger = None

    def __init__(self, recipes, numrecipes, logger=None):
        self.logger = logger
        self.recipes = recipes
        self.numrecipes = numrecipes

        self.solver = LpProblem("RecipePicker", LpMaximize)
        self.recipe_vars = LpVariable.dicts("Recipe", [r.id for r in self.recipes], cat='Binary')
        self.solver += lpSum(self.recipe_vars.values()) == self.numrecipes

        # introduce randomness to recipe selection
        self.solver += lpSum(random.random() * self.recipe_vars[r.id] for r in self.recipes)

    def select_recipes(self, num_recipes):
        self.solver += lpSum(self.recipes[i] for i in range(len(self.recipes))) <= self.numrecipes, "MaxRecipes"
        self.logger.info(f'Selecting {self.numrecipes} recipes with {self.numcriteria} selection criteria.')
        self.solver.solve()
        selected = [self.recipes[i] for i in range(len(self.recipes)) if self.recipes[i].varValue == 1]
        return selected

    def add_food_constraint(self, recipes, numrecipes, operator):
        if operator == ">=":
            self.solver += lpSum(self.recipe_vars[i] for i in recipes) >= numrecipes
        elif operator == "<=":
            self.solver += lpSum(self.recipe_vars[i] for i in recipes) <= numrecipes
        elif operator == "==":
            self.solver += lpSum(self.recipe_vars[i] for i in recipes) == numrecipes
        else:
            raise ValueError(f'Invalid constraint operator: {operator}')
        self.logger.debug(f'Added constraint {operator} {numrecipes} found in {len(recipes)} that contain selected food(s).')
        self.numcriteria += 1

    def add_keyword_constraint(self, keywords, numrecipes, operator, exclude=False):
        found_recipes = Recipe.recipesWithKeyword(self.recipes, keywords)
        if exclude:
            found_recipes = list(set(self.recipes) - set(found_recipes))

        if operator == ">=":
            self.solver += lpSum(self.recipe_vars[i] for i in [r.id for r in found_recipes]) >= numrecipes
        elif operator == "<=":
            self.solver += lpSum(self.recipe_vars[i] for i in [r.id for r in found_recipes]) <= numrecipes
        elif operator == "==":
            self.solver += lpSum(self.recipe_vars[i] for i in [r.id for r in found_recipes]) == numrecipes
        elif operator == "!=":
            self.solver += lpSum(self.recipe_vars[i] for i in [r.id for r in found_recipes]) != numrecipes
        else:
            raise ValueError(f'Invalid constraint operator: {operator}')
        self.logger.debug(f'Added constraint {operator} {numrecipes} found in {len(found_recipes)} recipes that contain the selected keyword(s): {keywords}.')
        self.numcriteria += 1

    def solve(self):
        self.solver.solve()
        return [r for r in self.recipes if value(self.recipe_vars[r.id]) == 1]



# class MenuPlanner:


#   # Other constraint methods

#   def get_recent_recipes(self, days):
#     # implementation

#   def get_five_star_not_recent(self, days):
#     # implementation

#   def get_unused_recipes(self):
#     # implementation
