import os, sys, re, datetime, math
from pprint import pprint
from functools import partial, wraps
from listorm import Listorm, read_excel

from dateutil.parser import parse

# MODULE_BASE = os.path.dirname(os.path.dirname(__file__))
# MODULE_PATH = os.path.join(MODULE_BASE, 'StockAdmin/services/FKHIS')
# sys.path.append(MODULE_PATH)


try:
    from .api_requests import OrderSelectApiRequest
    from .dbconn import get_all_list
    from .order_mon import get_order_object_list

except:
    from api_requests import OrderSelectApiRequest
    from dbconn import get_all_list
    from order_mon import get_order_object_list


type_order = {'ST':1, 'AD':2, 'EM':3, 'OT':4}
kind_order = {'LABEL':1, 'INJ':2, 'NUT':3}
type_verbose = {'ST': '정기', 'AD': '추가', 'EM': '응급', 'OT': '퇴원'}
type_reverbose = {v:k for k, v in type_verbose.items()}
kind_verbose = {'NUT': '영양수액', 'INJ': '주사', 'LABEL': '라벨'}
kind_reverbose = {v:k for k, v in kind_verbose.items()}


unit_sort = lambda unit: {'ML': 100, 'G': 101, '통': 102, 'BAG':998, 'KIT': 1000, 'VIAL': 1001, 'AMP': 1002, 'SYR': 1003}.get(unit, 0)


def time_to_normstr(*time_values, to='date'):
    ret = []
    for value in time_values:
        if isinstance(value, (datetime.date, datetime.datetime)):
            time = value
        elif isinstance(value, str):
            try:
                time = parse(value)
            except ValueError:
                time = value
        else:
            time = value        
        ret.append(time)
    if to == 'date':
        ret = tuple(map(lambda time: time.strftime("%Y-%m-%d"), ret))
    else:
        ret = tuple(map(lambda time: time.strftime("%Y-%m-%d %H:%M:%S"), ret))

    if len(ret) == 1:
        return ret[0]
    return ret


def norm_field(get_orderset):
    @wraps(get_orderset)
    def wrapper(types, wards, start_date, end_date, start_dt, end_dt, kind, kinds=None, date=None, get_static=None, **kwargs):
        types = list(map(lambda type: type_verbose.get(type, type), types))
        wards = re.split('\s*,\s*', wards) if isinstance(wards, str) else wards
        start_date, end_date = time_to_normstr(start_date, end_date)
        start_dt, end_dt = time_to_normstr(start_dt, end_dt, to='datetime')
        kind = kind_reverbose.get(kind, kind)

        date = date or datetime.date.today()
        date = date if isinstance(date, str) else time_to_normstr(date)
        return get_orderset(types=types, wards=wards, start_date=start_date, end_date=end_date, start_dt=start_dt, end_dt=end_dt, kind=kind, kinds=kinds, date=date, get_static=get_static, **kwargs)
    return wrapper

def norm_context(context, verbosing=None, time_to_str=True):
    new_context = {k:v for k, v in context.items()}
    types = context['types']
    kinds = context['kinds']

    if isinstance(kinds, str): kinds = [kinds]
    if isinstance(types, str): types = [types]

    if verbosing is not None:
        if isinstance(verbosing, str): verbosing = [verbosing]
        if 'types' in verbosing:
            types = sorted(map(lambda t: type_verbose.get(t, t), types), key=lambda t: type_order.get(t,t))
            new_context['types'] = types
        if 'kinds' in verbosing:
            kinds = list(map(lambda k: kind_verbose.get(k, ), kinds))
            new_context['kinds'] = kinds

    if time_to_str:
        new_context['start_dt'], new_context['end_dt'] = time_to_normstr(context['start_dt'], context['end_dt'], to='datetime')
        new_context['date'], new_context['start_date'], new_context['end_date'] = time_to_normstr(context['date'], context['start_date'], context['end_date'])
    return new_context



def norm_drug_name(name):
    ori_name = name
    pat = re.compile(r'^.+?\}')
    while True:
        name = pat.sub('', name)
        m = pat.search(name)
        if not m:
            return name.strip() or ori_name

