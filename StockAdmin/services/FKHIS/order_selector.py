import os
from recordlib import RecordParser, read_excel
try:
	from .api_requests import *
except:
	from api_requests import *



# path = 'C:\\Users\\HS\\Desktop\\처방조회종합.xlsx'


def get_label_object_test(kinds, types, wards, ord_start_date, ord_end_date, start_dt, end_dt):
	drug_db_recs = read_excel(DRUG_DB_PATH, drop_if= lambda row: row['단일포장구분'] not in kinds)
	pk_set = drug_db_recs.unique('약품코드')
	odr = OrderSelectApiRequest(ord_start_date, ord_end_date, wards)
	odr.set_test_response('response_samples/ordSelect51.sample.rsp')
	ord_recs = RecordParser(records = odr.get_records(), drop_if = lambda row: row.get('ord_cd') not in pk_set or row.get('rcpt_dt', "") == "" or row.get('rcpt_ord_tp_nm') not in types)
	ord_recs.format([('ord_qty', 0.0)])
	ord_recs.vlookup(drug_db_recs, 'ord_cd', '약품코드', [('단일포장구분', 'S')])

	# ord_recs.select('*', where=lambda row: start_dt <= row['rcpt_dt'] < end_dt)
	detail = ord_recs.records.copy()
	f, l = ord_recs.min('rcpt_dt'), ord_recs.max('rcpt_dt')
	ord_recs.group_by(
		columns=['단일포장구분','drug_nm'], 
		aggset=[('ord_qty', sum, 'ord_qty_sum'), ('drug_nm', len, 'drug_nm_count')], 
		selects=['단일포장구분','ord_cd', 'drug_nm', 'ord_qty_sum', 'ord_unit_nm', 'drug_nm_count']
	)
	ord_recs.add_column([('rcpt_dt_min', lambda x: f), ('rcpt_dt_max', lambda x:l)])
	ord_recs.value_map([('단일포장구분', {'S': '작은라벨', 'P': '큰라벨'}, '')])
	return ord_recs.records, detail

def get_label_object(kinds, types, wards, ord_start_date, ord_end_date, start_dt, end_dt):
	drug_db_recs = read_excel(DRUG_DB_PATH, drop_if= lambda row: row['단일포장구분'] not in ['S', 'P'])
	pk_set = drug_db_recs.unique('약품코드')
	odr = OrderSelectApiRequest(ord_start_date, ord_end_date, wards)
	odr.api_calls()
	records = odr.get_records()
	ord_recs = RecordParser(records = records, drop_if = lambda row: row.get('ord_cd') not in pk_set or row.get('rcpt_dt', "") == "" or row.get('rcpt_ord_tp_nm') not in types)

	ord_recs.vlookup(drug_db_recs, 'ord_cd', '약품코드', [('단일포장구분', 'S')])
	ord_recs.format([('ord_qty', 0.0)])

	ord_recs.select('*', where=lambda row: start_dt <= row['rcpt_dt'] < end_dt)
	detail = ord_recs.records.copy()
	f, l = ord_recs.min('rcpt_dt'), ord_recs.max('rcpt_dt')

	ord_recs.group_by(
		columns=['단일포장구분','drug_nm'],
		aggset=[('ord_qty', sum, 'ord_qty_sum'), ('drug_nm', len, 'drug_nm_count')],
		selects=['단일포장구분','ord_cd', 'drug_nm', 'ord_qty_sum', 'ord_unit_nm', 'drug_nm_count']
	)
	ord_recs.add_column([('rcpt_dt_min', lambda x: f), ('rcpt_dt_max', lambda x:l)])
	ord_recs.value_map([('단일포장구분', {'S': '작은라벨', 'P': '큰라벨'}, '')])
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
		inplace=False
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
		inplace=False
	)
	ord_recs.add_column([('rcpt_dt_min', lambda x: f), ('rcpt_dt_max', lambda x:l)])
	return ord_recs.records, detail

# path  = 'C:\\Users\\user\\Desktop\\집계표.xlsx'
# ret = get_label_object(['P', 'S'], ['51', '52', '61', '71', '81', '92', 'IC'], '2017-04-09','2017-04-10', '2017-04-08 00:00:00', '2017-04-08 23:23:00')
# ret.to_excel(path)
# os.startfile(path)

# get_label_object_test(['P', 'S'], ['51', '52', '61', '71', '81', '92', 'IC'], '2017-04-09','2017-04-10', '2017-04-08 00:00:00', '2017-04-08 23:23:00')