try:
	from .recordlib import RecordParser
	from .api_requests import *
except:
	from recordlib import RecordParser
	from api_requests import *


def get_order_object_list(order_date):
	ordmon = OrdMonApiRequest(API_REQ['order']['ptnt_info'])
	ordmon.api_call(order_date)
	record = ordmon.get_records()
	return record

def get_order_object_list_test(order_date):
	ordmon = OrdMonApiRequest(API_REQ['order']['ptnt_info'])
	ordmon.set_test_response('response_samples/jupsoo4.4.rsp')
	record = ordmon.get_records()
	return record


# get_order_object_list_test('20')