class OrderApi(object):

    def __init__(self, static=None, test=False, **kwargs):
        kwargs['start_date'], kwargs['end_date'] = time_to_normstr(kwargs.get('start_date'), kwargs.get('end_date'))
        self.ptnt_lst = Listorm()
        self.static= self._norm_static(static)
        self.drug_list = get_all_list(test=test)
        self.set_order_list(test=test, **kwargs)
        if not test:
            self.set_ptnt_list(**kwargs)

    def _norm_static(self, static):
        new = []
        static = Listorm(static) or Listorm()
        for row in static:
            kind = row.get('kind')
            extras, excludes, exclude_groups = row.get('extras', Listorm()), row.get('excludes', Listorm()), row.get('exclude_groups', Listorm())
            extras = re.split('\s*[\r\n]+,*\s*', extras) if isinstance(extras, str) else extras or Listorm()
            excludes = re.split('\s*[\r\n]+,*\s*', excludes) if isinstance(excludes, str) else excludes or []
            exclude_groups = re.findall('\d{3}', exclude_groups) if isinstance(exclude_groups, str) else exclude_groups or []
            new.append({'kind': kind, 'extras': extras, 'excludes': excludes, 'exclude_groups': exclude_groups})
        return Listorm(new)

    def _get_test_order_list(self, start_date, end_date, wards, **kwargs):
        request = OrderSelectApiRequest(start_date, end_date, wards)
        for ward in wards:
            request.set_test_response('response_samples/orderselect/{}.rsp'.format(ward))
        return Listorm(request.get_records())

    def _get_order_list(self, start_date, end_date, wards, **kwargs):
        request = OrderSelectApiRequest(start_date, end_date, wards)
        request.api_calls(max_worker=10)
        return Listorm(request.get_records())
        
    def set_order_list(self, test, **kwargs):
        if test:
            self.order_list = self._get_test_order_list(**kwargs)
        else:
            self.order_list = self._get_order_list(**kwargs)

    def set_ptnt_list(self, date, **kwargs):
        dates = [date] if isinstance(date, (str, datetime.datetime, datetime.date)) else date
        ptnts = Listorm()
        for date in dates:
            date = time_to_normstr(date)
            ptnts |= Listorm(get_order_object_list(date)).select('ptnt_no', 'ward').rename(ward='WARD').distinct('ptnt_no')
        self.ptnt_lst = ptnts

    def filter_drug_list(self, kinds, exclude_groups=None,**kwargs):
        print('filtering drug list by {}...'.format(kinds))
        static = self.static or {}
        drug_list = Listorm()
        for kind in kinds:
            static = self.static.filterand(kind=kind).first
            extras, excludes = static.extras, static.excludes 
            extras_lst = self.drug_list.filtersim(**{'약품명(한글)': extras})
            if kind == 'LABEL':
                lst = self.drug_list.filter(lambda row: row['단일포장구분'] in ['S', 'P']).orderby('-단일포장구분', '약품명(한글)')
            elif kind == 'NUT':
                lst = self.drug_list.filter(lambda row: row['효능코드(보건복지부)'] in ['325'])
            elif kind == 'INJ':
                lst = self.drug_list.filter(
                    lambda row: row['투여경로'] == '3' and row['약품법적구분'] in ['0'] and row['항암제구분'] == '0'
                )
            # exclude_group 

            lst = lst.filter(lambda row: row['효능코드(보건복지부)'] not in static.exclude_groups)
            drug_list|= lst.excludesim(**{'약품명(한글)': excludes}) | extras_lst
        return drug_list

    def filter_order_list(self, types, start_date, end_date, start_dt, end_dt, **kwargs):
        date_filter = lambda row: row.ord_ymd and start_date <= row.ord_ymd <= end_date and row.rcpt_dt and start_dt <= row.rcpt_dt < end_dt
        types_filter = lambda row: row.rcpt_ord_tp_nm in types
        return self.order_list.filter(lambda row: date_filter(row) and types_filter(row))

    def get_order_lists(self, *filter_contexts, **kwargs):
        print('get_order_lists call..')
        for context in filter_contexts:
            context =  norm_context(context)

            order_list = self.filter_order_list(**context)
            drug_list = self.filter_drug_list(**context).select('약품코드', '단일포장구분', '투여경로', '효능코드(보건복지부)', '약품명(한글)', '조제계산기준코드', '보관방법코드')
            order_list = order_list.join(drug_list, left_on='ord_cd', right_on='약품코드')
            
            if self.ptnt_lst:
                order_list = order_list.join(self.ptnt_lst, on='ptnt_no', how='left').update(WARD=lambda row: row.ward[:2], where=lambda row: not row.WARD) # 전실 정보를 받지 못한 환자는 기본(ward) 병동으로 채움
            else:
                order_list = order_list.update(ward=lambda row: row.ward[:2]).rename(ward='WARD')

            order_list = order_list.filter(lambda row: row.drug_nm and row.WARD in context['wards'])
            order_list = order_list.set_number_type(ord_qty=0.0, ord_frq=0, ord_day=0)
            order_list = order_list.add_columns(once_amt=lambda row: round(row.ord_qty / row.ord_frq, 2), total_amt=lambda row: row.ord_qty * row.ord_day, ward_=lambda row: row.ward[:2])
            order_list = order_list.update(total_amt=lambda row: math.ceil(row.once_amt)*row.ord_frq, where=lambda row: row['조제계산기준코드'] in ['7']) # 회수로 올림 약(7)의 경우 total_amt 의 재계산
            order_list = order_list.add_columns(type=lambda row: {'정기': 'ST', '응급': 'EM', '추가': 'AD', '퇴원': 'OT'}.get(row.rcpt_ord_tp_nm, ''))
            order_list.set_index('ord_seq', 'rcpt_seq', 'ord_exec_seq','rcpt_ord_seq', index_name='pk')
    
            yield order_list


