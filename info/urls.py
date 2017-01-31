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
	url(r'^update/view/$', UpdateItemLV.as_view(), name='update_lv'),
	url(r'^update/add/$', UpdateItemCV.as_view(), name='update_cv'),
	url(r'^gen/$', gen_drug, name='drug_gen'),
	url(r'^unlink/$', unlink_drug, name='drug_unlink'),
	url(r'^predict_week', PredictWeekLV.as_view(), name='predict_week')
	
)
