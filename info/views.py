from django.shortcuts import render, render_to_response
from django.core.urlresolvers import reverse_lazy
from django.views.generic.edit import FormView
from django.views.generic import ListView, DetailView, CreateView, TemplateView
from django.conf import settings
from django.db.models import Q


import os, sys, json, csv
from datetime import datetime
from .models import Info

from .forms import CSVForm
from .modules.utils import xlDB2DicIter, is_xlfile, DICrawler


from django.utils.safestring import mark_safe 
from django.http import HttpResponse
from StockAdmin.views import LoginRequiredMixin
from .backup_utils import csv_update, dict2csv, dict2xl


# Create your views here.




class CSVUpdateFV(LoginRequiredMixin ,FormView):
	form_class = CSVForm
	template_name = 'info/csv_update.html'
	def form_valid(self, form):
		context = csv_update(self.request)
		prepudates =context['preupdated']
		updates = context['updated']
	
		if updates:
			pvt = updates[0].keys()
			for pre, up in zip(prepudates, updates):
				for key in pvt:
					up_val = str(up.get(key) or "")
					pre_val = str(pre.get(key) or "")
					if pre_val != up_val:
						up[key] = mark_safe('<strong style="color:green;">' + up_val + '<strong>')
						pre[key] = mark_safe('<strong style="color:red;">' + pre_val + '<strong>')

		return render_to_response('info/update_result.html', context)


def backup2csv(request):
	queryset = Info.objects.all()
	timestamp = datetime.now().strftime('%Y%m%d%H%I%S')
	filename = 'StockAdmin{}.csv'.format(str(timestamp))
	return dict2csv(queryset, filename)
	
	 
def bacup2excel(request):
	queryset = Info.objects.all()
	timestamp = datetime.now().strftime('%Y%m%d%H%I%S')
	filename = 'StockAdmin{}.xls'.format(str(timestamp))
	return dict2xl(queryset,filename)

class IndexTV(TemplateView):
	template_name = "info/drug_info.html"




class InfoCV(LoginRequiredMixin,CreateView):
	model = Info
	template_name = 'info/info_cv.html'
	def get_success_url(self):
		return self.request.META['HTTP_REFERER']


def autocomplete(request):
	if request.is_ajax():
		kw = request.GET['term']
		iter_rsp = list(filter(None,DICrawler.iter_drug_summary(kw)))[:15]
		if len(iter_rsp) == 1:
			for html in DICrawler.iter_drug_detail(kw):
				iter_rsp[0]['pkg_unit'] ,iter_rsp[0]['pkg_amount'] = DICrawler.get_pkg_unit(html)
				iter_rsp[0]['narcotic_class'] = DICrawler.get_narcotic_class(html)
				iter_rsp = iter_rsp[0]
		return HttpResponse(json.dumps(iter_rsp), content_type='application/json')





	















