from django.conf.urls import url

from .views import *

urlpatterns = [
	url(r'^compare/$', GosiFileFormView.as_view(), name='compare'),
	url(r'^compare/list/$', gosi_listview, name='compare-list'),
]