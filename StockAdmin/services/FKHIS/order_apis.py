import os, sys, re, datetime, math
from pprint import pprint
from collections import namedtuple
from functools import partial, wraps
from listorm import Listorm, read_excel

from dateutil.parser import parse

MODULE_BASE = os.path.dirname(os.path.dirname(__file__))
MODULE_PATH = os.path.join(MODULE_BASE, 'StockAdmin/services/FKHIS')
sys.path.append(MODULE_PATH)
# from .listorm import Listorm, read_excel


try:
	from .api_requests import OrderSelectApiRequest, DRUG_DB_PATH
	from .dbconn import get_drug_list, get_all_list
	from .order_mon import get_order_object_list, get_order_object_list_test

except:
	from api_requests import OrderSelectApiRequest, DRUG_DB_PATH
	from dbconn import get_drug_list, get_all_list
	from order_mon import get_order_object_list, get_order_object_list_test


type_order = {'ST':1, 'AD':2, 'EM':3, 'OT':4}
type_verbose = {'ST': '정기', 'AD': '추가', 'EM': '응급', 'OT': '퇴원'}
kind_verbose = {'NUT': '영양수액', 'INJ': '주사', 'LABEL': '라벨'}
kind_reverbose = {'영양수액':'NUT', '주사':'INJ', '라벨':'LABEL'}


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


def norm_field(get_orderset):
	@wraps(get_orderset)
	def wrapper(types, wards, start_date, end_date, start_dt, end_dt, kind, kinds=None, date=None, get_static=None, **kwargs):
		types = list(map(lambda type: type_verbose.get(type, type), types))
		wards = re.split('\s*,\s*', wards) if isinstance(wards, str) else wards
		start_date, end_date = time_to_normstr(start_date, end_date)
		start_dt, end_dt = time_to_normstr(start_dt, end_dt, to='datetime')
		kind = kind_reverbose.get(kind, kind)

		# norm_static = []
		# for row in static:
		# 	extras, excludes, kind = row['extras'], row['excludes'], row['kind']
		# 	norm_static.append({'extras': extras, 'excludes': excludes, 'kind':kind})

		date = date or datetime.date.today()
		date = date if isinstance(date, str) else time_to_normstr(date)
		return get_orderset(types=types, wards=wards, start_date=start_date, end_date=end_date, start_dt=start_dt, end_dt=end_dt, kind=kind, kinds=kinds, date=date, get_static=get_static, **kwargs)
	return wrapper		


unit_sort = lambda unit: {'ML': 100, 'G': 101, '통': 102, 'BAG':998, 'KIT': 1000, 'VIAL': 1001, 'AMP': 1002, 'SYR': 1003}.get(unit, 0)


