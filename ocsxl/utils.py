import os, datetime

from listorm import Listorm, read_excel

from .getdiff import compare_contents, write_updated

OCS_MASTER_COLUMNS = ["약품코드", "약품명(영문)", "약품명(한글)", "성분명", "시작일자", "종료일자", "원내/원외 처방구분", "보험단가", "일반단가", "효능코드(보건복지부)", "효능코드명", "기본처방용법명", "성분코드", "수가코드", "수가명", "EDI코드", "EDI단가", "제약회사코드", "제약회사명", "투여경로", "상세투여경로코드", "상세투여경로", "제형코드", "수입약품여부", "약품관리구분", "임상연구번호", "약품법적구분", "항균제구분", "항암제구분", "FDA분류(임산부)", "FDA분류(수유부)", "전문의약품여부", "처치약품여부", "심평원평가구분", "포장단위", "규격량", "규격단위", "함량1", "함량단위1", "함량2", "함량단위2", "용량1", "용량단위1", "용량2", "용량단위2", "원내처방사유코드", "기본처방투여량(1회량)", "기본처방투여량(1일량)", "기본처방단위구분", "기본처방횟수", "기본처방일수", "기본처방용법", "처방최대량 (성인)", "처방최대량 (소아)", "처방최대일수", "처방허용여부 (처방과별)", "처방허용여부 (처방의별)", "조제고정용법", "주의사항코드", "산제가능여부", "정제분할구분", "단일포장구분", "처방전 출력제외여부", "조제계산기준코드", "조제기준단위구분", "조제기준단위", "수가기준단위구분", "누적약품여부", "누적약품기준량", "ATC조제여부(외래약국)", "ATC조제여부(병실약국)", "배달약품여부", "택배가능여부", "보관방법코드", "보관용기코드", "차광보관여부", "감사대상여부", "복약상담대상여부", "물품코드", "물품명", "물품청구단위", "물품청구환산량", "비고(공개)", "비고(약국전용)", "약장위치", "대사효소", "대사기능에따른용량조절", "신청자ID", "신청일자", "신청일련번호", "수가확인여부", "수가확인자ID", "수가확인자명", "수가확인일시", "대체여부", "대체약품코드", "대체약품명", "폐기여부", "폐기사유코드", "폐기사유내용", "인슐린구분", "최대허용용량", "최대허용일수", "수가시작일자", "수가종료일자", "PRN여부", "고주의약품분류", "시작일자 변경가능여부"]


def is_excel_file(filename):
	_, ext = os.path.splitext(filename)
	if ext in ('.xls', '.xlsx'):
		return True
	return False


def is_ocsxl(excel_file_contents):
	lst = read_excel(file_contents=excel_file_contents)
	if lst:
		columns = set(lst[0].keys())
		if columns <= set(OCS_MASTER_COLUMNS):
			return True
	return False

def get_item_count(excel_file_contents):
	if is_ocsxl(excel_file_contents): 
		lst = read_excel(file_contents=excel_file_contents)
		return len(lst)
	return 0

def get_compare(excel_file_content_before, excel_file_content_after, to_context=True):
	if is_ocsxl(excel_file_content_after) and is_ocsxl(excel_file_content_before):
		if to_context:
			return compare_contents(excel_file_content_before, excel_file_content_after, pk='약품코드', extras=('약품명(한글)', 'EDI코드'), to_context=True)
		return compare_contents(excel_file_content_before, excel_file_content_after, pk='약품코드', extras=['약품명(한글)', 'EDI코드'])


def make_description(items_count):
	str_time_stamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
	return "{} 건의 약품이 {} 에 저장 됨".format(items_count, str_time_stamp)


def transfrom_updated_result(changes_updated):
	return write_updated(changes_updated, None, pk='약품코드', column_orders=OCS_MASTER_COLUMNS, extras=['약품명(한글)', 'EDI코드'])





