from ..models import Buy, BuyItem
from itertools import groupby
from datetime import datetime

# 발주생성, 제약사별 그룹핑
def generate_buy(date, pk_list):
	incart = BuyItem.objects.filter(buy__isnull=True, id__in=pk_list).order_by('drug__account')
	success = []
	for g, items in groupby(incart, lambda x:x.drug.account):
		buy = Buy.objects.create(date=date)
		for item in items:
			buy.buyitem_set.add(item)
			success.append(item.id)
	return success




# account_set = BuyItem.objects.values('drug__account').distinct()


# #[{'drug__account': 1}, {'drug__account': 2}]

# for account in account_set:
# 	buyitem_group = incart.filter(drug__account__id=account['drug__account'])
# 	buyitem_group.update(buy=Buy.objects.create(date=date))

