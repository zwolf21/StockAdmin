from django.conf.urls import url,patterns, include
from .views import *


urlpatterns = patterns('',
	url(r'^list/$', InvestLV.as_view(), name='invest-list'),
	url(r'^create/$', InvestCV.as_view(), name='invest-create'),
	url(r'^update/(?P<slug>[-\w]+)/$', InvsetItemUV.as_view(), name='invest-update'),
	url(r'^delete/(?P<slug>[-\w]+)/$', InvestDelV.as_view(), name='invest-delete'),
	url(r'^confirm/(?P<slug>[-\w]+)/$', InvestConfirmUV.as_view(), name='invest-confirm'),

	url(r'^delete/item/(?P<pk>\d+)/$', InvestItemDelV.as_view(), name='invest-item-delete'),
	url(r'^item/print/(?P<slug>[-\w]+)/$', InvestItemPrintDV.as_view(), name='invest-item-print'),

	url(r'^get-excel-report/', excel_invest_report, name='invest-excel-report'),
	url(r'^sync-system-opstock/', sync_system_opstock, name='invest-system-opsync')
)
