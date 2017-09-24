from django.conf.urls import url

from .views import *

# urlpatterns = [
# 	url(r'^create/$', CollectFormView.as_view(), name='create'),
# 	url(r'^clear/$', clear_collect, name='clear'),
# 	url(r'^delete/(?P<slug>[\w\d-]+)/$', collect_delete, name='delete'),
# 	url(r'^detail/(?P<slug>[\w\d-]+)/$', collect_detail, name='detail'),
# 	# url(r'^create/(?P<kind>\w+)$', CollectCreateView.as_view(), name='create')
# ]

urlpatterns = [
	url(r'^create/(?P<kind>LABEL|NUT|INJ)/$', CollectFormView.as_view(), name='create'),
	url(r'^detail/(?P<slug>[\w\d-]+)/$', CollectDetailView.as_view(), name='detail'),
	url(r'^delete/$', clear, name='clear'),
	url(r'^delete/(?P<slug>[\w\d-]+)/$', CollectDeleteView.as_view(), name='delete'),
	url(r'^update/plusminus/(?P<kind>NUT|INJ)/$', StaticFormView.as_view(), name='update-plusminus'),
	# url(r'^update/excludes/(?P<kind>LABEL|NUT|INJ)/$', name='update-excludes')
]