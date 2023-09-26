import json

import configargparse
import yaml

from models import Food, Keyword, Recipe
from solver import RecipePicker
from tandoor_api import TandoorAPI
from utils import format_date, setup_logging, str2bool


class Menu:
	options = None
	recipe_picker = None
	keyword_constraints = None
	food_constraints = None
	book_constraints = None
	rating_constraints = None
	cookedon_constraints = None
	createdon_constraints = None

	def __init__(self, options):
		self.options = options
		self.include_children = self.options.include_children
		self.logger = setup_logging(log=self.options.log)
		self.tandoor = TandoorAPI(self.options.url, self.options.token, self.logger, cache=int(self.options.cache))
		self.choices = int(self.options.choices)
		self.recipes = []

		self.__format_constraints__()

	def __format_constraints__(self):
		constraints = ['book', 'food', 'keyword', 'rating', 'cookedon', 'createdon']
		for c in constraints:
			setattr(self, f'{c}_constraints', [json.loads(x.replace("'", '"')) for x in getattr(self.options, c, [])])
			for x in getattr(self, f'{c}_constraints', []):
				x['count'] = int(x['count'])
				if y := x.get('cooked', None):
					x['cooked'], x['cooked_after'] = format_date(y)
				if y := x.get('created', None):
					x['created'], x['created_after'] = format_date(y)

	def prepare_recipes(self):
		for r in self.tandoor.get_recipes(params=self.options.recipes, filters=self.options.filters):
			self.recipes.append(Recipe(r))
		self.recipes = list(set(menu.recipes))

	def prepare_books(self):
		pass

	def prepare_foods(self):
		for constraint in self.food_constraints:
			if not isinstance(c := constraint['condition'], list):
				constraint['condition'] = [c]
			if not isinstance(c := constraint.get('except', []), list):
				constraint['except'] = [c]

			food_list = []
			for fd in constraint['condition']:
				food_list.append(Food(self.tandoor.get_food(fd)))
			constraint['condition'] = food_list

			food_list = []
			for fd in constraint.get('except', []):
				food_list.append(Food(self.tandoor.get_food(fd)))
			constraint['except'] = food_list

			# recipe api doesn't include ingredients, so get a list of ingredients with the food
			params = {
				'foods_or': [f.id for f in constraint['condition']],
				'foods_or_not': [f.id for f in constraint['except']]
			}
			found_recipes = []
			for r in self.tandoor.get_recipes(params=params):
				found_recipes.append(Recipe(r))
			if cooked := constraint.get('cooked', None):
				found_recipes = Recipe.recipesWithDate(found_recipes, 'cookedon', cooked, constraint.get('cooked_after', False))
			if created := constraint.get('created', None):
				found_recipes = Recipe.recipesWithDate(found_recipes, 'createdon', created, constraint.get('created_after', False))
			constraint['condition'] = found_recipes

	def prepare_keywords(self):
		# TODO add 'except' condition to list of keywords
		for constraint in self.keyword_constraints:
			if not isinstance(c := constraint['condition'], list):
				constraint['condition'] = [c]
			if not isinstance(c := constraint.get('except', []), list):
				constraint['except'] = [c]
			if self.include_children:
				kw_tree = []
				for kw in constraint['condition']:
					kw_tree += self.tandoor.get_keyword_tree(kw)
			constraint['condition'] = list(set([Keyword(k) for k in kw_tree]))

	def prepare_data(self):
		self.prepare_recipes()
		self.prepare_keywords()
		self.prepare_foods()
		# self.prepare_books()

	def select_recipes(self):
		self.recipe_picker = RecipePicker(self.recipes, self.choices, logger=self.logger)
		# add keyword constraints
		for c in self.keyword_constraints:
			exclude = str2bool(c.get('exclude', False))
			found_recipes = Recipe.recipesWithKeyword(self.recipes, c['condition'])
			if cooked := c.get('cooked', None):
				found_recipes = Recipe.recipesWithDate(found_recipes, 'cookedon', cooked, c.get('cooked_after', False))
			if created := c.get('created', None):
				found_recipes = Recipe.recipesWithDate(found_recipes, 'createdon', created, c.get('created_after', False))
			self.recipe_picker.add_keyword_constraint(found_recipes, c['count'], c['operator'], exclude=exclude)

		# add food constraints
		for c in self.food_constraints:
			exclude = str2bool(c.get('exclude', False))
			self.recipe_picker.add_food_constraint(c['condition'], c['count'], c['operator'], exclude=exclude)

		# add rating contraints
		for c in self.rating_constraints:
			exclude = str2bool(c.get('exclude', False))
			found_recipes = self.recipes
			if cooked := c.get('cooked', None):
				found_recipes = Recipe.recipesWithDate(found_recipes, 'cookedon', cooked, after=c.get('cooked_after', False))
			if created := c.get('created', None):
				found_recipes = Recipe.recipesWithDate(found_recipes, 'createdon', created, after=c.get('created_after', False))
			self.recipe_picker.add_rating_constraints(Recipe.recipesWithRating(found_recipes, c.get('condition')), c['count'], c['operator'], exclude=exclude)
		return self.recipe_picker.solve()


