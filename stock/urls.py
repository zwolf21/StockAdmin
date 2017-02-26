from django.conf.urls import url, patterns

from .views import *
urlpatterns = patterns('',
	
	url(r'^showPeriod/$', StockInPTV.as_view(), name='show_period'),
	url(r'^showPeriod/result/list$', StockInPLV.as_view(), name='show_period_result_list'),
	url(r'^showPeriod/result/ano$', StockInPLVano.as_view(), name='show_period_result_ano'),

	url(r'^showIncomplete/$', StockIncompleteTV.as_view(), name='show_incomplete'),
	url(r'^showIncomplete/result/$', StockIncompleteLV.as_view(), name='show_incomplete_list'),
	url(r'^showIncomplete/print/$', StockIncompleteLVprint.as_view(), name='show_incomplete_print'),
	url(r'^showIncomplete/mail/$', StockIncompleteLVmail.as_view(), name='sho_incomplete_mail'),
	url(r'^in/$', StockRecCV.as_view(), name='stockin'),
	url(r'^end/$', StockInEndLV.as_view(), name='end'),
	url(r'^end/rollback/(?P<pk>\d+)/$', EndRollBack.as_view(), name='rollback'),
	url(r'^delete/(?P<pk>\d+)/$', StockInDelV.as_view(), name='delete'),

	url(r'^periodExcel/$', period2excel, name='period-excel'),
	


	# api-modules
	url(r'^showIncomplete/api/index/$', BuyItemIncompleteAPITV.as_view(), name='show_incomplete_tv-api'),
	url(r'^showIncomplete/api/$', BuyItemIncompleteAPILV.as_view(), name='show_incomplete-api'),

	url(r'^showStockin/api/index/$', StockRecStockinAPITV.as_view(), name='show_stockin_tv-api'),
	url(r'^showStockin/api/$', StockRecStockinAPVLV.as_view(), name='show_stockin-api'),

)
