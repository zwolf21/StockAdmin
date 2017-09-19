import os
# from recordlib import RecordParser, read_excel
import listorm
from recordlib import RecordParser, read_excel
try:
	from .api_requests import *
except:
	from api_requests import *

try:
	from dbconn import *
except:
	from .dbconn import *


# path = 'C:\\Users\\HS\\Desktop\\처방조회종합.xlsx'


def get_records(types, wards, ord_start_date, ord_end_date, start_dt, end_dt, test):
	# print(ord_start_date, ord_end_date, wards)
	ord_request = OrderSelectApiRequest(ord_start_date, ord_end_date, wards)
	if test:
		ord_request.set_test_response('response_samples/ordSelect51.sample.rsp')
		drug_lst = listorm.read_excel(DRUG_DB_PATH)
		ord_lst = listorm.Listorm(ord_request.get_records())
	else:
		ord_request.api_calls()
		ord_lst = listorm.Listorm(ord_request.get_records())
		try:
			drug_lst = get_label_list()
		except:
			drug_lst = read_excel(DRUG_DB_PATH)
		else:
			ord_lst = ord_lst.filter(where=lambda row:row.rcpt_dt and start_dt <= row['rcpt_dt'] < end_dt)
	
	drug_lst = drug_lst.select('약품코드', '단일포장구분', '효능코드(보건복지부)')
	pk_set = drug_lst.unique('약품코드')

	ord_lst = ord_lst.filter(where = lambda row: row.get('ord_cd') in pk_set and row.get('rcpt_dt') and row.get('rcpt_ord_tp_nm') in types)
	ord_lst = ord_lst.join(drug_lst, left_on='ord_cd', right_on='약품코드')
	ord_lst = ord_lst.set_number_type(ord_qty=0.0, ord_frq=0, ord_day=0)
	rcpt_dt_list = ord_lst.column_values('rcpt_dt')
	if rcpt_dt_list:
		f, l = min(rcpt_dt_list), max(rcpt_dt_list)
		ord_lst = ord_lst.add_columns(rcpt_dt_min=lambda x: f, rcpt_dt_max=lambda x: l)
	return ord_lst



def get_label_records(kinds, types, wards, ord_start_date, ord_end_date, start_dt, end_dt, test=False):
	ord_lst= get_records(types, wards, ord_start_date, ord_end_date, start_dt, end_dt, test).filter(lambda row: row['단일포장구분'] in kinds)
	ord_lst_length = len(ord_lst)
	ord_lst = ord_lst.add_columns(once_amt=lambda row: round(row['ord_qty'] / row['ord_frq'], 2), total_amt=lambda row: row['ord_qty'] * row['ord_day'])
	ord_lst = ord_lst.groupby('단일포장구분', 'drug_nm', ord_qty=sum, drug_nm=len, total_amt=sum, 
		renames={'drug_nm': 'drug_nm_count', 'total_amt': 'total_amt_sum', 'ord_qty': 'ord_qty_sum'},
		extra_columns = ['ord_cd', 'ord_unit_nm'],
		set_name = 'order_set'
	)
	ord_lst = ord_lst.map(단일포장구분= lambda x: {'S': '작은라벨', 'P': '큰라벨'}.get(x,x))
	return {'grp_by_drug_nm':ord_lst.orderby('-단일포장구분', 'drug_nm'), 'count': ord_lst_length}
	
# ret = get_label_records(['P', 'S'], ['정기'], ['51'], '2017-09-18','2017-09-18', '2017-09-17 00:00:00', '2017-09-17 23:23:00', test=False)

# for row in ret:
# 	print(row)
	# break

