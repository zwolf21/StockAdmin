import os, json, datetime, sys

from dateutil.parser import parser
from listorm import Listorm, read_excel

try:
	from StockAdmin.services.FKHIS.order_selector import get_nutfluid_records, get_label_records
except:
	MODULE_BASE = os.path.dirname(os.path.dirname(__file__))
	MODULE_PATH = os.path.join(MODULE_BASE, 'StockAdmin/services/FKHIS')
	sys.path.append(MODULE_PATH)
	from order_selector import get_label_records, get_nutfluid_records
	



APP_BASE_DIR = os.path.dirname(__file__)
COLLECT_LOG_FILE = os.path.join(APP_BASE_DIR, 'logs/collect.log')
MAX_COLLECT_LENGTH = 20
WARDS = ['51', '52', '61', '71', '72', '81', '92', 'IC']

TYPE_MAPPING = {'ST': '정기', 'AD':'추가', 'EM': '응급', 'OUT': '퇴원'}
KIND_MAPPING = {'LABEL': '라벨', 'NUT': '영양수액'}
# print(sys.path)
# print(MODULE_PATH)

# COLLECT = {
# 	'title': '영양수액 정기/추가/응급 1 차 (123건)',
# 	'date': '2017-04-11',
# 	'kind': '영양수액',
# 	'types': {'정기', '추가', '응급'},
# 	'wards': ['51', '52', '71', 'IC'],
# 	'ord_start_date': '2017-04-12',
# 	'ord_end_date': '2017-04-12',
# 	'start_dt': '2017-04-11 00:00:00',
# 	'end_dt': '2017-04-11 14:01:12',
# 	'seq': 1,
# 	'context': get_nutfluid_records
# }



