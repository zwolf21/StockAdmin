import os, json, sys, datetime
from pprint import pprint
from operator import itemgetter


from listorm import Listorm

# try:
from StockAdmin.services.FKHIS.order_apis import *

# except:
# 	MODULE_BASE = os.path.dirname(os.path.dirname(__file__))
# 	MODULE_PATH = os.path.join(MODULE_BASE, 'StockAdmin/services/FKHIS')
# 	sys.path.append(MODULE_PATH)
# 	sys.path.append(os.path.dirname(MODULE_PATH))
# 	from order_apis import get_orderset
# 	from utils import time_to_normstr


COLLECT_FILE = os.path.join(os.path.dirname(__file__), 'caches/collect.json')
STATIC_INFO_FILE = os.path.join(os.path.dirname(__file__), 'caches/static.json')
MAX_OBJECT_LIST_LENGTH = 40

class CollectStorage(object):
	
	def __init__(self, filepath, max_object_list_length=MAX_OBJECT_LIST_LENGTH):
		self.path = filepath
		self.max_object_list_length = max_object_list_length
		self._get_or_create_dir(self.path)
		self._load()

	def _get_or_create_dir(self, path):
		try:
			if os.path.isdir(path):
				os.makedirs(path)
			else:
				path = os.path.dirname(path)
				os.makedirs(path)
		except:
			return

	def _load(self):
		if os.path.isfile(self.path):
			with open(self.path) as fp:
				self.object_list = Listorm(json.loads(fp.read()))
		else:
			self.object_list = Listorm()

	def save(self, object=None, commit=True):
		if object:
			self.object_list.append(object)
		if commit:
			with open(self.path, 'w') as fp:
				object_list = self.object_list[-self.max_object_list_length:]
				data = json.dumps(object_list, indent=4)
				fp.write(data)
			return
		return self.object_list

	def delete(self, slug):
		self.object_list = self.object_list.filter(lambda row: row.slug != slug)
		self.save()
	
	def clear(self):
		self.object_list = Listorm()
		self.save()

	def get(self, slug):
		return self.object_list.filterand(slug=slug).first

	def get_object_list(self):
		return Listorm(self.object_list[::-1])

	def get_latest(self, **kwargs):
		latest = self.object_list.filterand(**kwargs).top('seq')
		return latest


class StaticStorage(CollectStorage):
	initial = [
		{'kind': 'LABEL', 'extras':'', 'excludes':''},
		{'kind': 'INJ', 'extras':'', 'excludes':''},
		{'kind': 'NUT', 'extras':'', 'excludes':''},
	]

	def __init__(self, filepath=STATIC_INFO_FILE):
		super(StaticStorage, self).__init__(filepath)

	def _load(self):
		if os.path.isfile(self.path):
			with open(self.path) as fp:
				self.object_list = Listorm(json.loads(fp.read()))
		else:
			with open(self.path, 'w') as fp:
				fp.write(json.dumps(self.initial, indent=4))
			self._load()

	def save(self, kind, excludes=None, extras=None, **kwargs):
		if excludes is not None:
			self.object_list.update(excludes=excludes, where=lambda row:row.kind==kind)
		if extras is not None:
			self.object_list.update(extras=extras, where=lambda row:row.kind==kind)

		with open(self.path, 'w') as fp:
			fp.write(json.dumps(self.object_list, indent=4))

	def get(self, kind):
		obj = self.object_list.filterand(kind=kind).first
		return obj

