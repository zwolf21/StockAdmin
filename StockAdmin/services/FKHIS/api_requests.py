import re, os
from socket import *

from bs4 import BeautifulSoup


SERVER = '192.168.8.8'
PORT = 7501
MODULE_BASE = os.path.dirname(__file__)

API_REQ = {
	'order': {
		'ptnt_info': bytes.fromhex('2e4e45540100000000000e06000004000101240000007463703a2f2f3139322e3136382e382e383a373530312f464b4849535f5355505f50484d06000101180000006170706c69636174696f6e2f6f637465742d73747265616d00000001000000ffffffff01000000000000001514000000121253656c537069526370744c69737450746e74127d464b4849532e5355502e52656d6f74652e50484d2e50484d52656d6f74652c20464b4849532e5355502e52656d6f74652e50484d2e50726f78792c2056657273696f6e3d302e302e302e302c2043756c747572653d6e65757472616c2c205075626c69634b6579546f6b656e3d3766363861633765626361636364343810010000000100000009020000000c030000004d46756a697473752e46572c2056657273696f6e3d342e302e302e302c2043756c747572653d6e65757472616c2c205075626c69634b6579546f6b656e3d393832353935396336303530313066660c040000004e53797374656d2e446174612c2056657273696f6e3d342e302e302e302c2043756c747572653d6e65757472616c2c205075626c69634b6579546f6b656e3d6237376135633536313933346530383905020000002046756a697473752e46572e464b506172616d65746572436f6c6c656374696f6e07000000085f646174615365740a5f646174615461626c65065f6974656d73075f726573756c74095f75736572496e666f065f6572726f72095f636f6e6e496e666f040403000400041353797374656d2e446174612e44617461536574040000001553797374656d2e446174612e446174615461626c65040000001c53797374656d2e436f6c6c656374696f6e732e486173687461626c65081346756a697473752e46572e55736572496e666f03000000011946756a697473752e46572e436f6e6e656374696f6e496e666f03000000030000000a0a0905000000000000000906000000000a04050000001c53797374656d2e436f6c6c656374696f6e732e486173687461626c65070000000a4c6f6164466163746f720756657273696f6e08436f6d70617265721048617368436f646550726f7669646572084861736853697a65044b6579730656616c756573000003030005050b081c53797374656d2e436f6c6c656374696f6e732e49436f6d70617265722453797374656d2e436f6c6c656374696f6e732e4948617368436f646550726f766964657208ec51383f0d0000000a0a110000000907000000090800000005060000001346756a697473752e46572e55736572496e666f12000000075f686f73704762075f656d706c4e6f075f656d706c4e6d075f646570744364075f646570744e6d0b5f4f637047726f757047620a5f4f63705479706547620a5f6c6963656e73654e6f075f636f6e6e4950055f70634e6d0a5f6d616e61676572596e095f66726d44656c596e095f554d656444657074075f466f726d4e6d0a5f5265704465707443640a5f457270446570744364085f455369676e49641d3c4f637355736572496e6465783e6b5f5f4261636b696e674669656c64010101010101010101010101010101010101030000000609000000044850594a060a000000055038383137060b00000009ebacb8ed9da5ec84ad060c000000045041524d060d00000009ec95bdeca09ceab3bc060e000000025443060f00000002504806100000000006110000000d3139322e3136382e392e32313706120000000550432d50430613000000014e061400000001590910000000061600000024464b4849532e5355502e57696e2e50484d2e4950442e497064526370744e6577466f726d0617000000045041524d0618000000045041524d0619000000055038383137061a000000013110070000000b000000061b0000000950524f475f53545553061c0000000d524350545f4352544e5f594d44061d0000000b524350545f4f52445f5450061e000000074d4544495f4e4f061f000000045741524406200000000c524350545f445255475f4742062100000007524554525f474206220000000750544e545f4e4f062300000008524350545f444752062400000010524350545f445255475f4c41575f4742062500000007494e4a435f474210080000000b000000062600000005594e5959590627000000083230313730343035062800000004594e4e4e06290000000125062a00000001250929000000062c00000001320929000000062e0000000125062f000000035959590630000000035959590b'),

	},
	'opremain': {
		'psy' : bytes.fromhex(''),

	},
	'opstock': {
		'psy':  bytes.fromhex('2e4e45540100000000004505000004000101240000007463703a2f2f3139322e3136382e382e383a373530312f464b4849535f5355505f50484d06000101180000006170706c69636174696f6e2f6f637465742d73747265616d00000001000000ffffffff01000000000000001514000000121853656c53706e447275674d73744279447275674c61774762127d464b4849532e5355502e52656d6f74652e50484d2e50484d52656d6f74652c20464b4849532e5355502e52656d6f74652e50484d2e50726f78792c2056657273696f6e3d302e302e302e302c2043756c747572653d6e65757472616c2c205075626c69634b6579546f6b656e3d3766363861633765626361636364343810010000000100000009020000000c030000004d46756a697473752e46572c2056657273696f6e3d342e302e302e302c2043756c747572653d6e65757472616c2c205075626c69634b6579546f6b656e3d393832353935396336303530313066660c040000004e53797374656d2e446174612c2056657273696f6e3d342e302e302e302c2043756c747572653d6e65757472616c2c205075626c69634b6579546f6b656e3d6237376135633536313933346530383905020000002046756a697473752e46572e464b506172616d65746572436f6c6c656374696f6e07000000085f646174615365740a5f646174615461626c65065f6974656d73075f726573756c74095f75736572496e666f065f6572726f72095f636f6e6e496e666f040403000400041353797374656d2e446174612e44617461536574040000001553797374656d2e446174612e446174615461626c65040000001c53797374656d2e436f6c6c656374696f6e732e486173687461626c65081346756a697473752e46572e55736572496e666f03000000011946756a697473752e46572e436f6e6e656374696f6e496e666f03000000030000000a0a0905000000000000000906000000000a04050000001c53797374656d2e436f6c6c656374696f6e732e486173687461626c65070000000a4c6f6164466163746f720756657273696f6e08436f6d70617265721048617368436f646550726f7669646572084861736853697a65044b6579730656616c756573000003030005050b081c53797374656d2e436f6c6c656374696f6e732e49436f6d70617265722453797374656d2e436f6c6c656374696f6e732e4948617368436f646550726f766964657208ec51383f020000000a0a030000000907000000090800000005060000001346756a697473752e46572e55736572496e666f12000000075f686f73704762075f656d706c4e6f075f656d706c4e6d075f646570744364075f646570744e6d0b5f4f637047726f757047620a5f4f63705479706547620a5f6c6963656e73654e6f075f636f6e6e4950055f70634e6d0a5f6d616e61676572596e095f66726d44656c596e095f554d656444657074075f466f726d4e6d0a5f5265704465707443640a5f457270446570744364085f455369676e49641d3c4f637355736572496e6465783e6b5f5f4261636b696e674669656c64010101010101010101010101010101010101030000000609000000044850594a060a000000055038383137060b00000009ebacb8ed9da5ec84ad060c000000045041524d060d00000009ec95bdeca09ceab3bc060e000000025443060f00000002504806100000000006110000000d3139322e3136382e392e32313706120000000550432d50430613000000014e061400000001590910000000061600000024464b4849532e5355502e57696e2e50484d2e4e41522e4e6172637453746f636b466f726d0617000000045041524d0618000000045041524d0619000000055038383137061a0000000131100700000002000000061b000000075354445f594d44061c0000000b445255475f4c41575f4742100800000002000000061d000000083230313730343033061e00000001320b'),
		'narc': bytes.fromhex('2e4e45540100000000004505000004000101240000007463703a2f2f3139322e3136382e382e383a373530312f464b4849535f5355505f50484d06000101180000006170706c69636174696f6e2f6f637465742d73747265616d00000001000000ffffffff01000000000000001514000000121853656c53706e447275674d73744279447275674c61774762127d464b4849532e5355502e52656d6f74652e50484d2e50484d52656d6f74652c20464b4849532e5355502e52656d6f74652e50484d2e50726f78792c2056657273696f6e3d302e302e302e302c2043756c747572653d6e65757472616c2c205075626c69634b6579546f6b656e3d3766363861633765626361636364343810010000000100000009020000000c030000004d46756a697473752e46572c2056657273696f6e3d342e302e302e302c2043756c747572653d6e65757472616c2c205075626c69634b6579546f6b656e3d393832353935396336303530313066660c040000004e53797374656d2e446174612c2056657273696f6e3d342e302e302e302c2043756c747572653d6e65757472616c2c205075626c69634b6579546f6b656e3d6237376135633536313933346530383905020000002046756a697473752e46572e464b506172616d65746572436f6c6c656374696f6e07000000085f646174615365740a5f646174615461626c65065f6974656d73075f726573756c74095f75736572496e666f065f6572726f72095f636f6e6e496e666f040403000400041353797374656d2e446174612e44617461536574040000001553797374656d2e446174612e446174615461626c65040000001c53797374656d2e436f6c6c656374696f6e732e486173687461626c65081346756a697473752e46572e55736572496e666f03000000011946756a697473752e46572e436f6e6e656374696f6e496e666f03000000030000000a0a0905000000000000000906000000000a04050000001c53797374656d2e436f6c6c656374696f6e732e486173687461626c65070000000a4c6f6164466163746f720756657273696f6e08436f6d70617265721048617368436f646550726f7669646572084861736853697a65044b6579730656616c756573000003030005050b081c53797374656d2e436f6c6c656374696f6e732e49436f6d70617265722453797374656d2e436f6c6c656374696f6e732e4948617368436f646550726f766964657208ec51383f020000000a0a030000000907000000090800000005060000001346756a697473752e46572e55736572496e666f12000000075f686f73704762075f656d706c4e6f075f656d706c4e6d075f646570744364075f646570744e6d0b5f4f637047726f757047620a5f4f63705479706547620a5f6c6963656e73654e6f075f636f6e6e4950055f70634e6d0a5f6d616e61676572596e095f66726d44656c596e095f554d656444657074075f466f726d4e6d0a5f5265704465707443640a5f457270446570744364085f455369676e49641d3c4f637355736572496e6465783e6b5f5f4261636b696e674669656c64010101010101010101010101010101010101030000000609000000044850594a060a000000055038383137060b00000009ebacb8ed9da5ec84ad060c000000045041524d060d00000009ec95bdeca09ceab3bc060e000000025443060f00000002504806100000000006110000000d3139322e3136382e392e32313706120000000550432d50430613000000014e061400000001590910000000061600000024464b4849532e5355502e57696e2e50484d2e4e41522e4e6172637453746f636b466f726d0617000000045041524d0618000000045041524d0619000000055038383137061a0000000131100700000002000000061b000000075354445f594d44061c0000000b445255475f4c41575f4742100800000002000000061d000000083230313730343033061e00000001310b'),
	}
}