@norm_field
def get_orderset(types, wards, start_date, end_date, start_dt, end_dt, kind=None, kinds=None, date=None, get_static=None, test=False):
	request = OrderSelectApiRequest(start_date, end_date, wards)

	if test:
		ptnt_lst = get_order_object_list_test(start_date)
		request.set_test_response('response_samples/orderselect/51.rsp')
		request.set_test_response('response_samples/orderselect/52.rsp')
		request.set_test_response('response_samples/orderselect/61.rsp')
		request.set_test_response('response_samples/orderselect/71.rsp')
		request.set_test_response('response_samples/orderselect/81.rsp')
		request.set_test_response('response_samples/orderselect/92.rsp')
		request.set_test_response('response_samples/orderselect/IC.rsp')
	else:
		# 환자 정보를 불러서 처방리스트에 조인 하여 전실 완료된 병동을 얻는다.(기본 값으로 당일자로 조회)
		ptnt_lst = get_order_object_list(date)
		request.api_calls()
	ord_lst = Listorm(request.get_records()).filter(lambda row: row.rcpt_dt and start_dt <= row.rcpt_dt < end_dt and row.rcpt_ord_tp_nm in types)

	kinds = kinds if kinds else [kind]

	for kind in kinds:
		static = get_static(kind)
		extras, excludes = static.extras, static.excludes
		extras = re.split('\s*[\r\n]+,*\s*', extras) if isinstance(extras, str) else static.extras or []
		excludes = re.split('\s*[\r\n]+,*\s*', excludes) if isinstance(excludes, str) else static.excludes or []
		extras = list(filter(None, extras))
		excludes = list(filter(None, excludes))
		drug_lst, plus, minus = get_drug_list(kind, extras=extras, excludes=excludes, test=test)
		ptnt_lst = ptnt_lst.select('ptnt_no', 'ward').rename(ward='WARD').distinct('ptnt_no') # WARD: 전실 완료된 병동 정보
		ptnt_lst = ptnt_lst.update(WARD=lambda row: row.WARD[:2])
		drug_lst = drug_lst.select('약품코드', '단일포장구분', '투여경로', '효능코드(보건복지부)', '약품명(한글)', '조제계산기준코드', '보관방법코드')
		ord_lst = ord_lst.join(ptnt_lst, on='ptnt_no', how='left').update(WARD=lambda row: row.ward[:2], where=lambda row: not row.WARD) # 전실 정보를 받지 못한 환자는 기본(ward) 병동으로 채움
		ord_lst = ord_lst.filter(lambda row: row.drug_nm)
		ord_lst = ord_lst.set_number_type(ord_qty=0.0, ord_frq=0, ord_day=0)
		ord_lst = ord_lst.join(drug_lst, left_on='ord_cd', right_on='약품코드')
		ord_lst = ord_lst.add_columns(once_amt=lambda row: round(row.ord_qty / row.ord_frq, 2), total_amt=lambda row: row.ord_qty * row.ord_day, ward_=lambda row: row.ward[:2])
		ord_lst = ord_lst.update(total_amt=lambda row: math.ceil(row.once_amt)*row.ord_frq, where=lambda row: row['조제계산기준코드'] in ['7']) # 회수로 올림 약(7)의 경우 total_amt 의 재계산
		ord_lst = ord_lst.add_columns(type=lambda row: {'정기': 'ST', '응급': 'EM', '추가': 'AD', '퇴원': 'OT'}.get(row.rcpt_ord_tp_nm))
		ord_lst.set_index('ord_seq', 'rcpt_seq', 'ord_exec_seq','rcpt_ord_seq', index_name='pk')
		ord_lst = ord_lst.distinct('pk')
		yield ord_lst, plus, minus

