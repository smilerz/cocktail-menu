import logging
import re
import shelve
import sys
from datetime import datetime, timedelta, timezone
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


def format_date(string):
	date, after = string_to_date(string)
	if date:
		return date, after

	after, offset, interval = split_offset(string)
	# TODO support more time intervals that days
	offset = timedelta(days=offset)
	return datetime.now(timezone.utc) - offset, after


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

def string_to_date(date_str):
	# Define the regex pattern
	pattern = r'^-?\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])$'

	# Use re.match to check if the string matches the pattern
	if re.match(pattern, date_str):
		if date_str[:1] == '-':
			return datetime.strptime(date_str[1:], '%Y-%m-%d').replace(tzinfo=timezone.utc), False
		else:
			return datetime.strptime(date_str[1:], '%Y-%m-%d').replace(tzinfo=timezone.utc), True
	else:
		return False, False


def split_offset(s):
	# Define the regex pattern to match the desired format
	pattern = r'^(-?)(\d+)([dD]?[aA]?[yY]?[sS]?)$'

	# Use re.match to extract the parts of the string
	match = re.match(pattern, s)

	if match:
		# Extract and assign values to variables
		after = not match.group(1) == '-'
		offset = int(match.group(2))
		interval = match.group(3).lower()  # Convert to lowercase for case-insensitivity
		return after, offset, interval

	else:
		# Return None or raise an exception for invalid input
		raise ValueError(f"Invalid time offset format: {s}.  Value must be in form of '-XXdays'")