def get_nutfluid_records(types, wards, ord_start_date, ord_end_date, start_dt, end_dt, exclude_names=None, test=False):
	ord_lst = get_records(types, wards, ord_start_date, ord_end_date, start_dt, end_dt, test).filter(lambda row: row['효능코드(보건복지부)'] in ['325'] or '알부민' in row['drug_nm'])
	if exclude_names:
		ord_lst = ord_lst.search_splited(exclude_names or [], ['drug_nm'], exclude=True)
	ord_lst_length = len(ord_lst)
	ord_lst = ord_lst.add_columns(
			once_amt=lambda row: round(row['ord_qty'] / row['ord_frq'], 2),
			total_amt=lambda row: row['ord_qty'] * row['ord_day'],
			ward_ = lambda row: row['ward'][:2]
		)
	
	grp_by_drug_nm = ord_lst.groupby('drug_nm', ord_qty=sum, total_amt=sum, drug_nm=len,
		renames={'ord_qty': 'ord_qty_sum', 'total_amt': 'total_amt_sum', 'drug_nm': 'drug_nm_count'}, 
		extra_columns=['ord_cd', 'ord_unit_nm',],
		set_name = 'order_set'
	).orderby('drug_nm')

	grp_by_ward = ord_lst.groupby('ward_', ord_qty=sum, total_amt=sum, drug_nm=len,
		renames={'ord_qty': 'ord_qty_sum', 'total_amt': 'total_amt_sum', 'drug_nm': 'drug_nm_count'}, 
		extra_columns=['ord_cd', 'ord_unit_nm',],
		set_name = 'order_set'
	).orderby('ward_', 'drug_nm')
	return {'grp_by_drug_nm': grp_by_drug_nm, 'grp_by_ward': grp_by_ward, 'count': ord_lst_length}

# ret = get_nutfluid_records(['정기'], ['51', '52', '61', '71', '81', '92', 'IC'], '2017-04-09','2017-04-10', '2017-04-08 00:00:00', '2017-04-08 23:23:00', test=True)

# for row in ret['grp_by_ward']:
# 	print(row)



def get_label_object_test(kinds, types, wards, ord_start_date, ord_end_date, start_dt, end_dt):
	drug_db_recs = read_excel(DRUG_DB_PATH, drop_if= lambda row: row['단일포장구분'] not in kinds)
	pk_set = drug_db_recs.unique('약품코드')
	odr = OrderSelectApiRequest(ord_start_date, ord_end_date, wards)
	odr.set_test_response('response_samples/ordSelect51.sample.rsp')
	ord_recs = RecordParser(records = odr.get_records(), drop_if = lambda row: row.get('ord_cd') not in pk_set or row.get('rcpt_dt', "") == "" or row.get('rcpt_ord_tp_nm') not in types)
	ord_recs.format([('ord_qty', 0.0)])
	ord_recs.vlookup(drug_db_recs, 'ord_cd', '약품코드', [('단일포장구분', 'S')])
	ord_recs.format([('ord_qty', 0.0), ('ord_frq', 0), ('ord_day', 0)])
	ord_recs.add_column([
		('once_amt', lambda row: round(row['ord_qty'] / row['ord_frq'], 2)),
		('total_amt', lambda row: row['ord_qty'] * row['ord_day'])
	])

	# ord_recs.select('*', where=lambda row: start_dt <= row['rcpt_dt'] < end_dt)
	detail = ord_recs.records.copy()
	f, l = ord_recs.min('rcpt_dt'), ord_recs.max('rcpt_dt')
	ord_recs.group_by(
		columns=['단일포장구분','drug_nm'], 
		aggset=[('ord_qty', sum, 'ord_qty_sum'), ('drug_nm', len, 'drug_nm_count'), ('total_amt', sum, 'total_amt_sum')], 
		selects=['단일포장구분','ord_cd', 'drug_nm', 'ord_qty_sum', 'ord_unit_nm', 'drug_nm_count', 'total_amt_sum']
	)
	ord_recs.add_column([('rcpt_dt_min', lambda x: f), ('rcpt_dt_max', lambda x:l)])
	ord_recs.value_map([('단일포장구분', {'S': '작은라벨', 'P': '큰라벨'}, '')])
	return ord_recs.records, detail