def parse_order_list(order_list):
	ord_lst = Listorm(order_list, nomalize=False)
	# ret_lst = ord_lst.filterand(ret_yn='Y')
	ret_lst = ord_lst.filter(lambda row: row.medi_no and row.medi_no >= '40000')
	ord_lst = ord_lst.filter(lambda row: row.medi_no and row.medi_no < '40000')
	# ord_lst = ord_lst.add_columns()

	grp_by_ward = ord_lst.groupby('WARD', ord_qty=sum, total_amt=sum, drug_nm=len,
		renames={'ord_qty': 'ord_qty_sum', 'total_amt': 'total_amt_sum', 'drug_nm': 'drug_nm_count'}, 
		set_name = 'order_set'
	).orderby('WARD', 'drug_nm')
	# grp_by_ward['order_set'] = grp_by_ward.order_set.order_by('drug_nm')
	# print('orderby')

	grp_by_ward_drug_nm = ord_lst.groupby('WARD', 'ord_cd', ord_qty=sum, total_amt=sum, drug_nm=len,
		renames={'ord_qty': 'ord_qty_sum', 'total_amt': 'total_amt_sum', 'drug_nm': 'drug_nm_count'},
		extra_columns = ['ord_cd', 'ord_unit_nm', '단일포장구분', '효능코드(보건복지부)', '단일포장구분', 'std_unit_nm', '보관방법코드', 'drug_nm'],
		set_name = 'order_set'
	).orderby('WARD','보관방법코드', lambda row: unit_sort(row.std_unit_nm), '단일포장구분', 'drug_nm')

	live_order_list = ord_lst.filter(lambda row: row.dc_gb == 'N' and row.ret_stus not in ['O', 'C'])
	dc_order_list = ord_lst.filter(lambda row: row.dc_gb == 'Y')
	not_dc_order_list = ord_lst.filter(lambda row: row.dc_gb == 'N')
	ret_order_list = ord_lst.filter(lambda row: row.ret_stus == 'O')
	only_dc = ord_lst.filter(lambda row: row.ret_stus not in ['O', 'C'] and row.dc_gb == 'Y')
	only_ret = ord_lst.filter(lambda row: row.dc_gb != 'Y' and row.ret_stus == 'O')
	dc_or_ret = ord_lst.filter(lambda row: row.dc_gb == 'Y' or row.ret_stus == 'O').orderby('WARD','보관방법코드', lambda row: unit_sort(row.std_unit_nm), '단일포장구분', 'drug_nm')
	# dc_or_ret|= ret_lst
	dc_and_ret = (ret_lst | only_dc).orderby('WARD','보관방법코드', lambda row: unit_sort(row.std_unit_nm), '단일포장구분', 'drug_nm')

	grp_dc_and_ret = dc_and_ret.groupby('WARD', 'medi_no', 'ord_cd','ptnt_no', ord_qty=sum, total_amt=sum, drug_nm=len,
		renames = {'ord_qty': 'ord_qty_sum', 'total_amt': 'total_amt_sum', 'drug_nm': 'drug_nm_count'},
		extra_columns = ['ptnt_nm', 'dc_ent_dt', 'ret_ymd', 'ord_ent_dt', '보관방법코드', '단일포장구분'],
	).orderby('WARD','보관방법코드', lambda row: unit_sort(row.std_unit_nm), '단일포장구분', 'drug_nm')

	grp_by_drug_nm = ord_lst.groupby('drug_nm', ord_qty=sum, drug_nm=len, total_amt=sum,
		renames={'drug_nm': 'drug_nm_count', 'total_amt': 'total_amt_sum', 'ord_qty': 'ord_qty_sum'},
		extra_columns = ['ord_cd', 'ord_unit_nm', '단일포장구분', '효능코드(보건복지부)', 'std_unit_nm', '보관방법코드'],
		set_name = 'order_set'
	).orderby('보관방법코드', lambda row: unit_sort(row.std_unit_nm),'단일포장구분', 'drug_nm')
	
	# 반납약 빼기 표시
	dcret_counts = grp_dc_and_ret.groupby('ord_cd', total_amt_sum=sum,
		renames = {'total_amt_sum': 'minus_count'}
	)
	# grp_by_ward_drug_nm = grp_by_ward_drug_nm.join(dcret_counts, on=['WARD','ord_cd'], how='left')


	grp_dc_by_ward = dc_order_list.groupby('WARD', ord_qty=sum, total_amt=sum, drug_nm=len,
		renames={'ord_qty': 'ord_qty_sum', 'total_amt': 'total_amt_sum', 'drug_nm': 'drug_nm_count'}, 
		set_name='order_set'
	).orderby('WARD', 'drug_nm')
	grp_ret_by_ward = ret_order_list.groupby('WARD', ord_qty=sum, total_amt=sum, drug_nm=len,
		renames={'ord_qty': 'ord_qty_sum', 'total_amt': 'total_amt_sum', 'drug_nm': 'drug_nm_count'}, 
		set_name='order_set'
	).orderby('WARD', 'drug_nm')

	nt = namedtuple('OrderCollections', 'count order_list  not_dc_order_list ret_order_list only_dc only_ret dc_or_ret dc_and_ret grp_dc_and_ret grp_by_drug_nm grp_by_ward grp_by_ward_drug_nm grp_dc_by_ward grp_ret_by_ward')

	context = nt(
		count = len(ord_lst),
		order_list = ord_lst,
		not_dc_order_list = not_dc_order_list, 
		ret_order_list = ret_order_list, 
		only_dc = only_dc,
		only_ret = only_ret,
		dc_or_ret = dc_or_ret,
		dc_and_ret = dc_and_ret,
		grp_dc_and_ret = grp_dc_and_ret,
		grp_by_drug_nm = grp_by_drug_nm,
		grp_by_ward_drug_nm = grp_by_ward_drug_nm,
		grp_by_ward = grp_by_ward, 
		grp_dc_by_ward = grp_dc_by_ward,
		grp_ret_by_ward = grp_ret_by_ward, 
	)
	return context



# ret = get_orderset(types=['정기', '추가', '응급', '퇴원'],
# 	wards=['51'], 
# 	start_date='2017-09-20', end_date='2017-09-20',
# 	start_dt='2016-09-19 00:00:00', end_dt='2017-09-20 00:00:00', 
# 	kind='NUT',
# 	# extras = ['란스톤15', '테리본', '하루날디'],
# 	# excludes = ['오마프원', '하모닐란', '위너프', '슈프라민', '멀티플렉스'],
# 	test=False
# )

# pprint(ret.first)





