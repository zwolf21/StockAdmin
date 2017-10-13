import os, json, sys, datetime
from pprint import pprint
from itertools import chain
from operator import itemgetter
from functools import reduce, wraps
from collections import defaultdict

from dateutil.parser import parse
from listorm import Listorm

from .storages import *
from StockAdmin.services.FKHIS.order_apis import *
from utils.shortcuts import time_to_normstr


def attatch_since(func):
	@wraps(func)
	def wrapper(self, *args, **kwargs):
		today = datetime.date.today()
		now = datetime.datetime.now()
		def since(date_str):
			timestamp = parse(date_str)
			one_minute_ago = now - datetime.timedelta(minutes=1)
			one_hour_ago = now - datetime.timedelta(hours=1)
			ond_day_ago = now - datetime.timedelta(days=1)

			if timestamp > one_minute_ago:
				return 'second'
			elif timestamp > one_hour_ago:
				return 'minute'
			elif timestamp > ond_day_ago:
				return 'hour'
			else:
				return 'day'

		queryset = func(self, *args, **kwargs)
		queryset = queryset.add_columns(since=lambda row: since(row.timestamp))
		return queryset
	return wrapper



class Collector(object):

	def __init__(self, *args, **kwargs):
		self.db = CollectStorage(COLLECT_FILE)
		self.config = StaticStorage(STATIC_INFO_FILE)

	def _generate_slug(self, date, kinds, types, wards, seq):
		types = '-'.join(types)
		date = time_to_normstr(date)
		kinds = '-'.join(kinds)
		wards = '-'.join(wards)
		return "{}-{}-{}-{}-{}".format(types, date, kinds, wards, seq)

	def _generate_title(self, date, kinds, types, seq, count):
		types = '/'.join(map(lambda t: type_verbose.get(t,t), types))
		kinds = '+'.join(map(lambda k: kind_verbose.get(k,k), kinds))
		date = time_to_normstr(date)
		return "{} [{}]{}{}차({}건)".format(date, kinds, types, seq, count)

	def _generate_seq(self, date, kinds, types, wards):
		date = time_to_normstr(date)
		latest = self.db.object_list.filterand(date=date, kinds=kinds, types=types, wards=wards).max('seq')
		return latest + 1 if latest else 1

	def _generate_initial_object(self, date, kinds, types, wards, start_date, end_date, start_dt, end_dt, len_queryset):
		
		if set(types) <= type_reverbose.keys(): # 쿼리 후의 컨텍스트는 한글로 되어있음, 일단 한글 types 를 vtypes 에 저장하고...
			vtypes = types 
			types = list(map(type_reverbose.get, vtypes)) # 슬러기 파이를 위해 다시 영어로 바꿔 줌(::IIS 에서 한글 주소 치면 하얀 화면만 나옴, IIS url에 한글 허용 X)	
		else:
			vtypes = list(map(type_verbose.get, types))	
		vkinds = list(map(kind_verbose.get, kinds)) 

		seq = self._generate_seq(date, kinds, types, wards)
		title = self._generate_title(date, kinds, types, seq, len_queryset)
		slug = self._generate_slug(date, kinds, types, wards, seq)
		timestamp = time_to_normstr(datetime.datetime.now(), to='datetime')
		context = {
			'date': date, 'kinds':kinds, 'types': types, 'wards': wards, 'start_date': start_date, 'end_date': end_date,
			'seq': seq, 'title': title, 'vtypes': vtypes, 'vkinds': vkinds, 'timestamp': timestamp, 'slug':slug,
			'start_dt': start_dt, 'end_dt': end_dt
		}
		return context
	
	def merge_object(self, *objects, commit=True):

		date = time_to_normstr(datetime.date.today())
		timestamp = time_to_normstr(datetime.datetime.now(), to='datetime')
		concated = defaultdict(list)
		
		for object in objects:
			for key, val in object.items():
				if key == 'queryset':
					concated[key] = Listorm(concated[key]) | Listorm(val)
				elif isinstance(val, list):
					concated[key]+=val
				else:
					concated[key].append(val)

		merged = {}
		queryset = Listorm()
		for key, val in concated.items():
			if key == 'kinds':
				merged[key] = sorted(set(val), key=lambda k: kind_order.get(k,k))
			elif key == 'types':
				merged[key] = sorted(set(val), key=lambda t: type_order.get(t,t))
			elif key == 'wards':
				merged[key] = sorted(set(val))
			elif key in ['start_date', 'start_dt']:
				merged[key] = sorted(val)[0]
			elif key in ['end_date', 'end_dt']:
				merged[key] = sorted(val)[-1]
			elif key == 'queryset':
				queryset = val
				merged['len_queryset'] = len(val)
			elif key == 'date':
				merged[key] = date

		instance = self._generate_initial_object(**merged)
		instance['slug'] = instance['slug'] + "-MERGED"
		instance['title'] = instance['title'] + "(병합본)"
		instance['queryset'] = queryset
		self.db.save(instance, commit)
		return instance

	def save(self, date, start_date, end_date, wards, *contexts, commit=True, test=False):
		oa = OrderApi(static=self.config.get(), date=date, start_date=start_date, end_date=end_date, wards=wards, test=test)
		for context, queryset in zip(contexts, oa.get_order_lists(*contexts)):
			print('saving context:', context)
			instance = self._generate_initial_object(len_queryset=len(queryset), **context)
			instance['queryset'] = queryset
			self.db.save(instance, commit)
		return instance # 일부러 마지막 인스턴스를 리턴

	def last(self, **kwargs):
		if kwargs:
			return self.db.get_latest(**kwargs)
		return self.db.object_list.last

	def get_parsed(self, slug, **kwargs):
		obj = self.get_object(slug)
		context = parse_order_list(obj.queryset)
		return context

	@attatch_since
	def get_queryset(self):
		return Listorm(self.db.object_list[::-1])


	def get_object(self, slug, **kwargs):
		return self.db.get(slug)

	def clear(self):
		self.db.clear()

	def delete(self, slug):
		self.db.delete(slug)

	def save_config(self, kinds, **kwargs):
		self.config.save(kinds, **kwargs)

	def get_config(self, kinds, **kwargs):
		return self.config.get(kinds)

	def time_options(self, kind, types, **kwargs):
		today = datetime.date.today()
		yesterday = today - datetime.timedelta(1)
		tomorrow = today + datetime.timedelta(1)
		now = datetime.datetime.now()
		end_dt = now

		if set(types) == {'ST', 'AD', 'EM'}:
			today_latest = self.db.get_latest(date=today, kind=kind, types=types)
			if today_latest:
				start_date, end_date = today, today
				start_dt = today_latest.end_dt
			else:
				start_date = yesterday
				end_date = today
				st_latest = self.db.get_latest(date=yesterday, kind=kind, types=['ST'])
				ad_latest = self.db.get_latest(date=yesterday, kind=kind, types=['AD', 'EM'])
				if st_latest and ad_latest:
					latest = st_latest if st_latest.end_dt < ad_latest.end_dt else ad_latest
				else:
					latest = st_latest or ad_latest or None
				
				start_dt = latest.end_dt if latest else yesterday
				if not latest:
					start_date = yesterday
		
		elif set(types) == {'ST'}:
			start_date = tomorrow
			end_date = tomorrow
			latest = self.db.get_latest(date=today, kind=kind, types=types)
			if latest:
				start_dt = latest.end_dt
			else:
				start_dt = today
		elif set(types) == {'AD', 'EM'}:
			start_date = today
			end_date = today

			st_ad_latest = self.db.get_latest(date=today, kind=kind, types=['ST', 'AD', 'EM'])
			if st_ad_latest:
				start_dt = st_ad_latest.end_dt
			else:
				latest = self.db.get_latest(date=today, kind=kind, types=types)
				if latest:
					start_dt = latest.end_dt
				else:
					start_dt = today
		else:
			start_date = today
			end_date = today
			start_dt, end_dt = today, now
		return {'start_date': start_date, 'end_date': end_date, 'start_dt': start_dt, 'end_dt': end_dt, 'date': today}


