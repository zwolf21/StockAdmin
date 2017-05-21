from django.conf.urls import url

from .views import *

urlpatterns = [
	url(r'^yetrcpts/$', OrderStateLV.as_view(), name='yetrcpts'),
	url(r'^labelcollect/$', LabelCollectFV.as_view(), name='labelcollect'),
	url(r'^labelcollect/(?P<ord_tp>정기|추가|응급|퇴원|항암)/(?P<date>[\d-]{10})/(?P<seq>\d+)/$', LabelCollectFV.as_view(), name='labelcollect-history')
]