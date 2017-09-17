from django.conf.urls import url

from .views import *

urlpatterns = [
	url(r'^create/$', CollectCreateView.as_view(), name='create'),
	url(r'^delete/(?P<slug>[\w\d-]+)/$', collect_delete, name='delete'),
	url(r'^detail/(?P<slug>[\w\d-]+)/$', collect_detail, name='detail'),
	# url(r'^create/(?P<kind>\w+)$', CollectCreateView.as_view(), name='create')
]
