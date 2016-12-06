from django.shortcuts import render
from django.core.urlresolvers import reverse_lazy, reverse
from django.views.generic import ListView, CreateView, DetailView, FormView, UpdateView, TemplateView, DeleteView
from django.views.generic.dates import DayArchiveView, TodayArchiveView, YearArchiveView, MonthArchiveView, ArchiveIndexView
from django.db.models import F
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import permission_required, login_required
from django.contrib.admin.views.decorators import staff_member_required
from itertools import groupby, chain
from django.forms.models import modelform_factory

from json import loads, dumps

from .modules.dbwork import *
from .models import BuyItem, Buy
from info.models import Info
from .forms import CreateBuyForm, BuyItemAddForm
from stock.models import StockRec
# Create your views here.


from StockAdmin.views import LoginRequiredMixin, PermissionRequiredMixin, Staff_memberRequiredMixin




class TestTV(TemplateView):
	template_name = "buy/test.html"

@login_required
def gen_buy(request):
	if request.is_ajax():
		date = request.GET['date']
		pk_list = loads(request.GET['pk_list'])
		date = datetime.strptime(date, "%Y-%m-%d")
		success_list =  generate_buy(date,pk_list)
		return HttpResponse(dumps(success_list), content_type='application/json')




class BuyLV(ListView):
	model = Buy
	template_name = 'buy/buy_lv.html'


class BuyUV(LoginRequiredMixin, UpdateView):
	model = Buy
	template_name = 'buy/buy_uv.html'

	def get_context_data(self, **kwargs):
		context = super(BuyUV, self).get_context_data(**kwargs)
		context['object_list'] = self.object.buyitem_set.order_by('drug__firm')
		context['slug'] = self.object.slug
		return context


class BuyDV(LoginRequiredMixin, DetailView):
	model = Buy
	template_name = 'buy/buy_dv.html'

	def get_context_data(self, **kwargs):
		context = super(BuyDV, self).get_context_data(**kwargs)
		context['object_list'] = self.object.buyitem_set.order_by('drug__firm')
		if self.object.buyitem_set.first().drug.narcotic_class == 1:
			context['is_narcotic'] = True
		return context

class BuyDVprint(BuyDV):
	template_name = 'buy/etc/buy_print.html'




class BuyItemLV(ListView):
	template_name = 'buy/buyitem_lv.html'

	def get_queryset(self):
		slug = self.request.GET.get('slug')
		return BuyItem.objects.filter(buy__slug=slug).order_by('create_date')

	def get_context_data(self, **kwargs):
		context = super(BuyItemLV, self).get_context_data(**kwargs)
		context['add_form'] =BuyItemAddForm
		context['uptodate_form'] = CreateBuyForm
		return context



class BuyItemCV(LoginRequiredMixin, CreateView):
	model = BuyItem
	fields = ['amount','comment']

	def get_success_url(self):
		return self.request.META['HTTP_REFERER']

	def form_valid(self, form):
		name = self.request.POST.get('name')
		slug = self.request.POST.get('slug')
		
		try:
			drug = Info.objects.get(name=name)
		except:
			return HttpResponseRedirect(self.get_success_url())
		else:
			if slug:
				buy = Buy.objects.get(slug=slug)
				itemset = buy.buyitem_set
				form.instance.buy = buy
				if itemset.count() > 0 and itemset.first().drug.account != drug.account:
					return HttpResponseRedirect(self.get_success_url())			
			else:
				itemset = BuyItem.objects.filter(buy__isnull=True)

			if itemset.filter(drug=drug).exists():
				return HttpResponseRedirect(self.get_success_url())			

			form.instance.drug=drug
			form.instance.by=self.request.user
		return super(BuyItemCV, self).form_valid(form)

	def form_invalid(self, form):
		return HttpResponseRedirect(self.get_success_url())



class BuyItemUV(UpdateView):
	model = BuyItem
	fields = ['amount', 'comment']

	def get_success_url(self):
		return self.request.META['HTTP_REFERER']

	def post(self, request, *args, **kwargs):
		amount = request.POST.get('amount')
		if amount in ['','0']:
			return HttpResponseRedirect(reverse_lazy('buy:buyitem_delete', args=(self.kwargs['pk'],)))
		elif not amount.isdigit(): 
			return HttpResponseRedirect(self.get_success_url())
		return super(BuyItemUV, self).post(request, *args, **kwargs)



class BuyItemDelV(DeleteView):
	model = BuyItem
	
	def get_success_url(self):
		return self.request.META['HTTP_REFERER']

	def get(self, request, *args, **kwargs):
		return self.post(request, *args, **kwargs)


def buy_commit(request, slug):
	if request.method == 'GET':
		if request.user.is_staff or request.user.is_superuser:
			try:
				buy = Buy.objects.get(slug=slug, commiter__isnull=True)
			except Buy.DoesNotExist:
				return HttpResponseRedirect(reverse_lazy('buy:buy_detail', args=(slug,)))
			else:
				buy.commiter = request.user
				buy.save()
	return HttpResponseRedirect(reverse_lazy('buy:buy_list'))



class NarcoticLV(ListView):
	model = BuyItem
	template_name = 'buy/etc/narcotic_buy.html'


	def get_context_data(self, **kwargs):
		context = super(NarcoticLV, self).get_context_data(**kwargs)
		query_set =  BuyItem.objects.filter(buy__slug=self.kwargs['slug'], drug__narcotic_class=1, buy__commiter__isnull=False)
		max_Nrow = 15
		if query_set.count() < max_Nrow:
			padding_list = [''] * (max_Nrow - query_set.count())
		context['object_list'] = query_set
		context['padding'] = padding_list
		return context


def roll_back2cart(request, slug):
	try:
		buy = Buy.objects.get(slug=slug)
	except:
		return HttpResponseRedirect(request.META['HTTP_REFERER'])
	else:
		buy.buyitem_set.update(buy=None)
		buy.delete()
		return HttpResponseRedirect(reverse('buy:buy_list'))




























