from django.conf.urls import url

from .views import *

urlpatterns = [
	url(r'^create/batch/$', CollectBatchFormView.as_view(), name='create-batch'),
	url(r'^create/(?P<kind>LABEL|NUT|INJ)/$', CollectFormView.as_view(), name='create'),
	url(r'^detail/(?P<slug>[\w\d-]+)/$', CollectDetailView.as_view(), name='detail'),
	url(r'^delete/$', clear, name='clear'),
	url(r'^delete/(?P<slug>[\w\d-]+)/$', CollectDeleteView.as_view(), name='delete'),
	url(r'^update/plusminus/(?P<kind>NUT|INJ)/$', ConfigFormView.as_view(), name='update-plusminus'),

	url(r'^generate-form/$', generate_form_initial, name='gen-time'),
	url(r'^merge/$', CollectMergeFormView.as_view(), name='merge')
]
