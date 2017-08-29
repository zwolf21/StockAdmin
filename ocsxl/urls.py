from django.conf.urls import url, patterns
from .views import *

urlpatterns = patterns('',

	# views
	url(r'^$', OcsFileLV.as_view(), name='list'),
	url(r'^add/$', OcsFileCV.as_view(), name='create'),

	# functions	
	url(r'^delete/$', ocsfiles_delete, name='delete'),
	url(r'^compare/$', ocsfiles_compare, name='compare'),
	url(r'^compare/download/$', ocsfiles_compare_excel_response, name='compare-download'),

)

















