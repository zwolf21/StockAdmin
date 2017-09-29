import os, json, sys, datetime
from pprint import pprint
from itertools import chain
from operator import itemgetter

from listorm import Listorm
from StockAdmin.services.FKHIS.order_apis import OrderApi, time_to_normstr, type_verbose, kind_reverbose, kind_verbose

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
		date = time_to_normstr(date)
		timestamp = time_to_normstr(datetime.datetime.now(), to='datetime')
		start_date, end_date = time_to_normstr(start_date, end_date)
		vtypes = list(map(type_verbose.get, types))
		print(vtypes)
		vkinds = list(map(kind_verbose.get, kinds))
		context = {
			'date': date, 'kinds':kinds, 'types': types, 'wards': wards, 'start_date': start_date, 'end_date': end_date,
			'seq': seq, 'title': title, 'vtypes': vtypes, 'vkind': vkinds, 'timestamp': timestamp
		}
		return context


	def save(self, date, start_date, end_date, wards, *contexts, commit=True, test=False):
		oa = OrderApi(static=self.config.get(), date=date, start_date=start_date, end_date=end_date, wards=wards, test=test)
		print(contexts)
		for context, queryset in zip(contexts, oa.get_order_lists(*contexts)):
			types = context['types']
			print(context)
			# OrderApi._norm_context(context
			start_dt, end_dt = context['start_dt'], context['end_dt']
			obj = self._generate_initial_object(
				date=date, kinds=context['kinds'], types=types, wards=wards,
				start_date = start_date, end_date=end_date, len_queryset = len(queryset)
			)
			obj['queryset'] = queryset
			self.db.save(obj, commit)
	


	def get_time_options(self, kind, types, **kwargs):
		today = datetime.date.today()
		yesterday = today - datetime.timedelta(1)
		tomorrow = today + datetime.timedelta(1)
		now = datetime.datetime.now()
		end_dt = now
		if set(types) == {'ST', 'AD', 'EM'}:
			today_latest = self.db.get_latest(date=today, kind=kind, types=types)
			if today_latest:
				# print(types, today_latest)
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
					start_date = yesterday
					start_dt = yesterday
		else:
			start_date = today
			end_date = today
			start_dt, end_dt = today, now
		# start_date, end_date = time_to_normstr(start_date, end_date)
		# start_dt, end_dt = time_to_normstr(start_dt, end_dt)
		return {'start_date': start_date, 'end_date': end_date, 'start_dt': start_dt, 'end_dt': end_dt}



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
	collector.save(date, start_date, end_date, wards, *contexts, test=test)
