class Collect(object):

	def __init__(self):
		self.db = CollectStorage(COLLECT_FILE)
		self.static_db = StaticStorage(STATIC_INFO_FILE)
		
	def get_context(self, *args, **kwargs):
		return get_orderset(*args, **kwargs)

	def _get_collect_date(self):
		today = datetime.date.today()
		return today.strftime('%Y-%m-%d')

	def _generate_seq(self, **kwargs):
		latest = self.db.get_latest(**kwargs)
		return latest.seq + 1 if latest else 1

	def _generate_title(self, kind, date, types, seq, wards, count=0, slugify=False):
		if slugify:
			types = '-'.join(types)
			wards = '-'.join(wards)
			return "{}-{}-{}-{}-{}".format(kind, date, types, wards, seq)
		types = map(type_verbose.get, types)
		types = '/'.join(types)
		return "{} {} {} {}차({}개 병동, {}건)".format(kind_verbose.get(kind), date, types, seq, len(wards) ,count)


	def save(self, types, wards, date, start_date, end_date, start_dt, end_dt, kind,  commit=True, test=False, **kwargs):
		types = sorted(types, key=type_order.get)
		vkind = kind_verbose.get(kind)
		vtypes = list(map(type_verbose.get, types))
		date, timestamp, start_date, end_date = time_to_normstr(date, datetime.datetime.now(), start_date, end_date)

		start_dt, end_dt = time_to_normstr(start_dt, end_dt, to='datetime')
		seq = self._generate_seq(kind=kind, date=date, types=types, wards=wards)
		static = self.get_static(kind)
		order_list = get_orderset(types, wards, start_date, end_date, start_dt, end_dt, kind, date=date, extras=static.extras, excludes=static.excludes, test=test)
		title = self._generate_title(kind, date, types, seq, wards, len(order_list))
		slug = self._generate_title(kind, date, types, seq, wards, slugify=True)
		rcpt_dt_min, rcpt_dt_max = order_list.min('rcpt_dt'), order_list.max('rcpt_dt')

		obj = {
			'slug': slug, 'title': title, 'date': date, 'timestamp': timestamp,
			'types': types, 'vtypes': vtypes, 'wards': wards, 'seq':seq,
			'start_date': start_date, 'end_date': end_date,
			'start_dt': start_dt, 'end_dt': end_dt,
			'kind': kind, 'vkind': vkind,
			'order_list': order_list,
			'count': len(order_list),
			'rcpt_dt_max': rcpt_dt_max, 'rcpt_dt_min': rcpt_dt_min
		}

		if commit:
			self.db.save(obj)
		return obj

	def get(self, slug):
		obj = self.db.get(slug)
		order_list = Listorm(obj.get('order_list'))
		obj['orders'] = parse_order_list(order_list)
		return obj

	def get_extra_and_exclude(self):
		return self.db.get_static()

	def delete(self, slug):
		return self.db.delete(slug)

	def clear(self):
		self.db.clear()

	def get_queryset(self):
		queryset =  self.db.get_object_list()
		return queryset

	def _get_next_dt(self, **kwargs):
		latest = self.db.get_latest(**kwargs)
		# print(latest)
		start_dt = latest.end_dt if latest else datetime.date.today()
		end_dt = datetime.datetime.now()
		return time_to_normstr(start_dt, end_dt, to='datetime')

	def _get_next_date(self, types, kind):
		start_date, end_date = datetime.date.today(), datetime.date.today()
		if {'ST'} <= set(types):
			start_date += datetime.timedelta(1)
			end_date += datetime.timedelta(1)
			if datetime.date.today().weekday() == 5 and kind == 'LABEL': # if saturday
				end_date += datetime.timedelta(1)
		return time_to_normstr(start_date, end_date)

	def get_form_initial(self, kind, types=['ST'], wards=['51', '52', '61', '71', '81', '92', 'IC']):
		date = time_to_normstr(datetime.date.today())
		start_dt, end_dt = self._get_next_dt(kind=kind, date=date, types=types, wards=wards)
		start_date, end_date = self._get_next_date(types, kind)
		initial = {
			'start_date': start_date, 'end_date': end_date,
			'start_dt': start_dt, 'end_dt': end_dt, 'types': types,
		}
		return initial

	def save_static(self, kind, **kwargs):
		self.static_db.save(kind, **kwargs)

	def get_static(self, kind, **kwargs):
		return self.static_db.get(kind)



# def set_default_form(request):
	


# c = Collect()
# c.save(
# 	# types=['정기', '추가', '응급', '퇴원'],
# 	types = ['ST', 'AD', 'EM', 'OT'],
# 	wards=['51', '52', '61', '71', '81', '92', 'IC'], 
# 	start_date='2017-09-19', end_date='2017-09-20',
# 	start_dt='2016-09-19 00:00:00', end_dt='2017-09-20 00:00:00', 
# 	kind='NUT',
# 	extras = ['란스톤15', '테리본', '하루날디'],
# 	excludes = ['오마프원', '하모닐란'],
# 	test=True
# )


