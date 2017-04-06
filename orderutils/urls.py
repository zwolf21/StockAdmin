from django.conf.urls import url

from .views import *

urlpatterns = [
	url(r'^yetrcpts/$', OrderStateLV.as_view(), name='yetrcpts'),
	url(r'^labelcollect/$', LabelCollectLV.as_view(), name='labelcollect'),
]