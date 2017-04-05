try:
	from recordlib import RecordParser
	from api_requests import LabelCollectingApiRequest, ApiRequest, API_REQ
except:
	from .recordlib import RecordParser
	from .api_requests import LabelCollectingApiRequest, ApiRequest


def get_object_list_test(start_dtime, end_dtime, kind):
	req = LabelCollectingApiRequest(API_REQ['collecting'][kind], start_dtime, end_dtime)
	req.set_test_response('response_samples/LabelCollecting.sample.rsp')
	records = req.get_records('table1')
	recs = RecordParser(records=records)
	recs.format([('tot_qty', 0)])
	recs.group_by(['drug_nm'], [('tot_qty', sum, 'agg_qty')], ['drug_nm', 'drug_cd', 'agg_qty'])

	return recs.records

def get_object_list(start_dtime, end_dtime, kind):
	req = LabelCollectingApiRequest(API_REQ['collecting'][kind], start_dtime, end_dtime)
	req.api_call()
	records = req.get_records('table1')
	recs = RecordParser(records=records)
	recs.format([('tot_qty', 0)])
	recs.group_by(['drug_nm'], [('tot_qty', sum, 'agg_qty')], ['drug_nm', 'drug_cd', 'agg_qty'])





r = get_object_list_test(('2017-04-01', '13:00:01'), ('2017-04-02', '20:17:08'), 'inj')
print(r)