class Collect(object):
	base_dir = os.path.dirname(__file__)
	collect_file = 'caches/collect.json'

	def __init__(self):
		self.objects = self._open_record_file()

	def _set_collect_path(self):
		collect_path = os.path.join(self.base_dir, self.collect_file)
		collect_dir = os.path.dirname(collect_path)
		if not os.path.exists(collect_dir):
			os.mkdir(collect_dir)
		return collect_path		


	def _open_record_file(self):
		collect_path = self._set_collect_path()
		if os.path.exists(collect_path):		
			with open(collect_path) as fp:
				records = json.loads(fp.read())
				return Listorm(records)
		return Listorm()


	def save(self, collect, remove=-1):
		collect_path = self._set_collect_path()
		if remove > -1:
			self.objects.pop(remove)
		else:
			self.objects.append(collect)
		cache = json.dumps(self.objects[-MAX_COLLECT_LENGTH:], check_circular=False)
		with open(collect_path, 'w') as fp:
			fp.write(cache)
		return collect

	def delete(self, slug):
		for i, collect in enumerate(self.objects):
			if collect.slug == slug:
				return self.save(collect, i)

	def _calc_seq(self, types, kind, date):
		date = date or datetime.date.today().strftime("%Y-%m-%d")
		objects = self.objects.filter(where = lambda row: row.date==date and row.types==types and row.kind==kind)
		top = objects.top('date', 'types', 'kind', 'seq', n=1)
		if top:
			return top[0]['seq'] + 1
		return 1

	def _calc_dt_range(self, types, kind, seq):
		if seq < 2:
			next_start_dt = datetime.date.today().strftime("%Y-%m-%d %H:%M:%S")
			next_end_dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
		else:
			pre_seq = seq - 1
			last = self.objects.filter(where = lambda row: row.types==types and row.kind==kind and row.seq==pre_seq)
			next_start_dt = last[0].end_dt
			next_end_dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
		return next_start_dt, next_end_dt


	def _get_auto_ord_date_range(self, auto_on_staturday=False):
		tomorrow = datetime.date.today() + datetime.timedelta(1)
		start, end = tomorrow, tomorrow
		if auto_on_staturday:
			today = datetime.date.today()
			if today.weekday() == 5:
				end = end + datetime.timedelta(1)
		return start, end

	def _generate_title(self, types, kind, seq, date, counts=None):
		type_order = {'정기':1 , '추가':2, '응급':3, '퇴원':4}		
		# types = map(TYPE_MAPPING.get, types)
		type = '/'.join(sorted(types, key=type_order.get))
		return "{} {} {} {}차({}건)".format(date, kind, type, seq, counts)

	# def _generate_slug(self, *args, **kwargs):
	# 	return self._generate_title(*args, **kwargs)

	def _generate_slug(self, types, kind, seq, date):
		type_order = {'ST':1 , 'AD':2, 'EM':3, 'OUT':4}
		type = '-'.join(sorted(types, key=type_order.get))
		return "{}-{}-{}-{}".format(date, kind, type, seq)

	def get_object(self, slug):
		for obj in self.objects:
			if obj.slug == slug:
				return obj
		return {}

	def get_list(self):
		return self.objects[::-1] 

	def create_collect(self, kind, types, wards, date=None, start_date=None, end_date=None, start_dt=None, end_dt=None, auto_on_staturday=True, translate=True):

		wards = wards.split(', ') if isinstance(wards, str) else wards

		ori_types, ori_kind = types, kind
		types = list(map(TYPE_MAPPING.get, types))
		kind = KIND_MAPPING.get(kind)

		if date is None:
			date = datetime.date.today().strftime("%Y-%m-%d")
		else:
			date = date.strftime("%Y-%m-%d") if isinstance(date, (datetime.datetime, datetime.date)) else date
			

		if start_date is None or end_date is None:
			start_date, end_date = self._get_auto_ord_date_range(auto_on_staturday=auto_on_staturday)
		else:
			start_date = start_date.strftime("%Y-%m-%d") if isinstance(start_date, (datetime.datetime, datetime.date)) else start_date
			end_date = end_date.strftime("%Y-%m-%d") if isinstance(end_date, (datetime.datetime, datetime.date)) else end_date		

		seq = self._calc_seq(types, kind, date)

		if not start_dt or not end_dt:
			start_dt, end_dt = self._calc_dt_range(types, kind, seq)
		else:
			start_dt = start_dt.strftime("%Y-%m-%d %H:%M:%S") if isinstance(start_dt, (datetime.datetime, datetime.date)) else start_dt
			end_dt = end_dt.strftime("%Y-%m-%d %H:%M:%S") if isinstance(end_dt, (datetime.datetime, datetime.date)) else end_dt

		slug = self._generate_slug(types, kind, seq, date)

		if not translate:
			types = ori_types
			kind = ori_kind

		collect = {
			'slug': slug, 'kind': kind, 'types': types, 'date': date, 'seq': seq, 'wards': wards,
			'start_date': start_date, 'end_date': end_date, 'start_dt': start_dt, 'end_dt': end_dt
		}
		return collect


	def set_context(self, collect=None, slug=None, test=False):

		collect = collect or self.get_object(slug)

		if not collect:
			return {}

		date, types, kind, wards, start_date, end_date, start_dt, end_dt = collect.get('date'), collect.get('types'), collect.get('kind'), collect.get('wards'), collect.get('start_date'), collect.get('end_date'), collect.get('start_dt'), collect.get('end_dt')
		
		if kind in ["영양수액", "NUT"]:
			context = get_nutfluid_records(types, wards, start_date, end_date, start_dt, end_dt, test)
			collect['grp_by_ward'] = context['grp_by_ward']
		elif kind in ["라벨", "LABEL"]:
			context = get_label_records(["S", "P"], types, wards, start_date, end_date, start_dt, end_dt, test)
			
		# collect['context'] = context
		collect['ord_count'] = context['count']
		collect['grp_by_drug_nm'] = context['grp_by_drug_nm']
		collect['title'] = self._generate_title(types, kind, collect['seq'], date, collect['ord_count'])
		

	def get_form(self,request, *args, **kwargs):
		if request.method == "GET":
			kind = request.GET.get('kind')
			types = request.GET.getlist('types')
			wards = request.GET.getlist('wards')

			if kind and types and wards:
				return self.create_collect(kind, types, wards, *args, **kwargs)

# 	def get_or_create(self, request):
# 		if request.method = "GET":
# 			request.GET.get('slug')


# cm = Collect()
# c = cm.create_collect(kind="라벨", types=['응급','정기', '추가'], wards=['51', '52'], date='2017-04-17', start_date='2017-04-18', end_date='2017-04-18', start_dt='2017-04-17 00:00:00', end_dt='2017-04-17 14:07:12')
# cm.set_context(c, test=True)























