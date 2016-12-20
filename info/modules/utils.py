# -*- coding: utf-8 -*-
import xlrd
from bs4 import BeautifulSoup
from urllib.request import *
from urllib.parse import *
import re, os, csv
from django.http import HttpResponse


def is_xlfile(file_name):
	fn, ext = os.path.splitext(file_name)
	if ext in ['.xls', '.xlsx']:
		return True	
	else:
		return False


def xlDB2DicIter(xls):
	wb = xlrd.open_workbook(xls)
	sht = wb.sheet_by_index(0)
	return [dict(zip(sht.row_values(0),sht.row_values(r))) for r in range(1,sht.nrows)]





class DICrawler:
	base_list_url = 'https://www.druginfo.co.kr/search2/search.aspx?q='
	base_detail_url = 'https://www.druginfo.co.kr/detail/product.aspx?pid='
	druginfo_cookie = 'userPid=325940fba6b853802913ade569774e8dc23964d1c95c6fe7bd7d45186a9194c713e93aac69419e3eec372abd43cfdc2a'

	def edi_parse(edis, parse_count=100):
		edi_set = edis.split()
		n = 0
		for n in range(len(edi_set)//parse_count):
			yield ' '.join(edi_set[n:n+parse_count])


	@classmethod
	def iter_drug_summary(self, kw):
		html = urlopen(self.base_list_url+quote(kw, encoding='cp949')).read()
		soup = BeautifulSoup(html, 'html.parser')
		# detail_url = soup.select('a[href^=/detail/product.aspx?pid=]')
		tables = soup.select("div[class$=table-res] > table")
		if not tables:
			return
		for table in tables:
			thead, *tbody = table.find_all('tr')
			hdr = [th.text for th in thead.find_all('td')]
			if set(hdr) != {'', '보험', '성분/함량', '약가', '대체', '제품명', '조회수', '수정', '보험코드', '판매사', '임부', '구분'}:
				continue
			for tr in tbody:
				d =  dict(zip(hdr,(td.text.strip().split('\n')[0] for td in tr.find_all('td'))))
				href = tr.select('a[href^=/detail/product.aspx?pid=]') or [{'href':''}]
				d['detail_url'] = urljoin(self.base_detail_url, href[0]['href'])
				d['약가'] = d['약가'].replace(',','')
				yield d

	@classmethod
	def iter_drug_detail(self, kw):
		for info in self.iter_drug_summary(kw) or []:
			if  not info.get('detail_url'):
				continue
			url = info['detail_url']
			req = Request(url)
			req.add_header('Cookie',self.druginfo_cookie)
			try:
				html = urlopen(req).read().decode(encoding='cp949')
			except Exception as e:
				pass
			else:
				yield html


			
	@classmethod
	def get_pkg_unit(self, html):
			soup = BeautifulSoup(html, 'html.parser')
			tds = soup.select('td[class=pdt-head-cell-left]')
			pack_units = [td for td in tds if td.text == '포장·유통단위']
			if pack_units:
				pack_unit = pack_units[0]
				unit_str =  pack_units[0].next_sibling.next_sibling.text
				# print(unit_str)
				regx = re.compile('(\d+)정|(\d+)caps?|(\d+)T|(\d+)개|(\d+)바이알|(\d+)캡슐|(\d+)C|(\d+)CAPS|(\d+)|(\d+)EA|(\d+)TAB|(\d+)tab|(\d+)캅셀|(\d+)펜|(\d+)V|(\d+)P|(\d+)포')
				try:
					ret = list(filter(None, regx.findall(unit_str)[-1]))[0]
					return unit_str, ret
				except IndexError:
					return '',1
			return '', 1


	@classmethod
	def get_narcotic_class(self, html):
		soup = BeautifulSoup(html, 'html.parser')
		mdt = soup('td',{'class':"medi_t2"})

		if mdt:
			for m in mdt:
				if '향정의약품' in m.text:
					return 2
				elif '마약' in m.text:
					return 1
				else:
					continue
			return 0


