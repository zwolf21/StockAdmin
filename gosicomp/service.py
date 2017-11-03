from .gosi_compare import *

def get_compare_result(file, test=False, to_list=False, **kwargs):

	fn, ext = os.path.splitext(file.name)
	filename = "{}(비교결과).xlsx".format(fn)

	gosi_tbl = get_tables_from_gosi(scheme=['제품코드', '제품명', '상한금액'], **kwargs)
	gosi_tbl.set_number_type(제품코드='')
	drug_info = get_all_list(test=test)
	drug_info.set_number_type(보험단가=0)
	join_result = drug_info.join(gosi_tbl, left_on='EDI코드', right_on='제품코드')
	join_result.add_columns(상한초과=lambda row: row.보험단가 > row.상한금액)
	join_result = join_result.map(**{'원내/원외 처방구분': lambda key: {'1': '원외만', '2': '원내만', '3': '원외/원내'}.get(key, key)})
	join_result = join_result.rename(**{'원내/원외 처방구분': '원내외'})
	# print(join_result)
	suga_info = get_all_suga()
	join_result = join_result.join(suga_info, left_on='약품코드', right_on='수가코드')
	# join_result.to_excel('test.xlsx')
	contents =  join_result.to_excel(selects=['시트명', '제품코드','제품명','약품코드','원내외', '상한금액','보험단가', '일반단가', '상한초과', '수가시작일자', '수가종료일자','시작일자', '종료일자'])
	if to_list:
		return join_result
	return file_response(contents, filename)

