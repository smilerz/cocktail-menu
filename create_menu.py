

import json

import configargparse
import yaml

from models import Keyword, Recipe
from tandoor_api import TandoorAPI
from utils import setup_logging


class Menu:
	def __init__(self, options):
		self.options = options
		self.include_children = self.options.include_children
		self.logger = setup_logging(log=self.options.log)
		self.tandoor = TandoorAPI(self.options.url, self.options.token, self.logger)
		self.choices = self.options.choices
		self.recipes = []
		self.solver = None

		self.keyword_constraints = [json.loads(kw.replace("'", '"')) for kw in self.options.keywords]

	def prepare_recipes(self):
		for r in self.tandoor.get_recipes(params=self.options.recipes, filters=self.options.filters):
			self.recipes.append(Recipe(r))
		self.recipes = list(set(menu.recipes))

	def prepare_books(self):
		pass

	def prepare_foods(self):
		pass

	def prepare_keywords(self):
		for constraint in self.keyword_constraints:
			if not isinstance(c := constraint['condition'], list):
				constraint['condition'] = [c]
			if self.include_children:
				kw_tree = []
				for kw in constraint['condition']:
					kw_tree += self.tandoor.get_keyword_tree(kw)
				constraint['condition'] = list(set([Keyword(k) for k in kw_tree]))
		pass


def parse_args():
	parser = configargparse.ArgParser(
		config_file_parser_class=configargparse.ConfigparserConfigFileParser,
		default_config_files=['./config.ini'],
		description='Create a custom menu from recipes in Tandoor with defined criteria.'
	)
	parser.add_argument('--log', default='info', help='Sets the logging level')
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
	menu.prepare_recipes()
	menu.prepare_keywords()

	pass
