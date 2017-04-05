import re, os
from socket import *
from collections import OrderedDict
from datetime import date

from bs4 import BeautifulSoup
try:
	from .ExcelParser import ExcelParser
	from .db import *
	from .settings import *
	from .recordlib import RecordParser
except:
	from ExcelParser import ExcelParser
	from db import *
	from settings import *
	from recordlib import RecordParser


def optstock_query(date_str, query_path):
	date_str = date_str.replace('-','')
	content_pat = re.compile(b'<NewDataSet>.+<\/NewDataSet>')
	with open(query_path, 'rb') as fp:
		data = fp.read()

	date = date_str.encode()
	pat = re.compile(b'\d{8}')
	data = pat.sub(date, data)

	cs = socket(AF_INET, SOCK_STREAM)
	cs.settimeout(REQ_TIMEOUT)
	cs.connect((SERVER, PORT))
	cs.send(data)
	response = b''

	while True:
		response += cs.recv(1024)
		if response[-1] == 11:
			cs.close()
			break
	return content_pat.findall(response)[1]
	

def get_std_name(record_row):
	std_drug = drugDB.get(record_row['drug_cd'])
	return std_drug['name'] if std_drug else  record_row['drug_nm']

def code_with_count(row):
	name = row['drug_nm']
	code = row['drug_cd']
	dup_codes = get_dup_codes(name)
	count = len(dup_codes)
	if count > 1:
		return "{}외 {}개".format(dup_codes[0], count-1)
	else:
		return code

def selective_int(row, column):
	before = row[column]
	after = 0
	try:
		after = int(row[column])
	except:
		return val
	else:
		return 

def parse_opstock_content(content):
	soup = BeautifulSoup(content, 'html.parser')
	recs = RecordParser(
		records = [OrderedDict((child.name, child.text) for child in table.children) for table in soup.find_all('table1')],
		drop_if = lambda row: row['drug_cd'] in EXCEPT_CODES
	)
	recs.format([('stock_qty', 0.0)])
	recs.update([('drug_nm', get_std_name), ('drug_cd', code_with_count)])
	recs.group_by(
		columns = ['drug_nm'], 
		aggset = [('stock_qty', sum, 'stock')], 
		selects = ['drug_cd', 'drug_nm', 'stock', 'stock_unit']
	)
	recs.update([('stock', lambda row: row['stock'] if int(row['stock'])!=row['stock'] else int(row['stock']) )])
	return recs.records




def get_opstock_object_list(date, psy=False, narc=False):

	psy_records, narc_records = [], []
	
	if narc:
		narc_response = optstock_query(date, os.path.join(BASE_DIR, 'requests/NarcStock.req'))
		narc_records = parse_opstock_content(narc_response)

	if psy:
		psy_response = optstock_query(date, os.path.join(BASE_DIR, 'requests/PsyStock.req'))
		psy_records = parse_opstock_content(psy_response)

	return narc_records + psy_records


def get_opstock_object_list_test(date, psy=False, narc=False):

	psy_records, narc_records = [], []
	
	if narc:
		with open(os.path.join(BASE_DIR, 'response_samples/NarcStock.sample.rsp'), 'rb') as fp:
			data = fp.read()
			content_pat = re.compile(b'<NewDataSet>.+<\/NewDataSet>')
			narc_response = content_pat.findall(data)[1]
		narc_records = parse_opstock_content(narc_response)


	if psy:
		with open(os.path.join(BASE_DIR, 'response_samples/PsyStock.sample.rsp'), 'rb') as fp:
			data = fp.read()
			content_pat = re.compile(b'<NewDataSet>.+<\/NewDataSet>')
			psy_response = content_pat.findall(data)[1]
		psy_records = parse_opstock_content(psy_response)

	return narc_records + psy_records



# with open(os.path.join(BASE_DIR, 'response_samples/OpStock.sample.rsp'), 'rb') as fp:
# 	content = fp.read()
# 	content_pat = re.compile(b'<NewDataSet>.+<\/NewDataSet>')
# 	contents = content_pat.findall(content)


# ret = parse_opstock_content(contents[1])
# ret = get_opstock_object_list('', narc=True)

# for r in ret:
# 	print(r)


# narc_response = optstock_query(date, os.path.join(BASE_DIR, 'requests/NarcStock.req'))
# print(narc_response)