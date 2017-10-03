from collections import Iterable
from datetime import datetime
import sys, os
import pymssql
from listorm import Listorm, read_excel


from pprint import pprint
try:
	from .mapping import codes
except:
	from mapping import codes

server = '192.168.7.7'
user = 'sa'
# user = 'p8817'
password = 'egmainkf#$R'
# password = 'pjr31983198'
database = 'FKOCS'

MODULE_BASE = os.path.dirname(__file__)
DRUG_DB_PATH = os.path.join(MODULE_BASE, '약품정보.xls')

class FkocsAPI:

	def __init__(self, **kwargs):
		self.conn = pymssql.connect(**kwargs)
		self.cursor = self.conn.cursor(as_dict=True)

	def iter_tables(self, callback=None):
		qry_iter_tables = 'SELECT * FROM INFORMATION_SCHEMA.TABLES'
		self.cursor.execute(qry_iter_tables)
		for record in self.cursor.fetchall():
			table_name = record['TABLE_NAME']
			query = 'SELECT TOP 100 * FROM {}'.format(table_name)
			try:
				self.cursor.execute(query)
			except:
				return
			else:
				records = [row for row in self.cursor.fetchall()]
				try:
					callback(records, table_name)
				except:
					return

	def backup_druginfo(self, filename, columns, **renames):
		query = "SELECT * FROM SPB_DRUG_MST"
		self.cursor.execute(query)
		records = [row for row in self.cursor.fetchall()]
		if records:
			column = [row[0] for row in self.cursor.description]
			lst = Listorm(records)
			lst.rename(**renames)
			lst.to_excel(filename, selects=columns)

	def get_all_info(self, **renames):
		query = "SELECT * FROM SPB_DRUG_MST WHERE DUSE_YN='N'"
		self.cursor.execute(query)
		records = [row for row in self.cursor.fetchall()]
		# pprint(records)
		return Listorm(records).rename(**renames)

	def get_nutfluid_info(self, **renames):
		query = "SELECT * FROM SPB_DRUG_MST WHERE DUSE_YN='N' AND EFCY_CD='325' OR EFCY_CD='634'"
		self.cursor.execute(query)
		records = [row for row in self.cursor.fetchall()]
		return Listorm(records).rename(**renames)

	def get_inj_info(self, **renames):
		query = "SELECT * FROM SPB_DRUG_MST WHERE DUSE_YN='N' AND MED_PTH='3'"
		self.cursor.execute(query)
		records = [row for row in self.cursor.fetchall()]
		return Listorm(records).rename(**renames)
		
	def get_label_info(self, **renames):
		query = "SELECT * FROM SPB_DRUG_MST WHERE DUSE_YN='N' AND SNG_PACK_GB='S' OR SNG_PACK_GB='P'"
		self.cursor.execute(query)
		records = [row for row in self.cursor.fetchall()]
		return Listorm(records).rename(**renames)


	def _update_druginfo(self, code, column, value):
		query = "UPDATE SPB_DRUG_MST SET {}='{}' WHERE DRUG_CD='{}';".format(column, value, code)
		self.cursor.execute(query)
		self.conn.commit()

	def update_duse_yesno(self, code, duse_ymd=None, duse_why=None):
		'''코드 폐기시 폐기일자[사유] 지정, 미지정시 폐기취소로 동작
		'''
		self._update_druginfo(code=code, column='DUSE_YN', value='Y' if duse_ymd else 'N')
		if duse_ymd:
			self._update_druginfo(code=code, column='END_YMD', value=duse_ymd)
			if duse_why:
				self._update_druginfo(code=code, column='DUSE_RESN_CONT', value=duse_why)

	def update_component(self, code, component):
		'''성분명 지정 255자 까지 잘림
		'''
		component = component[:256]
		self._update_druginfo(code=code, column='INGRD_NM', value=component)

	def update_pro_yn(self, code, pro_yn):
		pro_yn = pro_yn.upper()
		if pro_yn in ['Y', 'N']:
			self._update_druginfo(code=code, column='SPLST_DRUG_YN', value=pro_yn)

	def update_name_kor(self, code, rename):
		self._update_druginfo(code=code, column='DRUG_NM_KOR', value=rename)

	def update_med_path(self, code, path_no):
		'''투여경로 수정 1: 내복약, 2: 외용약, 3: 주사약
		'''
		self._update_druginfo(code=code, column='MED_PTH', value=rename)	

	def update_fda_prg(self, code, grade):
		grade = grade.upper()
		if grade in ('A', 'B', 'C', 'D', 'X'):
			self._update_druginfo(code=code, column='FDA_DIV_PRGNC', value=grade)

	def update_efficacy_code(self, code, ncode):
		if isinstance(ncode, int) or ncode.isdigit():
			ncode = str(ncode)
			self._update_druginfo(code=code, column='EFCY_CD', value=ncode)

	def update_component_code(self, code, ccode):
		self._update_druginfo(code=code, column='INGRD_CD', value=str(ccode))

	def update_inout(self, code, inout):
		if isinstance(inout, int) or inout.isdigit():
			inout = str(inout)
			self._update_druginfo(code=code, column='HOSIO_ORD_GB', value=inout)

	def __del__(self):
		if self.conn:
			self.conn.close()

