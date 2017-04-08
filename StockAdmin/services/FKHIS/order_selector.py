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

def get_label_object(kinds, wards, ord_start_date, ord_end_date, start_dt, end_dt):
	drug_db_recs = read_excel(DRUG_DB_PATH, drop_if= lambda row: row['단일포장구분'] not in ['S', 'P'])
	pk_set = drug_db_recs.unique('약품코드')
	odr = OrderSelectApiRequest(ord_start_date, ord_end_date, wards)
	print('wards', wards)
	odr.api_calls()
	records = odr.get_records()
	ord_recs = RecordParser(records = records, drop_if = lambda row: row.get('ord_cd') not in pk_set or row.get('rcpt_dt', "") == "" or row.get('rcpt_ord_tp_nm') != '정기')
	ord_recs.format([('ord_qty', 0.0)])
	ord_recs.vlookup(drug_db_recs, 'ord_cd', '약품코드', [('단일포장구분', 'S')])

	ord_recs.select('*', where=lambda row: start_dt <= row['rcpt_dt'] < end_dt)

	f, l = ord_recs.min('rcpt_dt'), ord_recs.max('rcpt_dt')
	ord_recs.group_by(columns=['단일포장구분','drug_nm'], aggset=[('ord_qty', sum, 'ord_qty_sum')], selects=['단일포장구분','ord_cd', 'drug_nm', 'ord_qty_sum', 'ord_unit_nm'])
	ord_recs.add_column([('rcpt_dt_min', lambda x: f), ('rcpt_dt_max', lambda x:l)])
	ord_recs.value_map([('단일포장구분', {'S': '작은라벨', 'P': '큰라벨'}, '')])
	return ord_recs.records


# path  = 'C:\\Users\\user\\Desktop\\집계표.xlsx'
# ret = get_label_object(['P', 'S'], ['51', '52', '61', '71', '81', '92', 'IC'], '2017-04-09','2017-04-10', '2017-04-08 00:00:00', '2017-04-08 23:23:00')
# ret.to_excel(path)
# os.startfile(path)

