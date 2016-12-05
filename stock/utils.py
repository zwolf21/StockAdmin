from datetime import datetime
from django.db.models import Q
from info.models import etc_class_choices
def get_narcotic_classes(req):
	general = [0] if req.get('general') else []
	narcotic = [1] if req.get('narcotic') else []
	psychotic = [2] if req.get('psychotic') else []
	return general+narcotic+psychotic or []

def get_date_range(req):
	start_date = datetime.strptime(req.get('start'), "%Y-%m-%d")
	end_date = datetime.strptime(req.get('end'), "%Y-%m-%d")
	return start_date, end_date


def gen_etc_classQ(keyword):
	keywords_set = set(keyword.split(','))
	etc_class_set = set(c[0] for c in etc_class_choices)
	min_kw_set = set(kw[1:] for kw in keywords_set if kw.startswith('-'))
	if min_kw_set:
		return(Q(drug__etc_class__in=etc_class_set-min_kw_set))
	else:
		return(Q(drug__etc_class__in=keywords_set))
