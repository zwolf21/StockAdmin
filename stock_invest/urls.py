from django.conf.urls import url,patterns, include
from .views import *


urlpatterns = patterns('',
	url(r'^list/$', InvestLV.as_view(), name='invest-list'),
	url(r'^create/$', InvestCV.as_view(), name='invest-create'),
	url(r'^update/(?P<slug>[-\w]+)/$', InvsetItemUV.as_view(), name='invest-update'),
)
