import os, sys, datetime
from dateutil.parser import parse

def time_to_normstr(*time_values, to='date'):
	ret = []
	for value in time_values:
		if isinstance(value, (datetime.date, datetime.datetime)):
			time = value
		elif isinstance(value, str):
			try:
				time = parse(value)
			except ValueError:
				time = value
		else:
			time = value		
		ret.append(time)
	if to == 'date':
		ret = tuple(map(lambda time: time.strftime("%Y-%m-%d"), ret))
	else:
		ret = tuple(map(lambda time: time.strftime("%Y-%m-%d %H:%M:%S"), ret))

	if len(ret) == 1:
		return ret[0]
	return ret


