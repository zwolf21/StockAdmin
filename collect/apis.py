import os, json, sys, datetime
from pprint import pprint
from itertools import chain
from operator import itemgetter

from dateutil.parser import parse
from listorm import Listorm
from StockAdmin.services.FKHIS.order_apis import OrderApi, time_to_normstr, type_verbose, kind_reverbose, kind_verbose, parse_order_list

from .storages import CollectStorage, StaticStorage, COLLECT_FILE, STATIC_INFO_FILE, MAX_OBJECT_LIST_LENGTH




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
		kinds = '/'.join(map(lambda k: kind_verbose.get(k,k), kinds))
		date = time_to_normstr(date)
		return "{} {} {} {} 차({}건)".format(date, kinds, types, seq, count)

	def _generate_seq(self, date, kinds, types, wards):
		date = time_to_normstr(date)
		latest = self.db.object_list.filterand(date=date, kinds=kinds, types=types, wards=wards).max('seq')
		return latest + 1 if latest else 1

	def _generate_initial_object(self, date, kinds, types, wards, start_date, end_date, len_queryset):
		seq = self._generate_seq(date, kinds, types, wards)
		title = self._generate_title(date, kinds, types, seq, len_queryset)
		slug = self._generate_slug(date, kinds, types, wards, seq)
		date = time_to_normstr(date)
		timestamp = time_to_normstr(datetime.datetime.now(), to='datetime')
		start_date, end_date = time_to_normstr(start_date, end_date)
		vtypes = list(map(type_verbose.get, types))
		vkinds = list(map(kind_verbose.get, kinds))
		context = {
			'date': date, 'kinds':kinds, 'types': types, 'wards': wards, 'start_date': start_date, 'end_date': end_date,
			'seq': seq, 'title': title, 'vtypes': vtypes, 'vkind': vkinds, 'timestamp': timestamp, 'slug':slug
		}
		return context

	def save(self, date, start_date, end_date, wards, *contexts, commit=True, test=False):
		oa = OrderApi(static=self.config.get(), date=date, start_date=start_date, end_date=end_date, wards=wards, test=test)
		for context, queryset in zip(contexts, oa.get_order_lists(*contexts)):
			types = context['types']
			start_dt, end_dt = context['start_dt'], context['end_dt']
			obj = self._generate_initial_object(
				date=date, kinds=context['kinds'], types=types, wards=wards,
				start_date = start_date, end_date=end_date, len_queryset = len(queryset)
			)
			obj['queryset'] = queryset
			obj['start_dt'], obj['end_dt'] = time_to_normstr(start_dt, end_dt, to='datetime')
			self.db.save(obj, commit)
		# ret lastest object
		return obj

	def last(self, **kwargs):
		if kwargs:
			return self.db.get_latest(**kwargs)
		return self.db.object_list.last

	def get_parsed(self, slug):
		obj = self.get_object(slug)
		context = parse_order_list(obj.queryset)
		return context

	def get_queryset(self):
		today = datetime.date.today()
		def since(date_str):
			date = parse(date_str)
			if today.day == date.day:
				return 'today'
			elif (date + datetime.timedelta(1)).day == today.day:
				return 'yesterday'
			return ''
		queryset = self.db.object_list.add_columns(since=lambda row: since(row.date))
		return queryset[::-1]

	def get_object(self, slug):
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





def serialize_context(start_dt, end_dt, types, kinds, **kwargs):
	context = {
		'start_dt': start_dt, 'end_dt': end_dt, 'types': types, 'kinds':kinds
	}
	return context

def serialize_query(date, start_date, end_date, wards, **kwargs):
	context = {
		'date': date, 'start_date': start_date, 'end_date': end_date, 'wards': wards
	}
	return context




def save_collect(*form_cleaned_datas, test=False):
	querys = Listorm()
	contexts = Listorm()
	for form_data in form_cleaned_datas:
		query = serialize_query(**form_data)
		context = serialize_context(**form_data)
		querys.append(query)
		contexts.append(context)

	# 날짜 조회 범위 정하기
	start_date, end_date = querys.min('start_date'), querys.max('end_date')

	# 병동 조회 범위 정하기
	wardset = []
	for wards in querys.column_values('wards'):
		wardset += wards

	wards = sorted(set(wardset))
	date = querys[0].date

	collector = Collector()
	return collector.save(date, start_date, end_date, wards, *contexts, test=test)








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
		yesterday_latest_ad_em = self.collector.db.get_latest(date=self.YESTERDAY, kinds=['INJ'], types=['AD', 'EM'])
		yesterday_latest_ad_em_st = self.collector.db.get_latest(date=self.YESTERDAY, kinds=['INJ'], types=['ST', 'AD', 'EM'])
		today_latest_ad_em_st = self.collector.db.get_latest(date=self.TODAY, kinds=['INJ'], types=['ST', 'AD', 'EM'])
		today_latest_ad_em = self.collector.db.get_latest(date=self.TODAY, kinds=['INJ'], types=['AD', 'EM'])
	
		yesterday_last_collecteds = sorted(filter(None, [yesterday_latest_st, yesterday_latest_ad_em, yesterday_latest_ad_em_st]), key=itemgetter('end_dt'))
		now_hour = self._now_hour()

		if self.types == ['ST', 'AD', 'EM']:
			start_date = self.YESTERDAY
			if today_latest_ad_em_st:
				start_date = self.TODAY	
				start_dt = self._today_last_dt(['INJ'])

			elif yesterday_last_collecteds:
				start_dt = yesterday_last_collecteds[-1]['end_dt']
			else:
				start_dt = self._yesterday_last_dt(['INJ'])
				print('start_dt:', start_dt)
			context['start_dt'] = start_dt
			context['start_date'] = start_date

		elif self.types == ['AD', 'EM']:
			if today_latest_ad_em:
				start_date = self.TODAY
				start_dt = self._today_last_dt(['INJ'])
			elif yesterday_latest_ad_em:
				start_date = self.YESTERDAY
				start_dt = self._yesterday_last_dt(['INJ'])
			else:
				start_date = self.TODAY
				start_dt = self.TODAY
			context['start_date'], context['start_dt'] = start_date, start_dt

		elif self.types == ['ST']:
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
