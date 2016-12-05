from django.conf.urls import url,patterns, include
from .views import *


urlpatterns = patterns(
	url(r'^$', IndexTV.as_view(), name='index'),
	# url(r'^updateForm/$', DrugInfoFromXlFile.as_view(), name='updatexl'),
	url(r'^create/$', InfoCV.as_view(), name='create'),
	url(r'^createAuto/$', autocomplete, name='create_auto'),
	url(r'^backup/csv/$', backup2csv, name='tocsv'),
	url(r'^backup/excel/$', bacup2excel, name='toexcel'),
	url(r'^csvUpdate/$', CSVUpdateFV.as_view(), name='fromcsv'),
	
)
