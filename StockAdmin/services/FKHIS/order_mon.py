from pprint import pprint
from listorm import Listorm
try:
	from .api_requests import *
except:
	from api_requests import *


def get_order_object_list(order_date):
	ordmon = OrdMonApiRequest(API_REQ['order']['ptnt_info'])
	ordmon.api_call(order_date)
	records = ordmon.get_records()
	return Listorm(records)

def get_order_object_list_test(order_date):
	ordmon = OrdMonApiRequest(API_REQ['order']['ptnt_info'])
	ordmon.set_test_response('response_samples/jupsoo4.4.rsp')
	records = ordmon.get_records()
	return Listorm(records)

# lst =  get_order_object_list('2017-09-25')

# # 	# pass
# pprint(lst.select('ptnt_no', 'ward').rename(ward='WARD').distinct('ptnt_no'))