def merge_collect(slugs):
	if slugs:
		c = Collector()
		objects = [c.get_object(slug) for slug in slugs]
		merged = c.merge_object(*objects)
		return merged


def save_collect(*form_cleaned_datas, test=False):

	contexts = Listorm(norm_context(form_data, verbosing='types') for form_data in form_cleaned_datas)

	dates = sorted(contexts.unique('date'))
	min_start_date, max_end_date = contexts.min('start_date'), contexts.max('end_date')
	total_wards = sorted(set(reduce(lambda acc, elem: acc + elem ,contexts.column_values('wards'))))
	print('saving form data...')
	pprint(contexts)
	print('min_start_date: ', min_start_date)
	print('max_end_date: ', max_end_date)
	print('total_wards:', total_wards)
	print('tested:', test)
	collector = Collector()
	return collector.save(dates, min_start_date, max_end_date, total_wards, *contexts, test=test)


def get_print_context(*form_cleaned_datas):
    counters = []
    c = Collector()
    for counter in form_cleaned_datas:
        counter['object'] = c.get_object(counter.get('slug'))
        counter['objects'] = c.get_parsed(counter.get('slug'))
        for page, count in counter.items():
            if page in counter['objects']:
                counter[page] = list(range(int(count)))
        counters.append(counter)
    return counters

