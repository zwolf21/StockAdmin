import os, sys, re, datetime, math
from pprint import pprint
from collections import namedtuple
from functools import partial, wraps

from listorm import Listorm, read_excel

from dateutil.parser import parse

MODULE_BASE = os.path.dirname(os.path.dirname(__file__))
MODULE_PATH = os.path.join(MODULE_BASE, 'StockAdmin/services/FKHIS')
sys.path.append(MODULE_PATH)


try:
	from .api_requests import OrderSelectApiRequest, DRUG_DB_PATH
	from .dbconn import get_drug_list

except:
	from api_requests import OrderSelectApiRequest, DRUG_DB_PATH
	from dbconn import get_drug_list



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
	def wrapper(types, wards, start_date, end_date, start_dt, end_dt, kind, extras=None, excludes=None, **kwargs):
		types = list(map(lambda type: type_verbose.get(type, type), types))
		wards = re.split('\s*,\s*', wards) if isinstance(wards, str) else wards
		start_date, end_date = time_to_normstr(start_date, end_date)
		start_dt, end_dt = time_to_normstr(start_dt, end_dt, to='datetime')
		kind = kind_reverbose.get(kind, kind)
		extras = re.split('\s*[\r\n]+,*\s*', extras) if isinstance(extras, str) else extras or []
		excludes = re.split('\s*[\r\n]+,*\s*', excludes) if isinstance(excludes, str) else excludes or []
		extras = list(filter(None, extras))
		excludes = list(filter(None, excludes))
		# print(types, wards, start_date, end_date, start_dt, end_dt, kind, extras, excludes)
		return get_orderset(types, wards, start_date, end_date, start_dt, end_dt, kind, extras, excludes, **kwargs)
	return wrapper		


@norm_field
def get_orderset(types, wards, start_date, end_date, start_dt, end_dt, kind, extras=None, excludes=None, test=False):
				
	request = OrderSelectApiRequest(start_date, end_date, wards)

	if test:
		request.set_test_response('response_samples/orderselect/51.rsp')
		request.set_test_response('response_samples/orderselect/52.rsp')
		request.set_test_response('response_samples/orderselect/61.rsp')
		request.set_test_response('response_samples/orderselect/71.rsp')
		request.set_test_response('response_samples/orderselect/81.rsp')
		request.set_test_response('response_samples/orderselect/92.rsp')
		request.set_test_response('response_samples/orderselect/IC.rsp')
	else:
		request.api_calls()

	drug_lst = get_drug_list(kind, extras=extras or [], excludes=excludes or [], test=test)

	drug_lst = drug_lst.select('약품코드', '단일포장구분', '투여경로', '효능코드(보건복지부)', '약품명(한글)', '조제계산기준코드')
	ord_lst = Listorm(request.get_records()).filter(lambda row: row.rcpt_dt and start_dt <= row.rcpt_dt < end_dt and row.rcpt_ord_tp_nm in types and row.medi_no < '40000')
	ord_lst = ord_lst.filter(lambda row: row.drug_nm)
	ord_lst = ord_lst.set_number_type(ord_qty=0.0, ord_frq=0, ord_day=0)
	ord_lst = ord_lst.join(drug_lst, left_on='ord_cd', right_on='약품코드')
	ord_lst = ord_lst.add_columns(once_amt=lambda row: round(row.ord_qty / row.ord_frq, 2), total_amt=lambda row: row.ord_qty * row.ord_day, ward_=lambda row: row.ward[:2])
	ord_lst = ord_lst.update(total_amt=lambda row: math.ceil(row.once_amt)*row.ord_frq, where=lambda row: row['조제계산기준코드'] in ['7'])
	ord_lst = ord_lst.add_columns(type=lambda row: {'정기': 'ST', '응급': 'EM', '추가': 'AD', '퇴원': 'OT'}.get(row.rcpt_ord_tp_nm))
	ord_lst.set_index('ord_seq', 'rcpt_seq', 'ord_exec_seq','rcpt_ord_seq', index_name='pk')
	ord_lst = ord_lst.distinct('pk')
	return ord_lst

def parse_order_list(order_list):
	ord_lst = Listorm(order_list, nomalize=False)
	grp_by_drug_nm = ord_lst.groupby('drug_nm', ord_qty=sum, drug_nm=len, total_amt=sum,
		renames={'drug_nm': 'drug_nm_count', 'total_amt': 'total_amt_sum', 'ord_qty': 'ord_qty_sum'},
		extra_columns = ['ord_cd', 'ord_unit_nm', '단일포장구분', '효능코드(보건복지부)', ],
		set_name = 'order_set'
	)

	grp_by_ward = ord_lst.groupby('WARD', ord_qty=sum, total_amt=sum, drug_nm=len,
		renames={'ord_qty': 'ord_qty_sum', 'total_amt': 'total_amt_sum', 'drug_nm': 'drug_nm_count'}, 
		set_name = 'order_set'
	).orderby('WARD', 'drug_nm')

	grp_by_ward_drug_nm = ord_lst.groupby('WARD', 'drug_nm', ord_qty=sum, total_amt=sum, drug_nm=len,
		renames={'ord_qty': 'ord_qty_sum', 'total_amt': 'total_amt_sum', 'drug_nm': 'drug_nm_count'},
		extra_columns = ['ord_cd', 'ord_unit_nm', '단일포장구분', '효능코드(보건복지부)'],
		set_name = 'order_set'
	).orderby('WARD', 'drug_nm')

	live_order_list = ord_lst.filter(lambda row: row.dc_gb == 'N' and row.ret_stus not in ['O', 'C'])
	dc_order_list = ord_lst.filter(lambda row: row.dc_gb == 'Y')
	not_dc_order_list = ord_lst.filter(lambda row: row.dc_gb == 'N')
	ret_order_list = ord_lst.filter(lambda row: row.ret_stus == 'O')
	only_dc = ord_lst.filter(lambda row: row.ret_stus not in ['O', 'C'] and row.dc_gb == 'Y')
	only_ret = ord_lst.filter(lambda row: row.dc_gb != 'Y' and row.ret_stus == 'O')
	dc_or_ret = ord_lst.filter(lambda row: row.dc_gb == 'Y' or row.ret_stus == 'O')

	grp_dc_by_ward = dc_order_list.groupby('WARD', ord_qty=sum, total_amt=sum, drug_nm=len,
		renames={'ord_qty': 'ord_qty_sum', 'total_amt': 'total_amt_sum', 'drug_nm': 'drug_nm_count'}, 
		set_name='order_set'
	).orderby('WARD', 'drug_nm')
	grp_ret_by_ward = ret_order_list.groupby('WARD', ord_qty=sum, total_amt=sum, drug_nm=len,
		renames={'ord_qty': 'ord_qty_sum', 'total_amt': 'total_amt_sum', 'drug_nm': 'drug_nm_count'}, 
		set_name='order_set'
	).orderby('WARD', 'drug_nm')

	nt = namedtuple('OrderCollections', 'count order_list live_order_list dc_order_list not_dc_order_list ret_order_list only_dc only_ret dc_or_ret grp_by_drug_nm grp_by_ward grp_by_ward_drug_nm grp_dc_by_ward grp_ret_by_ward')

	context = nt(
		count = len(ord_lst),
		order_list = ord_lst,
		live_order_list = live_order_list, 
		dc_order_list = dc_order_list,
		not_dc_order_list = not_dc_order_list, 
		ret_order_list = ret_order_list, 
		only_dc = only_dc,
		only_ret = only_ret,
		dc_or_ret = dc_or_ret,
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