def get_label_object(kinds, types, wards, ord_start_date, ord_end_date, start_dt, end_dt):
	try:
		drug_db_recs = get_label_list()
		drug_db_recs = RecordParser(drug_db_recs, drop_if= lambda row: row['단일포장구분'] not in ['S', 'P']) 
	except:
		drug_db_recs = read_excel(DRUG_DB_PATH, drop_if= lambda row: row['단일포장구분'] not in ['S', 'P'])

	pk_set = drug_db_recs.unique('약품코드')
	odr = OrderSelectApiRequest(ord_start_date, ord_end_date, wards)
	odr.api_calls()
	records = odr.get_records()
	ord_recs = RecordParser(records = records, drop_if = lambda row: row.get('ord_cd') not in pk_set or row.get('rcpt_dt', "") == "" or row.get('rcpt_ord_tp_nm') not in types)

	ord_recs.vlookup(drug_db_recs, 'ord_cd', '약품코드', [('단일포장구분', 'S')])
	ord_recs.format([('ord_qty', 0.0), ('ord_frq', 0), ('ord_day', 0)])

	ord_recs.select('*', where=lambda row: start_dt <= row['rcpt_dt'] < end_dt)
	ord_recs.add_column([
		('once_amt', lambda row: round(row['ord_qty'] / row['ord_frq'], 2)),
		('total_amt', lambda row: row['ord_qty'] * row['ord_day'])
	])
	detail = ord_recs.records.copy()
	f, l = ord_recs.min('rcpt_dt'), ord_recs.max('rcpt_dt')

	ord_recs.group_by(
		columns=['단일포장구분','drug_nm'],
		aggset=[('ord_qty', sum, 'ord_qty_sum'), ('drug_nm', len, 'drug_nm_count'), ('total_amt', sum, 'total_amt_sum')],
		selects=['단일포장구분','ord_cd', 'drug_nm', 'ord_qty_sum', 'ord_unit_nm', 'drug_nm_count', 'total_amt_sum']
	)
	ord_recs.add_column([('rcpt_dt_min', lambda x: f), ('rcpt_dt_max', lambda x:l)])
	ord_recs.value_map([('단일포장구분', {'S': '작은라벨', 'P': '큰라벨'}, '')])
	return ord_recs.records, detail

def get_inj_object(types, wards, ord_start_date, ord_end_date, start_dt, end_dt, test=False):
	drug_db_recs = read_excel(DRUG_DB_PATH, 
		drop_if = lambda row: row['투여경로'] != '3' or row['효능코드명'] in ['혈액대용제', '당류제'] or row['항암제구분'] == '1' or row['약품법적구분'] in ['1','2'])
	pk_set = drug_db_recs.unique('약품코드')
	odr = OrderSelectApiRequest(ord_start_date, ord_end_date, wards)

	if test:
		odr.set_test_response('response_samples/ordSelect51.sample.rsp')
	else:
		odr.api_calls()

	ord_recs = RecordParser(
		records = odr.get_records(), 
		drop_if = lambda row: row.get('ord_cd') not in pk_set or row.get('rcpt_dt', "") == "" or row.get('rcpt_ord_tp_nm') not in types
	)
	ord_recs.format([('ord_qty', 0.0), ('ord_frq', 0), ('ord_day', 0)])
	if not test:
		ord_recs.select('*', where=lambda row: start_dt <= row['rcpt_dt'] < end_dt)

	ord_recs.add_column([
		('once_amt', lambda row: round(row['ord_qty'] / row['ord_frq'], 2)),
		('total_amt', lambda row: row['ord_qty'] * row['ord_day'])
	])

	detail = ord_recs.records.copy()
	f, l = ord_recs.min('rcpt_dt'), ord_recs.max('rcpt_dt')
	ord_recs.group_by(
		columns = ['ord_cd'],
		aggset = [('ord_qty', sum, 'ord_qty_sum'), ('drug_nm', len, 'drug_nm_count'), ('total_amt', sum, 'total_amt_sum')],
		selects = ['ord_cd', 'drug_nm', 'ord_qty_sum', 'ord_unit_nm', 'drug_nm_count', 'total_amt_sum']
	)
	ord_recs.add_column([('rcpt_dt_min', lambda x: f), ('rcpt_dt_max', lambda x:l)])
	return ord_recs.records, detail