class OrderApi(object):
	type_order = {'ST':1, 'AD':2, 'EM':3, 'OT':4}
	type_verbose = {'ST': '정기', 'AD': '추가', 'EM': '응급', 'OT': '퇴원'}
	kind_verbose = {'NUT': '영양수액', 'INJ': '주사', 'LABEL': '라벨'}
	kind_reverbose = {'영양수액':'NUT', '주사':'INJ', '라벨':'LABEL'}

	# def __init__(self, start_date, end_date, wards, extras=None, excludes=None, test=False):
	# 	self.start_date, self.end_date = start_date, end_date
	# 	self.drug_list = get_drug_list(test=test)

	def __init__(self, static=None, test=False, **kwargs):
	# def __init__(self, dates, start_date, end_date, wards, static=None, test=False, **kwargs):
		kwargs['start_date'], kwargs['end_date'] = time_to_normstr(kwargs.get('start_date'), kwargs.get('end_date'))
		self.ptnt_lst = Listorm()
		self.static= self._norm_static(static)
		self.drug_list = get_all_list(test=test)
		self.set_order_list(test=test, **kwargs)
		if not test:
			self.set_ptnt_list(**kwargs)

	def _norm_context(self, *contexts):
		for context in contexts:
			types = map(lambda t: type_verbose.get(t, t), context['types'])
			types = sorted(types, key=lambda t:self.type_order.get(t,t))
			context['types'] = types
			context['start_dt'], context['end_dt'] = time_to_normstr(context['start_dt'], context['end_dt'], to='datetime')
		return context

	def _norm_static(self, static):
		new = []
		static = Listorm(static) or Listorm()
		for row in static:
			kind = row.get('kind')
			extras, excludes = row.get('extras') or Listorm(), row.get('excludes') or Listorm()
			extras = re.split('\s*[\r\n]+,*\s*', extras) if isinstance(extras, str) else extras or Listorm()
			excludes = re.split('\s*[\r\n]+,*\s*', excludes) if isinstance(excludes, str) else excludes or []
			new.append({'kind': kind, 'extras': extras, 'excludes': excludes})
		return Listorm(new)

	def _get_test_order_list(self, start_date, end_date, wards, **kwargs):
		request = OrderSelectApiRequest(start_date, end_date, wards)
		for ward in wards:
			request.set_test_response('response_samples/orderselect/{}.rsp'.format(ward))
		return Listorm(request.get_records())

	def _get_order_list(self, start_date, end_date, wards, **kwargs):
		request = OrderSelectApiRequest(start_date, end_date, wards)
		request.api_calls()
		return Listorm(request.get_records())
		
	def set_order_list(self, test, **kwargs):
		if test:
			self.order_list = self._get_test_order_list(**kwargs)
		else:
			self.order_list = self._get_order_list(**kwargs)

	def set_ptnt_list(self, dates, **kwargs):
		dates = [dates] if isinstance(dates, (str, datetime.datetime, datetime.date)) else dates
		ptnts = Listorm()
		for date in dates:
			date = time_to_normstr(date)
			ptnts |= Listorm(get_order_object_list(date)).select('ptnt_no', 'ward').rename(ward='WARD').distinct('ptnt_no')
		self.ptnt_lst = ptnts

	def filter_drug_list(self, kinds, **kwargs):
		static = self.static or {}
		drug_list = Listorm()
		for kind in kinds:
			static = self.static.filterand(kind=kind).first
			extras, excludes = static.extras, static.excludes 
			extras_lst = self.drug_list.filtersim(**{'약품명(한글)': extras})
			if kind == 'LABEL':
				lst = self.drug_list.filter(lambda row: row['단일포장구분'] in ['S', 'P']).orderby('-단일포장구분', '약품명(한글)')
			elif kind == 'NUT':
				lst = self.drug_list.filter(lambda row: row['효능코드(보건복지부)'] in ['325'])
			elif kind == 'INJ':
				lst = self.drug_list.filter(
					lambda row: row['투여경로'] == '3' and row['효능코드(보건복지부)'] not in ['325', '323', '331'] and row['약품법적구분'] in ['0'] and row['항암제구분'] == '0'
				)

			drug_list|= lst.excludesim(**{'약품명(한글)': excludes}) | extras_lst
		return drug_list

	def filter_order_list(self, types, start_dt, end_dt, **kwargs):
		return self.order_list.filter(lambda row: row.rcpt_dt and start_dt <= row.rcpt_dt < end_dt and row.rcpt_ord_tp_nm in types)

	def get_order_lists(self, *filter_contexts, **kwargs):
		for context in filter_contexts:
			context = self._norm_context(context)
			drug_list = self.filter_drug_list(**context).select('약품코드', '단일포장구분', '투여경로', '효능코드(보건복지부)', '약품명(한글)', '조제계산기준코드', '보관방법코드')
			order_list = self.filter_order_list(**context)
			order_list = order_list.join(drug_list, left_on='ord_cd', right_on='약품코드')

			if self.ptnt_lst:
				order_list = order_list.join(self.ptnt_lst, on='ptnt_no', how='left').update(WARD=lambda row: row.ward[:2], where=lambda row: not row.WARD) # 전실 정보를 받지 못한 환자는 기본(ward) 병동으로 채움
			else:
				order_list = order_list.update(ward=lambda row: row.ward[:2]).rename(ward='WARD')

			order_list = order_list.filter(lambda row: row.drug_nm)
			order_list = order_list.set_number_type(ord_qty=0.0, ord_frq=0, ord_day=0)
			order_list = order_list.add_columns(once_amt=lambda row: round(row.ord_qty / row.ord_frq, 2), total_amt=lambda row: row.ord_qty * row.ord_day, ward_=lambda row: row.ward[:2])
			order_list = order_list.update(total_amt=lambda row: math.ceil(row.once_amt)*row.ord_frq, where=lambda row: row['조제계산기준코드'] in ['7']) # 회수로 올림 약(7)의 경우 total_amt 의 재계산
			order_list = order_list.add_columns(type=lambda row: {'정기': 'ST', '응급': 'EM', '추가': 'AD', '퇴원': 'OT'}.get(row.rcpt_ord_tp_nm, ''))
			order_list.set_index('ord_seq', 'rcpt_seq', 'ord_exec_seq','rcpt_ord_seq', index_name='pk')	
			yield order_list

	def parse_order_list(self, order_list):
		ret_lst = order_list.filter(lambda row: row.medi_no and row.medi_no >= '40000')
		ord_lst = order_list.filter(lambda row: row.medi_no and row.medi_no < '40000')

		grp_by_drug_nm = ord_lst.groupby('drug_nm', ord_qty=sum, drug_nm=len, total_amt=sum,
			renames={'drug_nm': 'drug_nm_count', 'total_amt': 'total_amt_sum', 'ord_qty': 'ord_qty_sum'},
			extra_columns = ['ord_cd', 'ord_unit_nm', '단일포장구분', '효능코드(보건복지부)', 'std_unit_nm', '보관방법코드'],
			set_name = 'order_set'
		).orderby('보관방법코드', lambda row: unit_sort(row.std_unit_nm),'단일포장구분', 'drug_nm')

		grp_by_ward = ord_lst.groupby('WARD', ord_qty=sum, total_amt=sum, drug_nm=len,
			renames={'ord_qty': 'ord_qty_sum', 'total_amt': 'total_amt_sum', 'drug_nm': 'drug_nm_count'}, 
			set_name = 'order_set'
		).orderby('WARD', 'drug_nm')

		grp_by_ward_drug_nm = ord_lst.groupby('WARD', 'drug_nm', ord_qty=sum, total_amt=sum, drug_nm=len,
			renames={'ord_qty': 'ord_qty_sum', 'total_amt': 'total_amt_sum', 'drug_nm': 'drug_nm_count'},
			extra_columns = ['ord_cd', 'ord_unit_nm', '단일포장구분', '효능코드(보건복지부)', '단일포장구분', 'std_unit_nm', '보관방법코드', 'drug_nm'],
			set_name = 'order_set'
		).orderby('WARD','보관방법코드', lambda row: unit_sort(row.std_unit_nm), '단일포장구분', 'drug_nm')

		grp_by_ward_drug_nm_by_ward = grp_by_ward_drug_nm.groupby('WARD', drug_nm=len,
			renames = {'drug_nm': 'drug_nm_count'},
			extra_columns = ['WARD'],
			set_name = 'ward_set'
		).orderby('WARD')

		only_dc = ord_lst.filter(lambda row: row.ret_stus not in ['O', 'C'] and row.dc_gb == 'Y')
		dc_and_ret = (ret_lst | only_dc).orderby('WARD','보관방법코드', lambda row: unit_sort(row.std_unit_nm), '단일포장구분', 'drug_nm')

		grp_dc_and_ret = dc_and_ret.groupby('WARD', 'medi_no', 'ord_cd','ptnt_no', ord_qty=sum, total_amt=sum, drug_nm=len,
			renames = {'ord_qty': 'ord_qty_sum', 'total_amt': 'total_amt_sum', 'drug_nm': 'drug_nm_count'},
			extra_columns = ['ptnt_nm', 'dc_ent_dt', 'ret_ymd', 'ord_ent_dt', '보관방법코드', '단일포장구분'],
		).orderby('WARD','보관방법코드', lambda row: unit_sort(row.std_unit_nm), '단일포장구분', 'drug_nm')

		grp_dc_and_ret_by_ward = grp_dc_and_ret.groupby('WARD', drug_nm=len,
			renames = {'drug_nm': 'drug_nm_count'},
			set_name = 'dc_and_ret'
		)

		grp_by_ward_drug_nm_by_ward = grp_by_ward_drug_nm_by_ward.join(grp_dc_and_ret_by_ward, on='WARD', how='left').update(dc_and_ret=Listorm(), where=lambda row: not row.dc_and_ret)
		grp_by_ward_drug_nm_by_ward = grp_by_ward_drug_nm_by_ward.orderby('WARD')
		return {
			'grp_by_drug_nm':grp_by_drug_nm,
			'grp_by_ward': grp_by_ward,
			'grp_by_ward_drug_nm': grp_by_ward_drug_nm,
			'grp_by_ward_drug_nm_by_ward':grp_by_ward_drug_nm_by_ward,
			'grp_dc_and_ret': grp_dc_and_ret,
		}





