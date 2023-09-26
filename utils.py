import logging
import shelve
import sys
from datetime import datetime, timedelta
from functools import wraps
from uuid import NAMESPACE_OID, uuid3

try:
	caches = shelve.open('caches.db', writeback=True)
	for key in caches:
		if caches[key]['expired'] < datetime.now():
			caches.pop(key)
except FileNotFoundError:
	caches = {}


class InfoFilter(logging.Filter):
	def filter(self, rec):
		return rec.levelno in (logging.DEBUG, logging.INFO)


def relative_date(string):
    return string


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


def str2bool(v):
	if type(v) == bool or v is None:
		return v
	elif type(v) == int or type(v) == float:
		return v == 1
	else:
		return v.lower() in ("yes", "true", "1")


def cached(ttl=240):
	def decorator(func):
		@wraps(func)
		def wrapper(self, *args, **kwargs):
			if not ttl or ttl <= 0:
				return func(self, *args, **kwargs)
			expire_after = timedelta(minutes=ttl)
			# uuid's are consistent across runs, hash() is not
			key = str(uuid3(NAMESPACE_OID, ''.join([str(x) for x in args]) + str(kwargs)))
			if key not in caches or caches[key]['expired'] < datetime.now():
				caches[key] = {'data': func(self, *args, **kwargs), 'expired': datetime.now() + expire_after}
				caches.sync()

			return caches[key]['data']

		return wrapper
	return decorator
