import json

import configargparse
import yaml

from models import Food, Keyword, Recipe
from solver import RecipePicker
from tandoor_api import TandoorAPI
from utils import setup_logging, str2bool


class Menu:
	recipe_picker = None

	def __init__(self, options):
		self.options = options
		self.include_children = self.options.include_children
		self.logger = setup_logging(log=self.options.log)
		self.tandoor = TandoorAPI(self.options.url, self.options.token, self.logger, cache=int(self.options.cache))
		self.choices = int(self.options.choices)
		self.recipes = []

		self.keyword_constraints = [json.loads(kw.replace("'", '"')) for kw in self.options.keywords]
		for kc in self.keyword_constraints:
			kc['count'] = int(kc['count'])
		self.food_constraints = [json.loads(fd.replace("'", '"')) for fd in self.options.foods]
		for fc in self.food_constraints:
			fc['count'] = int(fc['count'])

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
			if not isinstance(c := constraint.get('except',[]), list):
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
			recipes_with_food = []
			for r in self.tandoor.get_recipes(params=params):
				recipes_with_food.append(Recipe(r))
			constraint['condition'] = recipes_with_food

	def prepare_keywords(self):
		# TODO add 'except' condition to list of keywords
		for constraint in self.keyword_constraints:
			if not isinstance(c := constraint['condition'], list):
				constraint['condition'] = [c]
			if not isinstance(c := constraint.get('except',[]), list):
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
		self.prepare_books()
		createdon = None
		rating = None
		cookedon = None

	def select_recipes(self):
		self.recipe_picker = RecipePicker(self.recipes, self.choices, logger=self.logger)
		# add keyword constraints
		for c in self.keyword_constraints:
			exclude = str2bool(c.get('exclude', False))
			self.recipe_picker.add_keyword_constraint(c['condition'], c['count'], c['operator'], exclude)

		# add food contstraints
		for c in self.food_constraints:
			exclude = str2bool(c.get('exclude', False))
			self.recipe_picker.add_food_constraint(c['condition'], c['count'], c['operator'], exclude)
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
	parser.add_argument('--books', nargs='*', default=[], help="Conditions are all list of dicts of the format {'condition':xx, 'count':yy, 'operator': [>= or <= or ==]}")
	parser.add_argument('--foods', nargs='*', default=[], help='Condition = ID or list of IDs')
	parser.add_argument('--keywords', nargs='*', default=[], help="e.g. [{'condition':[73, 273],'count':'1', 'operator':'>='},{'condition':47,'count':'2','operator':'=='}]")
	parser.add_argument('--ratings', nargs='*', default=[], help='condition = number between 0 and 5')
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
			menu.logger.debug(f'Selected recipe {r} for the menu.')
			kw_list = []
			for kw in r.keywords:
				kw_list.append(kw)
			menu.logger.debug(f'Selected recipe {r} contains keywords {kw_list}.')
			fd_list = []
	pass