def guess_print_count(request):
    counter = {
        'grp_by_drug_nm': 0,
        'grp_by_ward_drug_nm': 0,
        'grp_by_ward': 0
    }
    c = Collector()

    for data, _ in request.GET.lists():
        query = json.loads(data)
        obj = c.get_object(**query)
        if obj.kinds == ['INJ']:
            if set(obj.types) == {'ST'}:
                counter['grp_by_ward_drug_nm'] = 2
            elif set(obj.types) == {'AD', 'EM'}:
                counter['grp_by_ward_drug_nm'] = 1
            elif set(obj.types) == {'ST', 'AD', 'EM'}:
                counter['grp_by_ward_drug_nm'] = 1
        elif obj.kinds == ['NUT']:
            counter['grp_by_drug_nm'] = 1
            counter['grp_by_ward'] = 1
        elif obj.kinds == ['LABEL']:
            counter['grp_by_drug_nm'] = 1
    return json.dumps(counter)    


class FormInitTime(object):

	def __init__(self, types, wards):
		self.collector = Collector()
		self.types= types
		self.wards = wards
		self.TODAY = datetime.date.today()
		self.NOW = datetime.datetime.now()
		self.YESTERDAY = datetime.date.today() - datetime.timedelta(1)
		self.TOMORROW = datetime.date.today() + datetime.timedelta(1)
		self.START_DATE, self.END_DATE = datetime.date.today(), datetime.date.today()
		self.START_DT, self.END_DT = datetime.date.today(), datetime.datetime.now()
		self.DATE = datetime.date.today()

	def _now_hour(self):
		return datetime.datetime.now().hour

	def _yesterday_last_dt(self, kinds):
		latest = self.collector.db.get_latest(date=self.YESTERDAY, kinds=kinds, types=self.types, wards=self.wards)
		ret = latest.end_dt if latest else self.YESTERDAY
		return time_to_normstr(ret, to='datetime')

	def _today_last_dt(self, kinds):
		latest = self.collector.db.get_latest(date=self.TODAY, kinds=kinds, types=self.types, wards=self.wards)
		ret = latest.end_dt if latest else self.TODAY
		return time_to_normstr(ret, to='datetime')

	def get_default(self, kinds):
		context = {
			'kinds': kinds, 'types': self.types, 'wards': self.wards,
			'date': self.DATE, 'start_date': self.START_DATE, 'end_date': self.END_DATE, 'start_dt': self.START_DT, 'end_dt': self.END_DT
		}
		return context

	def inj_init(self):

		context = self.get_default(['INJ'])
		yesterday_latest_st = self.collector.db.get_latest(date=self.YESTERDAY, kinds=['INJ'], types=['ST'])
		yesterday_latest_ad_em = self.collector.db.get_latest(date=self.YESTERDAY, kinds=['INJ'], types=['EM', 'AD'])
		yesterday_latest_ad_em_st = self.collector.db.get_latest(date=self.YESTERDAY, kinds=['INJ'], types=['EM','ST', 'AD'])
		today_latest_ad_em_st = self.collector.db.get_latest(date=self.TODAY, kinds=['INJ'], types=['EM','ST', 'AD'])
		today_latest_ad_em = self.collector.db.get_latest(date=self.TODAY, kinds=['INJ'], types=['EM', 'AD'])
		yesterday_last_collecteds = sorted(filter(None, [yesterday_latest_st, yesterday_latest_ad_em, yesterday_latest_ad_em_st]), key=itemgetter('end_dt'))
		now_hour = self._now_hour()
		if set(self.types) == {'EM','ST', 'AD'}:
			start_date = self.YESTERDAY
			if today_latest_ad_em_st:
				start_date = self.TODAY	
				start_dt = self._today_last_dt(['INJ'])

			elif yesterday_last_collecteds:
				start_dt = yesterday_last_collecteds[-1]['end_dt']
			else:
				start_dt = self._yesterday_last_dt(['INJ'])
			context['start_dt'] = start_dt
			context['start_date'] = start_date

		elif set(self.types) <= {'EM', 'AD'}:
			if today_latest_ad_em or today_latest_ad_em_st:
				start_date = self.TODAY
				if today_latest_ad_em_st:
					self.types = ['EM', 'ST', 'AD'] # 임시로 바꿈
				start_dt = self._today_last_dt(['INJ'])

			elif yesterday_latest_ad_em:
				start_date = self.YESTERDAY
				start_dt = self._yesterday_last_dt(['INJ'])
			else:
				start_date = self.TODAY
				start_dt = self.TODAY
			context['start_date'], context['start_dt'] = start_date, start_dt

		elif set(self.types) <= {'ST'}:
			start_date = self.TOMORROW
			end_date = self.TOMORROW
			start_dt = self._today_last_dt(['INJ'])
			context['start_date'], context['end_date'], context['start_dt'] = start_date, end_date, start_dt
		else:
			context['start_dt'] = self._today_last_dt(['INJ'])
		return context

	def label_init(self):
		context = self.get_default(['LABEL'])
		context['start_dt'] = self._today_last_dt(['LABEL'])

		if self.types == ['ST']:
			start_date = self.TOMORROW
			end_date = self.TOMORROW
			start_dt = self._today_last_dt(['LABEL'])
			context['start_date'], context['end_date'], context['start_dt'] = start_date, end_date, start_dt
		return context

	def nut_init(self):
		context = self.get_default(['NUT'])
		context['start_dt'] = self._today_last_dt(['NUT'])		
		if self.types == ['ST']:
			start_date = self.TOMORROW
			end_date = self.TOMORROW
			start_dt = self._today_last_dt(['NUT'])
			context['start_date'], context['end_date'], context['start_dt'] = start_date, end_date, start_dt
		return context


def set_form_initial(kinds, types, wards):

	fit = FormInitTime(types, wards)

	if kinds == ['LABEL']:
		initial = fit.label_init()
	elif kinds == ['NUT']:
		initial = fit.nut_init()
	elif kinds == ['INJ']:
		initial = fit.inj_init()
	else:
		initial = fit.get_default(kinds)
	
	initial['date'], initial['start_date'], initial['end_date'] = time_to_normstr(initial['date'], initial['start_date'], initial['end_date'])
	initial['start_dt'], initial['end_dt'] = time_to_normstr(initial['start_dt'], initial['end_dt'], to='datetime')
	return json.dumps(initial)
	

def guess_time_range(request):
    context = {}
    for data, _ in request.GET.lists():
        data = json.loads(data)
        for key, val in data.items():
            for keyword in ('wards', 'kinds', 'types'):
                if keyword in key:
                    context[keyword] = val
    return context