static=[
    {
        "extras": "",
        "kind": "LABEL",
        "excludes": ""
    },
    {
        "extras": "염화칼륨\r\n염화나트륨주사액\r\n",
        # "extras": "",
        "kind": "INJ",
        "excludes": "에락시스\r\n멕쿨"
    },
    {
        "extras": "란스톤\r\n아달라트\r\n",
        # "extras": '''에락시스
        # ''',
        "kind": "NUT",
        "excludes": ""
    }
]

contexts = [
	{
		'start_dt': '2017-09-19 00:00:00',
		'end_dt': '2017-09-20 00:00:00',
		'types': ['정기', 'AD','EM'],
		'kinds': ['INJ'],
	},
	# {
	# 	'start_dt': '2017-09-19 00:00:00',
	# 	'end_dt': '2017-09-20 23:59:59',
	# 	'types': ['추가','응급', '정기'],
	# 	'kinds': ['INJ', 'NUT']
	# },
	# {
	# 	'start_dt': '2017-09-19 00:00:00',
	# 	'end_dt': '2017-09-28 23:59:59',
	# 	'types': ['추가','응급', '정기'],
	# 	'kinds': ['INJ', 'NUT', 'LABEL']
	# },
	# {
	# 	'start_dt': '2017-09-19 00:00:00',
	# 	'end_dt': '2017-09-20 23:59:59',
	# 	'types': ['추가','응급', 'ST'],
	# 	'kinds': ['NUT', 'LABEL']
	# },
]

