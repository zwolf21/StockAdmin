from datetime import datetime, timedelta, date
from django.db.models import Q, F
from info.models import etc_class_choices

etc_class_set = set(c[0] for c in etc_class_choices)

_today = date.today()

oneday = timedelta(1)
dates = {
	'그글피': _today + oneday*4,
	'ㄱㄱㅍ': _today + oneday*4,
	'글피' : _today + oneday*3,
	'ㄱㅍ' : _today + oneday*3,
	'모래' : _today + oneday*2,
	'ㅁㄹ' : _today + oneday*2,
	'내일' : _today + oneday*1,
	'ㄴㅇ' : _today + oneday*1,
	'오늘' : _today,
	'ㅇㄴ' : _today,
	'어제' : _today - oneday*1,
	'ㅇㅈ' : _today - oneday*1,
	'그제' : _today - oneday*2,
	'ㄱㅈ' : _today - oneday*2,
	'그저께' : _today - oneday*3,
	'ㄱㅈㄲ' : _today - oneday*3,
	'그끄제' : _today - oneday*4,
	'ㄱㄲㅈ' : _today - oneday*4,
	'그끄저께' : _today - oneday*4
}




def get_request_date_range(req):
	start_date = datetime.strptime(req.get('start'), "%Y-%m-%d")
	end_date = datetime.strptime(req.get('end'), "%Y-%m-%d")
	delta_days = (end_date - start_date).days
	return set((start_date + timedelta(i)).date() for i in range(delta_days))

def gen_etc_classQ(etc_cls_kw):
	keywords_set = set(etc_cls_kw.split())
	pos_kw_set = keywords_set & etc_class_set
	min_kw_set = set(kw.strip('-') for kw in keywords_set if kw.startswith('-') or kw.endswith('-')) & etc_class_set
	min_kw_set |= set(kw.strip('빼고') for kw in keywords_set if kw.startswith('빼고') or kw.endswith('빼고')) & etc_class_set
	qry = Q()
	if min_kw_set:
		return Q(drug__etc_class__in=etc_class_set-min_kw_set)
	elif pos_kw_set:
		return Q(drug__etc_class__in=pos_kw_set)
	else:
		return ~Q()


def gen_date_rangeQ(req,date_kw, mode='indate'):
	# or mode='buydate'	
	keywords_set = set(date_kw.split())
	qrydates = keywords_set & set(dates)

	negative_dates = set(kw.strip('-') for kw in keywords_set if kw.startswith('-') or kw.endswith('-')) & set(dates)
	negative_dates |= set(kw.strip('빼고') for kw in keywords_set if kw.startswith('빼고') or kw.endswith('빼고')) & set(dates)

	if negative_dates:
		date_range = get_request_date_range(req) - set(dates[kw] for kw in negative_dates)
		if mode == 'buydate':
			return Q(buy__date__in=date_range)
		else:
			return Q(date__in=date_range)

	if qrydates:
		date_range = [dates[kw] for kw in qrydates]
		if mode == 'buydate':
			return Q(buy__date__in=date_range)
		else:
			return Q(date__in=date_range)
	return ~Q()



def gen_name_containQ(name_kw):
	kw_set = set(name_kw.split())

	ng_keySet = set(kw.replace('-','').replace('빼고','') for kw in kw_set if kw.startswith('-') or kw.startswith('빼고')) - (set(dates)|etc_class_set)
	ps_keySet = set(kw for kw in kw_set if not kw.startswith('-') and not kw.startswith('빼고')) - (set(dates)|etc_class_set)

	if not (ng_keySet | ps_keySet):
		return ~Q()
	
	q = Q()
	for kw in ng_keySet:
		q &= ~Q(drug__name__icontains=kw)

	for kw in ps_keySet:
		q |= Q(drug__name__icontains=kw)
	return q

	

def Qfilter(request, kw, mode='indate'):
	# or mode='buydate'
	return gen_name_containQ(kw)&gen_date_rangeQ(request, kw, mode)&gen_etc_classQ(kw)