def record_to_excel(records, table_name):
	filename = "{}.xlsx".format(table_name)
	Listorm(records).to_excel(filename)


# lst = read_excel('원내약품정보상세.xlsx')
# fk = FkocsAPI(server=server, user=user, password=password, database=database, charset='utf8')
# fk.backup_druginfo('약품정보.xlsx', columns=columns, **codes)
# -- fk.cursor.execute("SELECT * FROM PIC_IPD_CALC_SLIP WHERE ORD_YMD='{}'".format('20170804'))
# fk.cursor.execute('SELECT * FROM SPB_DRUG_MST')
# records = [row for row in fk.cursor.fetchall()]
# Listorm(records).to_excel('오늘처방.xlsx')
# fk.update_efficacy_code('10DW10', 323)
# fk.backup_druginfo('backup.xlsx')

def drug_update(source_excel, base_excel, what):
	fk = FkocsAPI(server=server, user=user, password=password, database=database)
	source_lst = read_excel(source_excel)
	base_lst = read_excel(base_excel).select('약품코드', 'EDI코드', '원내/원외 처방구분', '투여경로')
	lst = source_lst.join(base_lst, left_on='보험코드', right_on='EDI코드')
	

	if what == 'inj_to_in':
		lst = lst.filter(lambda row: row['투여경로']=='3' and row['복지부분류']!='당뇨병용제')
		lst.to_excel('inj_to_in.xlsx')
	
	for record in lst[:]:
		code = record.get('약품코드')
		component = record['성분자세히'] or record['성분/함량'] or ''
		pro_yn = record['구분']

		if code:
			if what == 'component':
				fk.update_component(code, component)	
			elif what == 'pro_yn':
				value = 'Y' if record['구분'] == '전문' else 'N'
				fk.update_pro_yn(code, value)
			elif what == 'fda_prg':
				value = record['임부']
				fk.update_fda_prg(code, value)
			elif what == 'efcy_cd':
				fk.update_efficacy_code(code, record['복지부분류코드'])
			elif what == 'cmpnt_cd':
				fk.update_component_code(code, record['주성분코드'])
			elif what == 'inj_to_in':
				fk.update_inout(code, 2)


def get_label_list(test):
	if test:
		return read_excel(DRUG_DB_PATH).filter(lambda row: row['단일포장구분'] in ["S", "P"])
	fk = FkocsAPI(server=server, user=user, password=password, database=database)
	return fk.get_label_info(**codes)

def get_inj_list(test):
	if test:
		return read_excel(DRUG_DB_PATH).filter(lambda row: row['투여경로'] == "3")
	fk = FkocsAPI(server=server, user=user, password=password, database=database)
	return fk.get_inj_info(**codes)

def get_nutfluid_list(test):
	if test:
		return read_excel(DRUG_DB_PATH).filter(lambda row: row['효능코드(보건복지부)'] in ["325"] or "알부민" in row['약품명(한글)'])
	fk = FkocsAPI(server=server, user=user, password=password, database=database)
	return fk.get_nutfluid_info(**codes)

def get_all_list(test=False, **kwargs):
	if test:
		return read_excel(DRUG_DB_PATH)
	fk = FkocsAPI(server=server, user=user, password=password, database=database)
	return fk.get_all_info(**codes)








	

