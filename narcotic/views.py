from datetime import date, datetime

from django.shortcuts import render, render_to_response
from django.views.generic import FormView, TemplateView, ListView
from django.http import HttpResponse


# Create your views here.
from dateutil import parser

from .modules.FKHIS.opremain import get_opremain_contents, get_opremain_contents_test
from .modules.FKHIS.opstock import get_opstock_object_list, get_opstock_object_list_test
from .forms import DataRangeForm, OpSelectForm


class OpRemainDownloadFV(FormView):
	template_name = 'narcotic/opremain.html'
	form_class = DataRangeForm

	def form_valid(self, form):
		start = self.request.POST.get('start')
		end = self.request.POST.get('end')
		content = get_opremain_contents(start, end)
		fname = '{}~{}OpRemain.xlsx'.format(str(start), str(end))
		response = HttpResponse(content, content_type='application/vnd.ms-excel')
		response['Content-Disposition'] = 'attachment; filename='+fname
		return response

class OpRemainFV(FormView):
	template_name = 'narcotic/opremain.html'
	form_class = DataRangeForm

	def form_valid(self, form):
		start = self.request.POST.get('start')
		end = self.request.POST.get('end')
		opremain_list, opremain_grouped = get_opremain_contents(start, end, to_queryset=True)
		context = self.get_context_data()
		context['object_list'] = opremain_list
		context['object_grouped_list'] = opremain_grouped
		context['form'] = DataRangeForm(self.request.POST)
		context['start_date'] = start
		context['end_date'] = end
		# print(opremain_list)
		return render_to_response(self.template_name, context)





class OpStockFV(FormView):
	template_name = 'narcotic/opstock.html'
	form_class = OpSelectForm

	def get_context_data(self, **kwargs):
		context = super(OpStockFV, self).get_context_data(**kwargs)
		today = date.today().strftime('%Y-%m-%d')
		today0 = date.today().strftime('%Y%m%d')
		now = datetime.now().strftime('%H:%I:%S')
		object_list = get_opstock_object_list(today0)
		context['today'] = today
		context['now'] = now
		context['object_list'] = object_list
		# print(object_list)
		return context

	def form_valid(self, form):
		psy = self.request.POST.get('psychotic')
		narc = self.request.POST.get('narcotic')
		date = self.request.POST.get('date')
		today = date.today().strftime('%Y-%m-%d')
		object_list = get_opstock_object_list(today, psy, narc)
		context = self.get_context_data()
		context['object_list'] = object_list
		return render_to_response('narcotic/opstock.html', context)


class OpStockLV(ListView):
	template_name = 'narcotic/opstock.html'

	def get_context_data(self, **kwargs):
		context = super(OpStockLV, self).get_context_data(**kwargs)
		context['form'] = OpSelectForm(self.request.GET) if self.request.GET else OpSelectForm()
		# context['today'] = date.today().strftime('%Y-%m-%d')
		return context

	def get_queryset(self):
		psy = self.request.GET.get('psychotic', False)
		narc = self.request.GET.get('narcotic', False)
		today = self.request.GET.get('date', date.today().strftime('%Y-%m-%d'))
		return get_opstock_object_list(today, psy, narc)



class OpStockPrintTV(OpStockLV):
	template_name = 'narcotic/etc/opstock_print.html'

	def get_queryset(self):
		queryset = super(OpStockPrintTV, self).get_queryset()
		return queryset