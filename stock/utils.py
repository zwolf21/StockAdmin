from datetime import datetime, timedelta, date
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