def parse_order_list(order_list):
    if isinstance(order_list, list):
        order_list = Listorm(order_list)

    # 약품명 앞에 냉장} 이런거 빼기    
    order_list.update(drug_nm=lambda row: norm_drug_name(row.drug_nm), where=lambda row: row.drug_nm)

    ret_lst = order_list.filter(lambda row: row.medi_no and row.ret_yn == 'Y')
    ord_lst = order_list.filter(lambda row: row.medi_no and row.ret_yn == 'N')


    rcpt_dt_min, rcpt_dt_max = ord_lst.min('rcpt_dt'), ord_lst.max('rcpt_dt')

    grp_by_drug_nm = ord_lst.groupby('drug_nm', ord_qty=sum, drug_nm=len, total_amt=sum,
        renames={'drug_nm': 'drug_nm_count', 'total_amt': 'total_amt_sum', 'ord_qty': 'ord_qty_sum'},
        extra_columns = ['ord_cd', 'ord_unit_nm', '단일포장구분', '효능코드(보건복지부)', 'std_unit_nm', '보관방법코드'],
        set_name = 'order_set'
    ).orderby('보관방법코드', lambda row: unit_sort(row.std_unit_nm),'단일포장구분', 'drug_nm')

    grp_by_ward = ord_lst.groupby('WARD', ord_qty=sum, total_amt=sum, drug_nm=len,
        renames={'ord_qty': 'ord_qty_sum', 'total_amt': 'total_amt_sum', 'drug_nm': 'drug_nm_count'}, 
        set_name = 'order_set'
    ).orderby('WARD', 'drug_nm')

    grp_by_ward_drug_nm = ord_lst.groupby('WARD', 'drug_nm', ord_qty=sum, total_amt=sum, drug_nm=len,
        renames={'ord_qty': 'ord_qty_sum', 'total_amt': 'total_amt_sum', 'drug_nm': 'drug_nm_count'},
        extra_columns = ['ord_cd', 'ord_unit_nm', '단일포장구분', '효능코드(보건복지부)', '단일포장구분', 'std_unit_nm', '보관방법코드', 'drug_nm'],
        set_name = 'order_set'
    ).orderby('WARD','보관방법코드', lambda row: unit_sort(row.std_unit_nm), '단일포장구분', 'drug_nm')

    grp_by_ward_drug_nm_by_ward = grp_by_ward_drug_nm.groupby('WARD', drug_nm=len,
        renames = {'drug_nm': 'drug_nm_count'},
        extra_columns = ['WARD'],
        set_name = 'ward_set'
    ).orderby('WARD')

    only_dc = ord_lst.filter(lambda row: row.ret_stus not in ['O', 'C'] and row.dc_gb == 'Y')
    dc_and_ret = only_dc.orderby('WARD','보관방법코드', lambda row: unit_sort(row.std_unit_nm), '단일포장구분', 'drug_nm')
    # 2017-10-13 반납은 빼달라는 요청에 의하여 DC만 파싱
    # dc_and_ret = (ret_lst | only_dc).orderby('WARD','보관방법코드', lambda row: unit_sort(row.std_unit_nm), '단일포장구분', 'drug_nm')

    grp_dc_and_ret = dc_and_ret.groupby('WARD', 'medi_no', 'ord_cd','ptnt_no', ord_qty=sum, total_amt=sum, drug_nm=len,
        renames = {'ord_qty': 'ord_qty_sum', 'total_amt': 'total_amt_sum', 'drug_nm': 'drug_nm_count'},
        extra_columns = ['ptnt_nm', 'dc_ent_dt', 'ret_ymd', 'ord_ent_dt', '보관방법코드', '단일포장구분'],
    ).orderby('WARD','보관방법코드', lambda row: unit_sort(row.std_unit_nm), '단일포장구분', 'drug_nm')

    return {
        'grp_by_drug_nm':grp_by_drug_nm,
        'grp_by_ward': grp_by_ward,
        'grp_by_ward_drug_nm': grp_by_ward_drug_nm,
        # 'grp_by_ward_drug_nm_by_ward':grp_by_ward_drug_nm_by_ward,
        'grp_dc_and_ret': grp_dc_and_ret,
        'rcpt_dt_min': rcpt_dt_min, 'rcpt_dt_max': rcpt_dt_max,
    }





