from django.shortcuts import render
from django.views.generic import ListView, CreateView, DeleteView
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponse, HttpResponseRedirect

import json
from .models import OcsFile
from .utils import is_excel_file, get_compare, get_item_count, is_ocsxl, make_description, transfrom_updated_result
from StockAdmin.services.xlutils import excel_file_response
from StockAdmin.views import LoginRequiredMixin


# Create your views here.

class OcsFileCV(LoginRequiredMixin, CreateView):
	model = OcsFile
	fields = 'excel', 'description',
	success_url = reverse_lazy('ocsxl:list')
	template_name = 'ocsxl/ocsfile_create.html'

	def form_valid(self, form):
		excel = form.cleaned_data['excel']
		if not is_excel_file(excel.name):
			return HttpResponse('<h1>올바른 형식(.xls, .xlsx)의 파일을 넣으시오.(현재 파일: {})</h1>'.format(excel.name)) 

		excel_contents = excel.read()

		if not is_ocsxl(excel_contents):
			return HttpResponse('<h1>후지스 OCS 마스터 엑셀 파일인지 확인하십시오.</h1>')

		items_count = get_item_count(excel_contents)

		if items_count == 0:
			return HttpResponse('<h1>약품마스터 파일이긴 하나 품목 건수가 1도 없습니다.</h1>') 

		form.instance.description = make_description(items_count)
		return super(OcsFileCV, self).form_valid(form)


class OcsFileLV(ListView):
	model = OcsFile


class OcsFileDelV(DeleteView):
	model = OcsFile
	

def ocsfiles_delete(request):
	if request.method == "POST":
		pk_list = request.POST['reportList'].split(',')
		OcsFile.objects.filter(pk__in=pk_list).delete()
		return HttpResponseRedirect(reverse_lazy('ocsxl:list'))


def ocsfiles_compare(request):
	if request.method == "POST":
		pk_list = request.POST['reportList'].split(',')
		if len(pk_list) == 2:
			context = {}
			before, after = OcsFile.objects.filter(pk__in=pk_list).order_by('created')
			before_created = before.created.strftime("%Y%m%d")
			after_created = after.created.strftime("%Y%m%d")
			context['pk_list'] = ','.join(pk_list)				
			context['changes'] = get_compare(before.excel.read(), after.excel.read())
			context['updated'] = transfrom_updated_result(context['changes'].updated)
			context['title'] = "약품정보 변경사항(전:{} ~ 후:{})".format(before.filename, after.filename)
			return render(request, 'ocsxl/compare_result.html', context)


def ocsfiles_compare_excel_response(request):
	if request.method == "POST":
		pk_list = request.POST['reportList'].split(',')
		if len(pk_list) == 2:
			print(pk_list)
			context = {}
			before, after = OcsFile.objects.filter(pk__in=pk_list).order_by('created')
			before_created = before.created.strftime("%Y%m%d")
			after_created = after.created.strftime("%Y%m%d")
			filename = "OCS Changes {}~{}.xlsx".format(before.filename, after.filename)
			contents = get_compare(before.excel.read(), after.excel.read(), to_context=False)
			return excel_file_response(contents, filename)





					



