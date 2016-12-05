from django.shortcuts import render
from django.core.urlresolvers import reverse_lazy, reverse
from django.views.generic import ListView, CreateView, DetailView, FormView, TemplateView, UpdateView, DeleteView
from django.views.generic.dates import MonthArchiveView
from django.db.models import F, Sum, Q
from django.http import HttpResponseRedirect

from datetime import datetime, timedelta, date
from itertools import groupby

# Create your views here.
from .models import StockRec
from buy.models import BuyItem
from .forms import DateRangeForm, StockRecAmountForm
from .utils import get_narcotic_classes, get_date_range
from .kwQutils import gen_etc_classQ, gen_date_rangeQ, gen_name_containQ, Qfilter
from StockAdmin.views import LoginRequiredMixin


class StockRecCV(CreateView):
	model = StockRec

	def post(self, request):
		for key in filter(lambda key:key.isdigit(), request.POST):
			amount = request.POST[key]
			end = True if request.POST.get(key+'end')=='on' else False
			if not amount and not end:
				continue
			item = BuyItem.objects.get(pk=int(key))
			if amount:
				StockRec.objects.create(buyitem=item, amount=int(amount), date=request.POST['indate'])
			elif end:
				item.end = end
				item.save()
		return HttpResponseRedirect(request.META['HTTP_REFERER'])		
		


class StockIncompleteTV(TemplateView):
	template_name = 'stock/incomplete_tv.html'

	def get_context_data(self, **kwargs):
		context = super(StockIncompleteTV, self).get_context_data(**kwargs)
		context['form'] = DateRangeForm
		return context



class StockIncompleteLV(ListView):
	template_name = 'stock/incomplete_lv.html'

	def get_queryset(self):
		name = self.request.GET.get('name')
		queryset = BuyItem.objects.filter_by_date(*get_date_range(self.request.GET))
		queryset =  queryset.filter(
			Q(drug__name__icontains=name)|Q(buy__slug__icontains=name)|Qfilter(self.request.GET, name,'buydate'),
			drug__narcotic_class__in=get_narcotic_classes(self.request.GET),
			buy__commiter__isnull=False
		).order_by('drug__firm')
	
		return filter(lambda item: not item.is_completed, queryset)

	def get_context_data(self, **kwargs):
		context = super(StockIncompleteLV, self).get_context_data(**kwargs)
		context['form'] = DateRangeForm(self.request.GET)
		context['amount_form'] = StockRecAmountForm
		return context



class StockInEndLV(ListView):
	template_name = 'stock/end_lv.html'

	def get_queryset(self):
		return BuyItem.objects.filter(
			end=True, 
			buy__date__range=get_date_range(self.request.GET),
			drug__narcotic_class__in=get_narcotic_classes(self.request.GET)
			)

	def get_context_data(self, **kwargs):
		context = super(StockInEndLV, self).get_context_data(**kwargs)
		context['form'] = DateRangeForm(self.request.GET)
		return context


class EndRollBack(UpdateView):
	model = BuyItem
	fields = ['id']
	def get_success_url(self):
		return self.request.META['HTTP_REFERER']


	def form_valid(self, form):
		form.instance.end = False
		return super(EndRollBack, self).form_valid(form)



class StockInPTV(TemplateView):
	template_name = 'stock/period_tv.html'

	def get_context_data(self, **kwargs):
		context = super(StockInPTV, self).get_context_data(**kwargs)
		context['form'] = DateRangeForm
		return context


class StockInPLV(ListView):
	model = StockRec
	template_name = 'stock/period_plv_list.html'

	def get_queryset(self):
		name = self.request.GET.get('name')
		queryset = StockRec.objects.filter(
				Q(buyitem__buy__slug__contains=name)|Q(date__contains=name)|Qfilter(self.request.GET, name,'indate'),
				date__range=get_date_range(self.request.GET), 
				amount__gt=0, 
				drug__narcotic_class__in=get_narcotic_classes(self.request.GET)
			)
		return queryset

	def get_context_data(self, **kwargs):
		context = super(StockInPLV, self).get_context_data(**kwargs)
		context['form'] = DateRangeForm(self.request.GET)
		total_price = 0
		for s in self.get_queryset():
			total_price+=s.total_price
		context['total_price'] = total_price
		return context


class StockInPLVano(StockInPLV):
	template_name = 'stock/period_plv_ano.html'

	def get_context_data(self, **kwargs):
		context = super(StockInPLVano, self).get_context_data(**kwargs)
		queryset = self.get_queryset().order_by('drug')
		queryset = [{'drug':g ,'total_amount':sum(e.amount for e in l)} for g, l in groupby(queryset, lambda x: x.drug)]
		context['object_list'] = queryset
		context['total_price'] = sum(e['drug'].price * e['total_amount'] for e in queryset)
		return context


class StockInDelV(LoginRequiredMixin ,DeleteView):
	model = StockRec

	def get_success_url(self):
		return self.request.META['HTTP_REFERER']






























