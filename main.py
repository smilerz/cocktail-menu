import locale
import logging
import sys
#!/usr/bin/env python3
from typing import Optional

import configargparse


class InfoFilter(logging.Filter):
	def filter(self, rec):
		return rec.levelno in (logging.DEBUG, logging.INFO)


class Menu:
	log_levels = {
		'CRITICAL': logging.CRITICAL,
		'ERROR': logging.ERROR,
		'WARNING': logging.WARNING,
		'INFO': logging.INFO,
		'DEBUG': logging.DEBUG
	}

	def __init__(self, options):
		self.logger = logging.getLogger('PlexSync')
		self.options = options
		self.setup_logging()
		self.source_player: Optional[MediaPlayer] = None
		self.destination_player: Optional[MediaPlayer] = None
		if self.options.reverse:
			self.source_player = PlexPlayer()
			self.destination_player = self.get_player()
		else:
			self.source_player = self.get_player()
			self.destination_player = PlexPlayer()
		self.source_player.dry_run = self.destination_player.dry_run = self.options.dry
		self.conflicts = []
		self.updates = []

	def setup_logging(self):
		self.logger.setLevel(logging.DEBUG)

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
		self.logger.addHandler(fh)

		# Set up the error / warning command line logger
		ch_err = logging.StreamHandler(stream=sys.stderr)
		ch_err.setFormatter(formatter_explicit)
		ch_err.setLevel(logging.WARNING)
		self.logger.addHandler(ch_err)

		# Set up the verbose info / debug command line logger
		ch_std = logging.StreamHandler(stream=sys.stdout)
		ch_std.setFormatter(formatter_brief)
		ch_std.addFilter(InfoFilter())
		level = -1
		if isinstance(self.options.log, str):
			try:
				level = self.log_levels[self.options.log.upper()]
			except KeyError:
				pass
		elif isinstance(self.options.log, int):
			if 0 <= self.options.log <= 50:
				level = self.options.log

		if level < 0:
			print('Valid logging levels specified by either key or value:{}'.format('\n\t'.join(
				'{}: {}'.format(key, value) for key, value in self.log_levels.items()))
			)
			raise RuntimeError('Invalid logging level selected: {}'.format(level))
		else:
			ch_std.setLevel(level)
			self.logger.addHandler(ch_std)


def parse_args():
	parser = configargparse.ArgumentParser(default_config_files=['./config.ini'], description='Synchronizes ID3 music ratings with a Plex media-server')
	# parser.add_argument('--sync', nargs='*', default=['tracks'], help='Selects which items to sync: one or more of [tracks, playlists]')
	parser.add_argument('--log', default='info', help='Sets the logging level')
	parser.add_argument('--url', type=str, required=True, help='The full url of the Tandoor server, including protocol, name, port and path')
	parser.add_argument('--token', type=str, required=True, help='Tandoor API token.')


	return parser.parse_args()


if __name__ == "__main__":
	args = parse_args()
	sync_agent.sync()