# static=[
#     {
#         "extras": "",
#         "kind": "LABEL",
#         "excludes": ""
#     },
#     {
#         "extras": "염화칼륨\r\n염화나트륨주사액\r\n",
#         # "extras": "",
#         "kind": "INJ",
#         "excludes": "에락시스\r\n멕쿨"
#     },
#     {
#         "extras": "란스톤\r\n아달라트\r\n",
#         # "extras": '''에락시스
#         # ''',
#         "kind": "NUT",
#         "excludes": ""
#     }
# ]

# contexts = [
#   {
#       'start_dt': '2017-09-19 00:00:00',
#       'end_dt': '2017-09-20 00:00:00',
#       'types': ['정기', 'AD','EM'],
#       'kinds': ['INJ'],
#       'wards': ['51', '52']
#   }
#   {
#       'start_dt': '2017-09-19 00:00:00',
#       'end_dt': '2017-09-20 23:59:59',
#       'types': ['추가','응급', '정기'],
#       'kinds': ['INJ', 'NUT']
#   },
#   {
#       'start_dt': '2017-09-19 00:00:00',
#       'end_dt': '2017-09-28 23:59:59',
#       'types': ['추가','응급', '정기'],
#       'kinds': ['INJ', 'NUT', 'LABEL']
#   },
#   {
#       'start_dt': '2017-09-19 00:00:00',
#       'end_dt': '2017-09-20 23:59:59',
#       'types': ['추가','응급', 'ST'],
#       'kinds': ['NUT', 'LABEL']
#   },
# ]

# oa = OrderApi(dates=datetime.datetime.now(), start_date=datetime.datetime(2017,9,20), end_date='2017-09-20', wards=['51', '52', '61', '71', '81', '92', 'IC'],  static=static, test=True)
# pprint(len(oa.drug_list))
# print(len(oa.ptnt_lst))
# print(len(oa.order_list))
# drug_list=oa.filter_drug_list(['INJ', 'NUT'])
# pprint(drug_list.select('약품명(한글)').filter(lambda row: '트라우밀' in row['약품명(한글)']))
# print(len(drug_list))
# order_list = oa.filter_order_list([ '추가', '응급'], '2017-09-28 16:00:00', '2017-09-28 23:59:59')
# print(len(order_list))
# for orderlist in oa.get_order_lists(contexts[0]):
#   parsed = oa.parse_order_list(orderlist)
#   for wards in parsed['grp_by_ward_drug_nm']:
#       print('----collect',wards.WARD)
#       for ward in wards.order_set:
#           print(ward.drug_nm, ward.total_amt_sum)





