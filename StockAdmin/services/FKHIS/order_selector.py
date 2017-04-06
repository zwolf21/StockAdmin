import os

try:
	from .recordlib import RecordParser, read_excel
	from .api_requests import *
except:
	from recordlib import RecordParser, read_excel
	from api_requests import *



path = 'C:\\Users\\HS\\Desktop\\처방조회종합.xlsx'


def get_label_objet_test(kinds, wards, date_str, start_time, end_time):
	drug_db_recs = read_excel(DRUG_DB_PATH, drop_if= lambda row: row['단일포장구분'] not in ['S', 'P'])
	pk_set = drug_db_recs.unique('약품코드')
	odr = OrderSelectApiRequest( '', [])
	odr.set_test_response('response_samples/ordSelect51.sample.rsp')
	ord_recs = RecordParser(records = odr.get_records(), drop_if = lambda row: row.get('ord_cd') not in pk_set or row.get('rcpt_dt', "") == "" or row.get('rcpt_ord_tp_nm') != '정기')
	ord_recs.format([('ord_qty', 0.0)])
	ord_recs.vlookup(drug_db_recs, 'ord_cd', '약품코드', [('단일포장구분', 'S')])
	f, l = ord_recs.min('rcpt_dt'), ord_recs.max('rcpt_dt')
	ord_recs.group_by(columns=['단일포장구분','drug_nm'], aggset=[('ord_qty', sum, 'ord_qty_sum')], selects=['단일포장구분','ord_cd', 'drug_nm', 'ord_qty_sum', 'ord_unit_nm'])
	ord_recs.add_column([('rcpt_dt_min', lambda x: f), ('rcpt_dt_max', lambda x:l)])
	ord_recs.value_map([('단일포장구분', {'S': '작은라벨', 'P': '큰라벨'}, '')])
	return ord_recs.records

def get_label_object(kinds, wards, date_str, start_time, end_time):
	drug_db_recs = read_excel(DRUG_DB_PATH, drop_if= lambda row: row['단일포장구분'] not in ['S', 'P'])
	pk_set = drug_db_recs.unique('약품코드')
	odr = OrderSelectApiRequest(date_str, wards)
	odr.api_calls()
	ord_recs = RecordParser(records = odr.get_records(), drop_if = lambda row: row.get('ord_cd') not in pk_set or row.get('rcpt_dt', "") == "" or row.get('rcpt_ord_tp_nm') != '정기')
	ord_recs.format([('ord_qty', 0.0)])
	ord_recs.vlookup(drug_db_recs, 'ord_cd', '약품코드', [('단일포장구분', 'S')])
	f, l = ord_recs.min('rcpt_dt'), ord_recs.max('rcpt_dt')
	ord_recs.group_by(columns=['단일포장구분','drug_nm'], aggset=[('ord_qty', sum, 'ord_qty_sum')], selects=['단일포장구분','ord_cd', 'drug_nm', 'ord_qty_sum', 'ord_unit_nm'])
	ord_recs.value_map([('단일포장구분', {'S': '작은라벨', 'P': '큰라벨'}, '')])
	return {'object_list': ord_recs.records, 'first_rcpt_dt': f, 'last_rcpt_dt': l}


# for row in get_label_objet_test(['P', 'S'], ['71'], '2017-05-03', '00:00:00', '23:59:59')['object_list']:
# 	print(row)