# oa = OrderApi(
# 	dates=datetime.datetime.now(), start_date='2017-09-20', end_date='2017-09-20', wards=['51', '52', '61', '71', '81', '92', 'IC'],  static=static, test=True)
# # pprint(len(oa.drug_list))
# # print(len(oa.ptnt_lst))
# # print(len(oa.order_list))
# # drug_list=oa.filter_drug_list(['INJ', 'NUT'])
# # pprint(drug_list.select('약품명(한글)').filter(lambda row: '트라우밀' in row['약품명(한글)']))
# # print(len(drug_list))
# # order_list = oa.filter_order_list([ '추가', '응급'], '2017-09-28 16:00:00', '2017-09-28 23:59:59')
# # print(len(order_list))
# for orderlist in oa.get_order_lists(*contexts):
# 	parsed = oa.parse_order_list(orderlist)
# 	for wards in parsed['grp_by_ward_drug_nm_by_ward']:
# 		print('----collect',wards.WARD)
# 		for ward in wards.ward_set:
# 			print(ward.drug_nm, ward.total_amt_sum)
# 		print('-----DC LIST')
# 		for dcret in wards.dc_and_ret:
# 			print(dcret.medi_no, dcret.drug_nm, dcret.total_amt_sum, dcret.ret_ymd, dcret.dc_ent_dt or dcret.ord_ent_dt)





