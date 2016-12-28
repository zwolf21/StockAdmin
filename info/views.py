from django.shortcuts import render, render_to_response
from django.core.urlresolvers import reverse_lazy
from django.views.generic.edit import FormView
from django.views.generic import ListView, DetailView, CreateView, TemplateView
from django.conf import settings
from django.db.models import Q


import os, sys, json, csv
from datetime import datetime
from json import loads, dumps
from .models import Info

from .forms import CSVForm, InfoCVForm
from .modules.utils import xlDB2DicIter, is_xlfile, DICrawler
from .modules.dicrawler import DrugInfoSearch, get_drug_info


from django.utils.safestring import mark_safe 
from django.http import HttpResponse, HttpResponseRedirect
from StockAdmin.views import LoginRequiredMixin, login_required
from .backup_utils import csv_update, dict2csv, dict2xl
from StockAdmin.services.xlutils import excel_response

# Create your views here.


@login_required
def gen_drug(request):
	if request.is_ajax():
		pk_list = loads(request.GET['pk_list'])
		Info.objects.filter(edi__in=pk_list).update(status='사용중')
		return HttpResponse(dumps(pk_list), content_type='application/json')


@login_required
def unlink_drug(request):
	if request.is_ajax():
		pk_list = loads(request.GET['pk_list'])
		Info.objects.filter(edi__in=pk_list).delete()
		return HttpResponse(dumps(pk_list), content_type='application/json')


class UpdateItemLV(ListView):
	template_name = 'info/update_lv.html'

	def get_queryset(self):
		return Info.objects.filter(status='생성대기')

	def get_context_data(self, **kwargs):
		context = super(UpdateItemLV, self).get_context_data(**kwargs)
		context['form'] = InfoCVForm
		return context


class UpdateItemCV(LoginRequiredMixin ,CreateView):
	model = Info
	form_class = InfoCVForm
	
	def get_success_url(self):
		return self.request.META['HTTP_REFERER']

	def form_valid(self, form):
		# print('form_valid\n*10')
		form.instance.status = '생성대기'
		form.instance.by = self.request.user
		return super(UpdateItemCV, self).form_valid(form)
	
	def form_invalid(self, form):
		return HttpResponseRedirect(self.get_success_url())



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
	filename = 'StockAdmin{}.xlsx'.format(str(timestamp))
	data = excel_response(queryset.values())
	response = HttpResponse(data, content_type='application/vnd.ms-excel')
	response['Content-Disposition'] = 'attachment; filename='+filename
	return response

class IndexTV(TemplateView):
	template_name = "info/drug_info.html"




class InfoCV(LoginRequiredMixin,CreateView):
	model = Info
	template_name = 'info/info_cv.html'
	def get_success_url(self):
		return self.request.META['HTTP_REFERER']


# def autocomplete(request):
# 	if request.is_ajax():
# 		kw = request.GET['term']
# 		iter_rsp = list(filter(None,DICrawler.iter_drug_summary(kw)))
# 		if len(iter_rsp) == 1:
# 			for html in DICrawler.iter_drug_detail(kw):
# 				iter_rsp[0]['pkg_unit'] ,iter_rsp[0]['pkg_amount'] = DICrawler.get_pkg_unit(html)
# 				iter_rsp[0]['narcotic_class'] = DICrawler.get_narcotic_class(html)
# 				# iter_rsp = iter_rsp[0]
		
# 		return HttpResponse(json.dumps(iter_rsp), content_type='application/json')




def autocomplete(request):
	if request.is_ajax():
		kw = request.GET['term']
		dg = DrugInfoSearch(kw)
		iter_rsp = dg.get_search_list()
		for row in iter_rsp:
			row['약가'] = dg._norm_price(row.get('약가'))

		if len(iter_rsp) == 1:
			iter_rsp = list(get_drug_info(kw, '포장·유통단위','주성분코드', result_limit=1))

		return HttpResponse(json.dumps(iter_rsp), content_type='application/json')















