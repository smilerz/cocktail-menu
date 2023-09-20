import logging
import sys

import configargparse
import yaml

#!/usr/bin/env python3
from tandoor_api import TandoorAPI


class InfoFilter(logging.Filter):
	def filter(self, rec):
		return rec.levelno in (logging.DEBUG, logging.INFO)


class Menu:


	def __init__(self, options):

		self.options = options


def setup_logging(log='INFO'):
	log_levels = {
		'CRITICAL': logging.CRITICAL,
		'ERROR': logging.ERROR,
		'WARNING': logging.WARNING,
		'INFO': logging.INFO,
		'DEBUG': logging.DEBUG
	}
	logger = logging.getLogger('CreateMenu')
	logger.setLevel(logging.DEBUG)

	# Set up the two formatters
	formatter_brief = logging.Formatter(fmt='[%(asctime)s] %(levelname)s: %(message)s', datefmt='%H:%M:%S')
	formatter_explicit = logging.Formatter(
		fmt='[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s',
		datefmt='%H:%M:%S'
	)

	# Set up the file logger
	fh = logging.FileHandler(filename='cocktail-menu.log', encoding='utf-8', mode='w')
	fh.setLevel(logging.DEBUG)
	fh.setFormatter(formatter_explicit)
	logger.addHandler(fh)

	# Set up the error / warning command line logger
	ch_err = logging.StreamHandler(stream=sys.stderr)
	ch_err.setFormatter(formatter_explicit)
	ch_err.setLevel(logging.WARNING)
	logger.addHandler(ch_err)

	# Set up the verbose info / debug command line logger
	ch_std = logging.StreamHandler(stream=sys.stdout)
	ch_std.setFormatter(formatter_brief)
	ch_std.addFilter(InfoFilter())
	level = -1
	if isinstance(log, str):
		try:
			level = log_levels[log.upper()]
		except KeyError:
			pass
	elif isinstance(log, int):
		if 0 <= log <= 50:
			level = log

	if level < 0:
		print('Valid logging levels specified by either key or value:{}'.format('\n\t'.join(
			'{}: {}'.format(key, value) for key, value in log_levels.items()))
		)
		raise RuntimeError('Invalid logging level selected: {}'.format(level))
	else:
		ch_std.setLevel(level)
		logger.addHandler(ch_std)
	return logger


def parse_args():

	parser = configargparse.ArgParser(
		config_file_parser_class=configargparse.ConfigparserConfigFileParser,
		default_config_files=['./config.ini'],
		description='Create a custom menu from Tandoor with defined criteria.'
	)
	parser.add_argument('--log', default='info', help='Sets the logging level')
	parser.add_argument('--url', type=str, required=True, help='The full url of the Tandoor server, including protocol, name, port and path')
	parser.add_argument('--token', type=str, required=True, help='Tandoor API token.')
	parser.add_argument('--recipes', type=yaml.safe_load, help='Selects which items to sync: one or more of [tracks, playlists]')
	parser.add_argument('--filters', nargs='*', default=[], help='Selects which items to sync: one or more of [tracks, playlists]')
	parser.add_argument('--choices', default=5, help='Number of recipes to choose')
	parser.add_argument('--books', nargs='*', default=[], help='Selects which items to sync: one or more of [tracks, playlists]')
	parser.add_argument('--foods', nargs='*', default=[], help='Selects which items to sync: one or more of [tracks, playlists]')
	parser.add_argument('--keywords', nargs='*', default=[], help='Selects which items to sync: one or more of [tracks, playlists]')
	parser.add_argument('--ratings', nargs='*', default=[], help='Selects which items to sync: one or more of [tracks, playlists]')
	parser.add_argument('--cookedon', nargs='*', default=[], help='Selects which items to sync: one or more of [tracks, playlists]')
	parser.add_argument('--createdon', nargs='*', default=[], help='Selects which items to sync: one or more of [tracks, playlists]')

	return parser.parse_args()


if __name__ == "__main__":
	args = parse_args()
	logger = setup_logging(log=args.log)
	tandoor = TandoorAPI(args.url, args.token, logger)
	recipes = tandoor.get_recipes(params=args.recipes, filters=args.filters)
	pass
