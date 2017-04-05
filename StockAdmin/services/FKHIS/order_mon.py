try:
	from .recordlib import RecordParser
	from .api_requests import *
except:
	from recordlib import RecordParser
	from api_requests import *


def get_order_object_list(order_date):
	ordmon = OrdMonApiRequest(API_REQ['order']['ptnt_info'])
	ordmon.api_call(order_date)
	records = ordmon.get_records()
	return records

def get_order_object_list_test(order_date):
	ordmon = OrdMonApiRequest(API_REQ['order']['ptnt_info'])
	ordmon.set_test_response('response_samples/jupsoo4.4.rsp')
	records = ordmon.get_records()
	return records

# for ret in get_order_object_list('2017-04-05'):
# 	print(ret)
