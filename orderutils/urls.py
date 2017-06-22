from django.conf.urls import url

from .views import *

urlpatterns = [
	url(r'^yetrcpts/$', OrderStateLV.as_view(), name='yetrcpts'),
	url(r'^labelcollect/$', LabelCollectFV.as_view(), name='labelcollect'),
	url(r'^labelcollect/(?P<ord_tp>st|ex|em|op|ch)/(?P<date>[\d-]{10})/(?P<seq>\d+)/$', LabelCollectFV.as_view(), name='labelcollect-history'),
	url(r'^labelcollect/history-clear/$', label_history_clear, name='labelcollect-history-clear'),
	url(r'^labelcollect/(?P<ord_tp>st|ex|em|op|ch)/(?P<date>[\d-]{10})/(?P<seq>\d+)/delete/$', label_history_clear_one, name='labelcollect-history-clear-one'),	
]