import xlrd, re, argparse, sys, os
from listorm import Listorm, read_excel

from StockAdmin.services.FKHIS.dbconn import get_all_list, get_all_suga

from utils.shortcuts import file_response

renames = {}


def is_excel(excel):
	fn, ext = os.path.splitext(excel)
	if ext in ['.xls', '.xlsx']:
		return True
	return False

def is_gosi_file(contents):
	scheme=['제품코드', '제품명', '상한금액']
	lst = get_tables_from_gosi(file_contents=contents, scheme=scheme)
	if lst and set(scheme) <= set(lst.column_orders):
		return True
	return False


def get_edi_code_from_gosi(xl_file=None, **kwargs):
	
	edis = Listorm()
	re_compile_edi = re.compile('[A-Z\d]\d{8}')
	wb = xlrd.open_workbook(xl_file) if xl_file else xlrd.open_workbook(**kwargs)
	for sheet_index in range(wb.nsheets):
		sheet = wb.sheet_by_index(sheet_index)
		
		for r in range(sheet.nrows):
			for cell in sheet.row(r):
				for edi in re_compile_edi.findall(str(cell.value)):
					edis.append({'시트이름': sheet.name, 'EDI코드':edi})
	return Listorm(edis)
			

def get_tables_from_gosi(scheme, xl_file=None, **kwargs):
	re_compile_edi = re.compile('[A-Z\d]\d{8}')
	wb = xlrd.open_workbook(xl_file) if xl_file else xlrd.open_workbook(**kwargs)
	
	records = []
	for nsheet in range(wb.nsheets):
		ws = wb.sheet_by_index(nsheet)
		sheet_name = ws.name
		
		columns = []
		for nrow in range(ws.nrows):
			row_values = [cell.value for cell in ws.row(nrow)]
			if not columns and set(scheme) <= set(row_values):
				columns = row_values
				continue
			row = dict(zip(columns, row_values))
			if not row:
				continue

			record = {k: row[k] for k in scheme if k in row and row[k]}
			record['시트명'] = sheet_name
			records.append(record)

	return Listorm(records)

# def retrieve_drug_info(**renames):
# 	conn = pymssql.connect(server='', database='', user='', password='')
# 	cursor = conn.cursor(as_dict=True)
# 	drug_table_qry = 'SELECT * FROM '
# 	cursor.execute(drug_table_qry)
# 	records = [row for row in cursor.fetchall()]
# 	lst = Listorm(record)
	return lst.rename(**renames)


def identify_excel(paths):
	if len(paths) != 2:
		return 
	drug_info_header_examples = {'약품코드', '약품명(영문)', '약품명(한글)'}
	drug_info_path = ''
	gosi_path = ''
	for path in paths:
		fn, ext = os.path.splitext(path)
		if ext in ('.xls', '.xlsx'):
			wb = xlrd.open_workbook(path)
			sht = wb.sheet_by_index(0)
			header = sht.row_values(0)
			if drug_info_header_examples <= set(header):
				drug_info_path = path
				paths.remove(path)
				break
	gosi_path = paths[0]

	if drug_info_path and gosi_path:
		return drug_info_path, gosi_path




def analize_excel(xl_drug_info=None, xl_gosi_table=None, filename=None):
	gosi_tbl = get_tables_from_gosi(xl_gosi_table, scheme=['제품코드', '제품명', '상한금액'])
	gosi_tbl.set_number_type(제품코드='')
	drug_info = read_excel(xl_drug_info) if xl_drug_info else get_all_list()
	drug_info.set_number_type(보험단가=0)
	suga_info = get_all_suga()
	join_result = drug_info.join(gosi_tbl, left_on='EDI코드', right_on='제품코드').join(suga_info, left_on='약품코드', right_on='수가코드')
	print(join_result)
	join_result.add_columns(상한초과=lambda row: row.보험단가 > row.상한금액)
	join_result = join_result.map(**{'원내/원외 처방구분': lambda key: {'1': '원외만', '2': '원내만', '3': '원외/원내'}.get(key, key)})
	return join_result.to_excel(selects=['시트명', '제품코드','제품명','수가코드','원내/원외 처방구분', '상한금액','보험단가', '일반단가', '상한초과', '수가시작일자', '수가종료일자','시작일자', '종료일자'])
	



	