def parse_args():
	parser = configargparse.ArgParser(
		config_file_parser_class=configargparse.ConfigparserConfigFileParser,
		default_config_files=['./config.ini'],
		description='Create a custom menu from recipes in Tandoor with defined criteria.'
	)
	parser.add_argument('--log', default='info', help='Sets the logging level')
	parser.add_argument('--cache', default='240', help='Minutes to cache Tandoor API results; 0 to disable.')
	parser.add_argument('--url', type=str, required=True, help='The full url of the Tandoor server, including protocol, name, port and path')
	parser.add_argument('--token', type=str, required=True, help='Tandoor API token.')
	parser.add_argument('--recipes', type=yaml.safe_load, help='recipes to choose from; search parameters, see /docs/api/ for full list of parameters')
	parser.add_argument('--filters', nargs='*', default=[], help='Array of CustomFilter IDs')
	parser.add_argument('--choices', default=5, help='Number of recipes to choose')
	parser.add_argument('--book', nargs='*', default=[], help="Conditions are all list of dicts of the format {'condition':xx, 'count':yy, 'operator': [>= or <= or ==]}")
	parser.add_argument('--food', nargs='*', default=[], help='Condition = ID or list of IDs')
	parser.add_argument('--keyword', nargs='*', default=[], help="e.g. [{'condition':[73, 273],'count':'1', 'operator':'>='},{'condition':47,'count':'2','operator':'=='}]")
	parser.add_argument('--rating', nargs='*', default=[], help='condition = number between 0 and 5')
	parser.add_argument('--cookedon', nargs='*', default=[], help="condition = date in YYYY-MM-DD format (use 'XXdays' for relative date XX days ago)")
	parser.add_argument('--createdon', nargs='*', default=[], help="condition = date in YYYY-MM-DD format (use 'XXdays' for relative date XX days ago)")
	parser.add_argument('--include_children', action='store_true', default=True, help='For keywords and foods, child objects also satisfy the condition.')

	return parser.parse_args()


if __name__ == "__main__":
	args = parse_args()
	menu = Menu(args)
	menu.prepare_data()
	recipes = menu.select_recipes()

	menu.logger.info(f'Selected {len(recipes)} recipes for the menu.')
	if menu.logger.level >= 10:
		for r in recipes:
			date_cooked = (x := getattr(r, 'cookedon', None)) and x.strftime("%Y-%m-%d") or "Never"
			menu.logger.debug(f'Selected recipe {r} for the menu with rating {r.rating}. Created on: {r.createdon.strftime("%Y-%m-%d")} and last cooked {date_cooked}')
			kw_list = []
			for kw in r.keywords:
				kw_list.append(kw)
			menu.logger.debug(f'Selected recipe {r} contains keywords {kw_list}.')
			fd_list = []
	pass
