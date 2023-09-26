import random

from pulp import LpMaximize, LpProblem, LpVariable, lpSum, value


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
        self.solver += lpSum((10 + random.random()) * self.recipe_vars[r.id] for r in self.recipes)

    def select_recipes(self, num_recipes):
        self.solver += lpSum(self.recipes[i] for i in range(len(self.recipes))) <= self.numrecipes, "MaxRecipes"
        self.logger.info(f'Selecting {self.numrecipes} recipes with {self.numcriteria} selection criteria.')
        self.solver.solve()
        selected = [self.recipes[i] for i in range(len(self.recipes)) if self.recipes[i].varValue == 1]
        return selected

    def add_food_constraint(self, found_recipes, numrecipes, operator, exclude=False):
        found_recipes = list(set(self.recipes) & set(found_recipes))
        if exclude:
            found_recipes = list(set(self.recipes) - set(found_recipes))
        if operator == ">=":
            self.solver += lpSum(self.recipe_vars[i] for i in [r.id for r in found_recipes]) >= numrecipes
        elif operator == "<=":
            self.solver += lpSum(self.recipe_vars[i] for i in [r.id for r in found_recipes]) <= numrecipes
        elif operator == "==":
            self.solver += lpSum(self.recipe_vars[i] for i in [r.id for r in found_recipes]) == numrecipes
        else:
            raise ValueError(f'Invalid constraint operator: {operator}')
        self.logger.debug(f'Added constraint {operator} {numrecipes}.  Found {len(found_recipes)} recipes that contain the selected food(s).')
        self.numcriteria += 1

    def add_keyword_constraint(self, found_recipes, numrecipes, operator, exclude=False):
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
        self.logger.debug(f'Added constraint {operator} {numrecipes}.  Found {len(found_recipes)} recipes that contain the selected keyword(s).')
        self.numcriteria += 1

    def add_rating_constraints(self, found_recipes, numrecipes, operator, exclude=False):
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
        self.logger.debug(f'Added constraint {operator} {numrecipes}.  Found {len(found_recipes)} recipes that contain the selected rating.')
        self.numcriteria += 1

    def solve(self):
        self.solver.solve()
        return [r for r in self.recipes if value(self.recipe_vars[r.id]) == 1]