class ApiRequest:

	def __init__(self, request_bytes):
		self.reqeust = request_bytes

	def api_call(self, host=SERVER, port=PORT, timeout=60):
		cs = socket(AF_INET, SOCK_STREAM)
		cs.settimeout(timeout)
		cs.connect((host, port))
		cs.send(self.reqeust)
		response = b''
		while True:
			data = cs.recv(1024)
			response += data
			if data[-1] == 11:
				cs.close()
				break
		self.raw = response

	def get_records(self, table_name, encoding='utf-8'):
		soup = BeautifulSoup(self.raw.decode(encoding , errors='replace') if encoding else self.raw, 'html.parser')
		return [{column.name: column.text for column in ptnt.children} for ptnt in soup.find_all(table_name)]

	def ext_new_data_set(self):
		content_pat = re.compile(b'<NewDataSet>.+<\/NewDataSet>')
		return content_pat.find_all(self.raw)

	def set_test_response(self, response_sample_path):
		with open(os.path.join(MODULE_BASE, response_sample_path), 'rb') as fp:
			self.raw = fp.read()


class OpstockApiRequest(ApiRequest):

	def __init__(self, request_bytes, stock_date):
		content_pat = re.compile(b'<NewDataSet>.+<\/NewDataSet>')
		super(OpstockApiRequest, self).__init__(content_pat.find_all(request_bytes)[1])
		self.date = start_date

	def set_date(self):
		date = self.date.replace('-', '').encode()
		pat = re.compile(b'\d{8}')
		self.raw = pat.sub(date, self.raw)

		


class OpremainApiRequest(ApiRequest):

	def __init__(self, request_bytes, start_date, end_date):
		super(OpremainApiRequest, self).__init__(request_bytes)
		self.start = start_date
		self.end = end_date

	def set_date_range(self, start, end):
		start = self.start.replace('-', '').encode()
		end = self.end.replace('-', '').encode()
		pat = re.compile(b'\d{8}')
		self.raw = pat.sub(start, self.raw)
		self.raw = pat.sub(end, self.raw, 1)



class OrdMonApiRequest(ApiRequest):
	table_name = 'ptntlist'

	def __init__(self, request_bytes):
		super(OrdMonApiRequest, self).__init__(request_bytes)

	def api_call(self, ord_date):
		super(OrdMonApiRequest, self).api_call()
		date = ord_date.replace('-', '').encode()
		pat = re.compile(b'\d{8}')
		self.raw = pat.sub(date, self.raw)
		
	def get_records(self):
		return super(OrdMonApiRequest, self).get_records(self.table_name)




