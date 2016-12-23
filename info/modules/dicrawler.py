from bs4 import BeautifulSoup
from urllib.request import *
from urllib.parse import *
import re


class Crawler(object):
	"""docstring for Crawler"""
	def __init__(self, url, page_encoding='utf-8', **req_header):
		self.url = url
		req = Request(url)
		for hdr, val in req_header.items():
			req.add_header(hdr, val)
		self.soup = BeautifulSoup(urlopen(req).read().decode(encoding=page_encoding), 'html.parser')


	def show_html(self):
		print(self.soup)
		
	def ext_links(self, regPattern, **tagAttr):
		rex = re.compile(regPattern)
		for tag, attr in tagAttr.items():
			qry = '{}[{}]'.format(tag, attr)
			links = self.soup.select(qry)
			return [link for link in links if rex.search(link[attr])]

	def ext_tables(self, *column, only_data=True):
		spc = re.compile('\s+')
		ret = []
		for table in self.soup('table'):
			if table('table'):
				continue
			hdr, *recs = table('tr')
			hdr_val = [spc.sub(' ', hdr.text).strip() for hdr in hdr.select('td, th')]

			if set(column) <= set(hdr_val):
				if only_data:
					ret+=[dict(zip(hdr_val, [spc.sub(' ',rec.text).strip() for rec in rec('td')])) for rec in recs]
				else:
					ret+=[dict(zip(hdr_val, [rec for rec in rec('td')])) for rec in recs]
		return ret
					

	


class DrugInfoSearch(Crawler):
	"""docstring for DrugInfo"""
	host = 'http://www.druginfo.co.kr/'
	cookie = 'ASP.NET_SessionId=dcf5it2xjh5vug552iqzy3ex; userId=eb5d597f75e166e8a642f84684740a700a7eb2af23b1a1f0ece5cd9634c9d5e554e6ef1b0f4108aaf937b61fd07c9928; userIp=9ba91e4438eee45af0b3b1894b0c8275c430d47df08d9eef63410aa7f79ff7d5743c07eb31149f7ec5b6d0ae6bb5b548; userName=eb5d597f75e166e8a642f84684740a700a7eb2af23b1a1f0ece5cd9634c9d5e554e6ef1b0f4108aaf937b61fd07c9928; userPid=fb8c6c99ee8478b4750b1dfab3df0b65e90f6440a8aeb1eed7429af04cddcfcb548a123325b697c1463529b24ce34237; userRole=4498d4ab12af0b8ddd5c28875c46ce5f8a86b2caf722fbd7780194be91efdd665bf26e9566ec930c817da2f137a7471d; userTime=f944b136ba411f9e4e3dfd7c5b34a33f2e4f796e4f19eda9d5dbf0d4408867615efde023b7a45444c17e12964dbd925c; userJobSort=7ab78d7c6be16ad261e456f33ef3f6d52e62105491597dde66c605b8edae98db; userPoint=0ea5cc69ce53e7613837a65c0b18c7892abf635cd0a828bc3360d2fcd40c670b; userTel=dd2af4acba624126d1d1d3423ecd5fb541eb27598421c0aa175d7f7ecc88ba774f31ad5f041e96b52b81623fc0880758; userEmail=b56ee86ed55f5cf1e2ee3b7a7ab57e135b822a6787395a788a6a64ec383acde2dd4574a3a63b4ce762373b199b8cef4b; userSummits=1752c0e36aea5bf64643d871736e496c80465287b25525787de7e37c57c1f815; companyName=1752c0e36aea5bf64643d871736e496c80465287b25525787de7e37c57c1f815; prevUrl=http://www.druginfo.co.kr/detail/product.aspx?pid=214732&; _ga=GA1.3.981463393.1481303669; _gat=1; __utmt=1; __utma=133333467.981463393.1481303669.1481303669.1481306265.2; __utmb=133333467.2.10.1481306265; __utmc=133333467; __utmz=133333467.1481303669.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none)'

	def __init__(self, keyword):
		url = 'http://www.druginfo.co.kr/search2/search.aspx?q={}'.format(quote(keyword, encoding='cp949'))
		super(DrugInfoSearch, self).__init__(url, page_encoding='cp949', cookie=self.cookie)
		
	def get_search_list(self):
		return self.ext_tables('제품명', '임부','보험코드',only_data=True)

	def get_detail_url(self):
		ret = self.ext_tables('제품명','임부','보험코드', only_data=False)
		try:
			detail_url = urljoin(self.host, ret[0]['제품명'].a['href'])
		except:
			detail_url = 'noresult'
		else:
			return detail_url

	def get_detail_info(self, *select):
		detail_url = self.get_detail_url()
		cw = Crawler(detail_url, 'cp949', cookie=self.cookie)
		ret = {}
		for elm in cw.ext_tables('항목','내용'):
			if elm['항목'] in select:
				ret[elm['항목']] = elm['내용']
		return ret


	def _pkg_num_from(self, pkg_str):
		regx = re.compile('(\d+)정|(\d+)caps?|(\d+)T|(\d+)개|(\d+)바이알|(\d+)캡슐|(\d+)C|(\d+)CAPS|(\d+)|(\d+)EA|(\d+)TAB|(\d+)tab|(\d+)캅셀|(\d+)펜|(\d+)V|(\d+)P|(\d+)포')
		try:
			ret = list(filter(None, regx.findall(pkg_str)[-1]))[0]
			return ret
		except IndexError:
			return 1

	def _norm_price(self, price_str):
		regx = re.compile('[^\d]')
		return regx.sub('', price_str)

	def get_narcotic_class(self):
		url = self.get_detail_url()
		cw = Crawler(url, 'cp949', cookie=self.cookie)
		soup = cw.soup
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



def get_drug_info(keyword,  *detail_select,  result_limit=15):
	lg = DrugInfoSearch(keyword)
	search_list = lg.get_search_list()

	for result in search_list[:result_limit]:
		edi = result.get('보험코드')
		if not edi:
			dg = DrugInfoSearch(result['제품명'])
		else:
			dg = DrugInfoSearch(edi)
		details = dg.get_detail_info(*detail_select)
		result.update(details)
		pkg_str = result.get('포장·유통단위')
		price_str = result.get('약가')
		if pkg_str:
			result['pkg_amount'] =dg._pkg_num_from(pkg_str)
		if price_str:
			result['약가']= dg._norm_price(price_str)
			
		result['narcotic_class'] = dg.get_narcotic_class()
		yield result










