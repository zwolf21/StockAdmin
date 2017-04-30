from django.shortcuts import render
from django.core.urlresolvers import reverse_lazy
from django.views.generic import ListView, TemplateView, DetailView, FormView, CreateView, UpdateView
from django.http import HttpResponseRedirect

from .models import Invest, InvestItem
from .forms import InvestInlineFormSet, InvestCreateForm
from .modules import gen_invest_list, report_excel_response, sync_op_stock
# Create your views here.


def sync_system_opstock(request):
	if request.method == "POST":
		slug = request.POST['syncSlug']
		# sync_op_stock(slug)
		print(slug)
		return HttpResponseRedirect(request.META['HTTP_REFERER'])


def excel_invest_report(request):
	if request.method == "POST":
		slugs = request.POST['reportList']
		return report_excel_response(slugs.split(','))


class InvestCV(CreateView):
	model = Invest
	fields = ('date', )
	template_name = 'stock_invest/invest_create_form.html'
	success_url = reverse_lazy('stock_invest:invest-list')

	def form_valid(self, form):
		invest = form.save()
		gen_invest_list(form.instance, self.request.POST)
		return super(InvestCV, self).form_valid(form)

class InvestLV(ListView):
	model = Invest

	def get_context_data(self, **kwargs):
	    context = super(InvestLV, self).get_context_data(**kwargs)
	    context['form'] = InvestCreateForm()
	    return context


class InvsetItemUV(UpdateView):
	model = Invest
	fields = ('date', )
	template_name = 'stock_invest/invest_item_form.html'

	def get_success_url(self):
		return self.request.META['HTTP_REFERER']

	def get_context_data(self, **kwargs):
		context = super(InvsetItemUV, self).get_context_data(**kwargs)
		# context['formset']  = InvestInlineFormSet(self.request.POST, instance=self.object)
		if self.request.POST:
			context['formset'] = InvestInlineFormSet(self.request.POST or None, instance=self.object)
		else:
			context['formset'] = InvestInlineFormSet(instance=self.object)
		return context

	def form_valid(self, form):
		context = self.get_context_data()
		formset = context['formset']
		if formset.is_valid():
			for f in formset:
				if f.has_changed():
					f.save()
		return super(InvsetItemUV, self).form_valid(form)