def get_chemo_label_object_test(wards, ord_start_date, ord_end_date, start_dt, end_dt):
	drugs_recs = read_excel(DRUG_DB_PATH)
	odr = OrderSelectApiRequest(ord_start_date, ord_end_date, wards)
	odr.set_test_response('response_samples/ordSelect51.sample.rsp')
	records = odr.get_records()
	ord_recs = RecordParser(records=records, drop_if = lambda row: row.get('rcpt_dt', "") == "")

	# if real
	# ord_recs.select('*', where= lambda row: start_dt <= row['rcpt_dt'] < end_dt)

	ord_recs.vlookup(drugs_recs, 'ord_cd', '약품코드', [('항암제구분', '0'), ('함량1', 0.0), ('함량단위1', ''), ('함량2', 0.0), ('함량단위2', '')])
	ord_recs.format([('ord_qty', 0.0), ('함량1', 0.0), ('함량2', 0.0)])
	ord_recs.add_column([('amt_vol', lambda row: row['ord_qty'] * row['함량1']), ('amt_wgt', lambda row: row['ord_qty'] * row['함량2'])])

	chemo_index = ord_recs.select(['ord_ymd', 'rcpt_seq', 'medi_no', 'ord_no'],
		where = lambda row: row['항암제구분'] == '1',
		inplace = False
	).to2darry(headers=False)
	ord_recs.select('*', where=lambda r:[r['ord_ymd'], r['rcpt_seq'], r['medi_no'], r['ord_no']] in chemo_index)
	detail = ord_recs.records.copy()
	f, l = ord_recs.min('rcpt_dt'), ord_recs.max('rcpt_dt')
	ord_recs.group_by(
		columns=['ord_ymd', 'rcpt_seq', 'medi_no', 'ord_cd'], 
		aggset=[('amt_vol', sum, 'amt_vol_sum'), ('amt_wgt', sum, 'amt_wgt_sum'), ('ord_qty', sum, 'ord_qty_sum'), ('drug_nm', len, 'drug_nm_count')],
		selects=['ord_cd', 'drug_nm', 'ord_unit_nm', 'amt_vol_sum','amt_wgt_sum', 'ord_qty_sum', '함량단위1', '함량단위2', 'drug_nm_count'],
		inplace=True
	)
	ord_recs.add_column([('rcpt_dt_min', lambda x: f), ('rcpt_dt_max', lambda x:l)])
	return ord_recs.records, detail

def get_chemo_label_object(wards, ord_start_date, ord_end_date, start_dt, end_dt):
	drugs_recs = read_excel(DRUG_DB_PATH)
	odr = OrderSelectApiRequest(ord_start_date, ord_end_date, wards)
	odr.api_calls()
	records = odr.get_records()
	ord_recs = RecordParser(records=records, drop_if = lambda row: row.get('rcpt_dt', "") == "")

	# if real
	ord_recs.select('*', where= lambda row: start_dt <= row['rcpt_dt'] < end_dt)

	ord_recs.vlookup(drugs_recs, 'ord_cd', '약품코드', [('항암제구분', '0'), ('함량1', 0.0), ('함량단위1', ''), ('함량2', 0.0), ('함량단위2', '')])
	ord_recs.format([('ord_qty', 0.0), ('함량1', 0.0), ('함량2', 0.0)])
	ord_recs.add_column([('amt_vol', lambda row: row['ord_qty'] * row['함량1']), ('amt_wgt', lambda row: row['ord_qty'] * row['함량2'])])

	chemo_index = ord_recs.select(['ord_ymd', 'rcpt_seq', 'medi_no', 'ord_no'],
		where = lambda row: row['항암제구분'] == '1',
		inplace = False
	).to2darry(headers=False)
	ord_recs.select('*', where=lambda r:[r['ord_ymd'], r['rcpt_seq'], r['medi_no'], r['ord_no']] in chemo_index)
	detail = ord_recs.records.copy()
	f, l = ord_recs.min('rcpt_dt'), ord_recs.max('rcpt_dt')
	ord_recs.group_by(
		columns=['ord_ymd', 'rcpt_seq', 'medi_no', 'ord_cd'], 
		aggset=[('amt_vol', sum, 'amt_vol_sum'), ('amt_wgt', sum, 'amt_wgt_sum'), ('ord_qty', sum, 'ord_qty_sum'), ('drug_nm', len, 'drug_nm_count')],
		selects=['ord_cd', 'drug_nm', 'ord_unit_nm', 'amt_vol_sum','amt_wgt_sum', 'ord_qty_sum','함량단위1', '함량단위2', 'drug_nm_count'],
		inplace=True
	)
	ord_recs.add_column([('rcpt_dt_min', lambda x: f), ('rcpt_dt_max', lambda x:l)])
	return ord_recs.records, detail

# path  = 'C:\\Users\\user\\Desktop\\집계표.xlsx'
# ret = get_label_object(['P', 'S'], ['51', '52', '61', '71', '81', '92', 'IC'], '2017-04-09','2017-04-10', '2017-04-08 00:00:00', '2017-04-08 23:23:00')
# ret.to_excel(path)
# os.startfile(path)

# get_label_object_test(['P', 'S'], ['51', '52', '61', '71', '81', '92', 'IC'], '2017-04-09','2017-04-10', '2017-04-08 00:00:00', '2017-04-08 23:23:00')