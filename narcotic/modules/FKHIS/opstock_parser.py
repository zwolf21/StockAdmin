import re, os
from socket import *
from bs4 import BeautifulSoup

from .ExcelParser import ExcelParser
from .db import *

BASE_DIR = os.path.dirname(__file__)


host = '192.168.8.8'
port = 7501

def get_opstock(date_str, req_file):
	with open(os.path.join(BASE_DIR, req_file), 'rb') as fp:
		data = fp.read()
	date_str = date_str.replace('-', '')
	date = date_str.encode()
	pat = re.compile(b'\d{8}')
	data = pat.sub(date, data)

	cs = socket(AF_INET, SOCK_STREAM)
	cs.connect((host, port))
	cs.send(data)

	response = b''

	while True:
		response += cs.recv(1024)
		if response[-1] == 11:
			cs.close()
			break
	return response

# to test



def opstock_contents_parser(contents):
	content_pat = re.compile(b'<NewDataSet>.+<\/NewDataSet>')
	content = content_pat.findall(contents)
	soup = BeautifulSoup(content[1], 'html.parser')
	ret = []
	for table in soup.newdataset.find_all('table1'):

		record = {
			'약품코드': table.drug_cd.text if table.drug_cd else "",
			'약품명' : table.drug_nm.text if table.drug_nm else "",
			'규격단위' : table.stock_unit.text if table.stock_unit else "",
			'재고' : table.stock_qty.text if table.stock_qty else ""
		}
		ret.append(record)
	return ret

def get_std_name(record_row):
	std_drug = drugDB.get(record_row['약품코드'])
	if std_drug:
		return std_drug['name']
	return record_row['약품명'] 

def str_digit_sum(digit_list):
	nums = []
	for num in digit_list:
		try:
			flt = float(num)
		except:
			continue
		else:
			nums.append(flt)
	ret = sum(nums)
	return int(ret) if ret == int(ret) else ret

def code_with_count(row):
	name = row['재고약품명']
	code = row['약품코드']
	dup_codes = get_dup_codes(name)
	count = len(dup_codes)
	if count > 1:
		return "{}외 {}개".format(dup_codes[0], count-1)
	else:
		return code

def get_opstock_object_list(date, psy=False, narc=False):
	# response = get_opstock(date)

	'''test code'''
	
	''''''
	psy_raw, narc_raw = [], []

	if psy:
		psy_response = get_opstock(date, os.path.join(BASE_DIR, 'PsyStock.req'))
		psy_raw = opstock_contents_parser(psy_response)

	if narc:
		with open(os.path.join(BASE_DIR, 'NarcStock.rsp'), 'rb') as fp:
			narc_response = fp.read()
		# narc_response = get_opstock(date, os.path.join(BASE_DIR, 'NarcStock.req'))
		narc_raw = opstock_contents_parser(narc_response)

	raw_data = psy_raw + narc_raw

	if raw_data:
		exl = ExcelParser(records =raw_data, 재고약품명="")
		exl.update(재고약품명 = get_std_name)
		exl.update(약품코드=code_with_count).order_by('재고약품명')
		return exl.group_by('재고약품명', 재고=str_digit_sum)




# with open('OpStock.sample', 'rb') as fp:
# 	response = fp.read()

# rec = opstock_contents_parser(response)

# objlist=get_opstock_object_list(rec)
# print(objlist)





