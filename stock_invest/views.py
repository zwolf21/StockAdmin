from django.shortcuts import render
from django.core.urlresolvers import reverse_lazy
from django.views.generic import ListView, TemplateView, DetailView, FormView, CreateView, UpdateView

from .models import Invest, InvestItem
from .forms import InvestInlineFormSet
from .modules import gen_invest_list
# Create your views here.

class InvestCV(CreateView):
	model = Invest
	fields = ('date', )
	template_name = 'stock_invest/invest_form.html'
	success_url = reverse_lazy('stock_invest:invest-list')

	def form_valid(self, form):
		invest = form.save()

		gen_invest_list(form.instance)
		return super(InvestCV, self).form_valid(form)

class InvestLV(ListView):
	model = Invest


class InvsetItemUV(UpdateView):
	model = Invest
	fields = ('date', )
	template_name = 'stock_invest/invest_item_form.html'

	def get_success_url(self):
		return self.request.META['HTTP_REFERER']

	def get_context_data(self, **kwargs):
		context = super(InvsetItemUV, self).get_context_data(**kwargs)
		if self.request.POST:
			context['formset'] = InvestInlineFormSet(self.request.POST, instance=self.object)
		else:
			context['formset'] = InvestInlineFormSet(instance=self.object)
		return context

	def form_valid(self, form):
		context = self.get_context_data()
		formset = context['formset']
		if formset.is_valid():
			formset.save()
		return super(InvsetItemUV, self).form_valid(form)