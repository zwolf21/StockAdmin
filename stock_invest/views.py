from django.shortcuts import render
from django.core.urlresolvers import reverse_lazy
from django.views.generic import ListView, TemplateView, DetailView, FormView, CreateView, UpdateView, DeleteView
from django.http import HttpResponseRedirect
from djangoslicer import SlicePaginatorMixin

from .models import Invest, InvestItem
from .forms import InvestInlineFormSet, InvestCreateForm
from .modules import gen_invest_list, report_excel_response, sync_op_stock
# Create your views here.


def sync_system_opstock(request):
	if request.method == "POST":
		slug = request.POST['syncSlug']
		sync_op_stock(slug)
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
		invest = gen_invest_list(invest, self.request.POST)
		return super(InvestCV, self).form_valid(form)

class InvestLV(SlicePaginatorMixin, ListView):
	model = Invest
	paginate_by = 10

	def get_context_data(self, **kwargs):
	    context = super(InvestLV, self).get_context_data(**kwargs)
	    context['form'] = InvestCreateForm()
	    return context

last_focus = None
class InvsetItemUV(UpdateView):
	model = Invest
	fields = ('date', 'commiter', )
	template_name = 'stock_invest/invest_item_form.html'

	def get_success_url(self):
		return self.request.META['HTTP_REFERER']

	def get_context_data(self, **kwargs):
		global last_focus
		context = super(InvsetItemUV, self).get_context_data(**kwargs)
		if self.request.POST:
			context['formset'] = InvestInlineFormSet(self.request.POST, instance=self.object)
			last_focus = self.request.POST.get('lastFocus')
		else:
			context['formset'] = InvestInlineFormSet(instance=self.object)

		context['lastFocus'] = last_focus if self.request.path in self.request.META['HTTP_REFERER'] else None
		return context

	def form_valid(self, form):
		context = self.get_context_data()
		formset = context['formset']
		if formset.is_valid():
			for f in formset:
				if f.has_changed():
					if 'DELETE' in f.changed_data:
						f.instance.delete()
					elif ['ORDER'] == f.changed_data:
						continue
					else:
						f.save()
		return super(InvsetItemUV, self).form_valid(form)


class InvestItemPrintDV(DetailView):
	model = Invest
	template_name = 'stock_invest/invest_item_print.html'

class InvestItemDelV(DeleteView):
	model = InvestItem

	def get_success_url(self):
		return self.request.META('HTTP_REFERER')

class InvestDelV(DeleteView):
	model = Invest
	success_url = reverse_lazy('stock_invest:invest-list')


class InvestConfirmUV(UpdateView):
	model = Invest
	success_url = reverse_lazy('stock_invest:invest-list')
	fields = ('commiter', )

