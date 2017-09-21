import os, sys, datetime
from pprint import pprint
from collections import namedtuple
from listorm import Listorm, read_excel
from dateutil.parser import parse

MODULE_BASE = os.path.dirname(os.path.dirname(__file__))
MODULE_PATH = os.path.join(MODULE_BASE, 'StockAdmin/services/FKHIS')
sys.path.append(MODULE_PATH)

from api_requests import OrderSelectApiRequest, DRUG_DB_PATH
from dbconn import get_drug_list



def _time_to_str(*time_values, to='date'):
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
		return tuple(map(lambda time: time.strftime("%Y-%m-%d"), ret))
	else:
		return tuple(map(lambda time: time.strftime("%Y-%m-%d %H:%M:%S"), ret))

						
def get_orderset(types, wards, start_date, end_date, start_dt, end_dt, kind='LABEL', test=False):

	start_date, end_date = _time_to_str(start_date, end_date)
	start_dt, end_dt = _time_to_str(start_dt, end_dt, to='datetime')

	request = OrderSelectApiRequest(start_date, end_date, wards)

	if test:
		start_dt, end_dt = '2017-09-15 00:00:00', '2017-09-21 00:00:00'
		request.set_test_response('response_samples/orderselect')
	else:
		request.api_calls()

	drug_lst = get_drug_list(kind, test)
	drug_lst = drug_lst.select('약품코드', '단일포장구분', '투여경로', '효능코드(보건복지부)')
	ord_lst = Listorm(request.get_records()).filter(lambda row: row.rcpt_dt and start_dt <= row.rcpt_dt < end_dt and row.rcpt_ord_tp_nm in types)

	if kind == 'NUT':
		drug_lst = drug_lst.filter(lambda row: row.get('효능코드(보건복지부)') in ['325'] or row.drug_nm and '알부민' in row.drug_nm)
	elif kind == 'INJ':
		drug_lst = drug_lst
	else:
		drug_lst = drug_lst.filter(lambda row: row.get('단일포장구분') in ['S', 'P'])

	ord_lst = ord_lst.set_number_type(ord_qty=0.0, ord_frq=0, ord_day=0)
	ord_lst = ord_lst.join(drug_lst, left_on='ord_cd', right_on='약품코드')
	ord_lst = ord_lst.add_columns(once_amt=lambda row: round(row.ord_qty / row.ord_frq, 2), total_amt=lambda row: row.ord_qty * row.ord_day, ward_=lambda row: row.ward[:2])
	ord_lst.set_index('ord_seq', 'rcpt_seq', 'ord_exec_seq','rcpt_ord_seq', index_name='pk')

	grp_by_drug_nm = ord_lst.groupby('drug_nm', ord_qty=sum, drug_nm=len, total_amt=sum,
		renames={'drug_nm': 'drug_nm_count', 'total_amt': 'total_amt_sum', 'ord_qty': 'ord_qty_sum'},
		extra_columns = ['ord_cd', 'ord_unit_nm', '단일포장구분', '효능코드(보건복지부)'],
		set_name = 'order_set'
	).orderby('-단일포장구분', 'drug_nm')

	grp_by_ward = ord_lst.groupby('ward_', ord_qty=sum, total_amt=sum, drug_nm=len,
		renames={'ord_qty': 'ord_qty_sum', 'total_amt': 'total_amt_sum', 'drug_nm': 'drug_nm_count'}, 
		set_name = 'order_set'
	).orderby('ward_', 'drug_nm')

	live_order_list = ord_lst.filter(lambda row: row.dc_gb == 'N' and row.ret_yn == 'N')
	dc_order_list = ord_lst.filter(lambda row: row.dc_gb == 'Y')
	not_dc_order_list = ord_lst.filter(lambda row: row.dc_gb == 'N')
	ret_order_list = ord_lst.filter(lambda row: row.ret_yn == 'Y')
	only_dc = ord_lst.filter(lambda row: row.dc_gb == 'Y' and row.ret_yn == 'N')
	only_ret = ord_lst.filter(lambda row: row.dc_gb != 'Y' and row.ret_yn == 'Y')
	grp_dc_by_ward = dc_order_list.groupby('ward_', ord_qty=sum, total_amt=sum, drug_nm=len,
		renames={'ord_qty': 'ord_qty_sum', 'total_amt': 'total_amt_sum', 'drug_nm': 'drug_nm_count'}, 
		set_name='order_set'
	).orderby('ward_', 'drug_nm')
	grp_ret_by_ward = ret_order_list.groupby('ward_', ord_qty=sum, total_amt=sum, drug_nm=len,
		renames={'ord_qty': 'ord_qty_sum', 'total_amt': 'total_amt_sum', 'drug_nm': 'drug_nm_count'}, 
		set_name='order_set'
	).orderby('ward_', 'drug_nm')

	nt = namedtuple('OrderCollections', 'order_list live_order_list dc_order_list not_dc_order_list ret_order_list only_dc only_ret grp_by_drug_nm grp_dc_by_ward grp_ret_by_ward kind')

	context = nt(
		order_list = ord_lst,
		live_order_list = live_order_list, 
		dc_order_list = dc_order_list,
		not_dc_order_list = not_dc_order_list, 
		ret_order_list = ret_order_list, 
		only_dc = only_dc,
		only_ret = only_ret,
		grp_by_drug_nm = grp_by_drug_nm, 
		grp_dc_by_ward = grp_dc_by_ward,
		grp_ret_by_ward = grp_ret_by_ward, 
		kind = kind
	)
	return context



ret = get_orderset(types=['정기', '추가', '응급', '퇴원'],
	# wards=['51', '52', '61', '71', '81', '92', 'IC'], 
	# start_date='2017-09-18', end_date='2017-09-21',
	# start_dt='2016-09-18 00:00:00', end_dt='2017-09-21 00:00:00', 
	wards=['51', '52', '61'], 
	start_date='2017-09-20', end_date='2017-09-20',
	start_dt='2016-09-19 00:00:00', end_dt='2017-09-20 00:00:00', 
	kind='NUT',
	# test=False
)


pprint(ret.order_list)
print(len(ret.order_list.column_values('pk')))
print(len(ret.order_list.unique('pk')))


