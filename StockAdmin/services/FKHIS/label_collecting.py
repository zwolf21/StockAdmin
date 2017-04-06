import os
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
	for row in recs:
		print(row)

	recs.format([('tot_qty', 0)])
	recs.group_by(['drug_nm'], [('tot_qty', sum, 'agg_qty'), ('drug_nm', len, 'ord_cnt')], ['drug_nm', 'drug_cd', 'agg_qty', 'ord_cnt'])
	return recs


to_path = 'C:\\Users\\pc\\Desktop\\집계.xlsx'
# if os.path.exists(to_path):
# 	os.unlink(to_path)


# ret = get_object_list(('2017-04-06', '17:55:00'), ('2017-04-06', '23:59:59'), 'big')


	


