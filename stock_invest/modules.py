from .models import Invest, InvestItem
from info.models import Info

def gen_invest_list(invest):
	invest_items = Info.objects.filter(invest_class__in=['경구', '마약류', '주사' ,'냉장', '외용'])
	for drug in invest_items:
		item = InvestItem.objects.create(drug=drug, invest=invest)
	return invest

