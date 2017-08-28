from django.shortcuts import render
from django.core.urlresolvers import reverse_lazy, reverse
from django.views.generic import ListView, CreateView, DetailView, FormView, TemplateView, UpdateView, DeleteView
from django.views.generic.dates import MonthArchiveView
from django.db.models import F, Sum, Q
from django.http import HttpResponseRedirect, HttpResponse
from django.core.mail import EmailMessage
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from djangoslicer import SlicePaginatorMixin

from datetime import datetime, timedelta, date
from itertools import groupby, filterfalse
from collections import OrderedDict
import os, re

# Create your views here.
from django.conf import settings
from info.forms import InfoCVForm
from .models import StockRec
from buy.models import BuyItem
from StockAdmin.serializers import *
from .forms import DateRangeForm, StockRecAmountForm
from .utils import get_narcotic_classes, get_date_range
from .kwQutils import gen_etc_classQ, gen_date_rangeQ, gen_name_containQ, Qfilter
from StockAdmin.views import LoginRequiredMixin
from StockAdmin.services.xlutils import excel_output, excel_gmail_send


class StockRecCV(CreateView):
	model = StockRec

	def post(self, request):
		# print(request.POST)
		for key in filter(lambda x: x.endswith('price'), request.POST):
			buyitem_pk = int(key[:-5])
			price = int(request.POST[key])
			# print(buyitem_pk, price)
			buyitem = BuyItem.objects.get(pk=buyitem_pk)
			if buyitem.drug.price != price:
				drug_pk = buyitem.drug.pk
				Info.objects.filter(pk=drug_pk).update(price=price)
				


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
		context['info_form'] = InfoCVForm
		return context

class StockIncompleteLVprint(StockIncompleteLV):
	template_name = 'etc/incomplete_print.html'

	def get_queryset(self):
		qryset = super(StockIncompleteLVprint, self).get_queryset()
		return sorted(qryset, key=lambda item: item.buy.slug)


class StockIncompleteLVmail(LoginRequiredMixin, StockIncompleteLV):
	template_name = 'etc/incomplete_print.html'

	def get(self, request, *args, **kwargs):
		
		start_date = request.GET['start'].replace('-','')
		end_date = request.GET['end'].replace('-','')
		account_id = int(request.GET.get('account'))
		object_list = list(filter(lambda obj: obj.drug.account.id == account_id, self.get_queryset()))

		xl_template = [
			OrderedDict((
				('발주번호', obj.buy), ('보험코드', obj.drug.edi), ('제약회사', obj.drug.firm), ('약품명', obj.drug), 
				('발주수량', obj.amount), ('기입고수량', obj.stockin_amount), ('미입고분', obj.incomplete_amount)
			)) 
			for obj in object_list
		]
		
		if not xl_template:
			return HttpResponseRedirect(request.META['HTTP_REFERER'])

		
		mail_to = object_list[0].drug.account.email
		account_name = object_list[0].drug.account.name
		mail_content = request.GET.get('content', '미입고현황(발주일기준)')
		now = datetime.now().strftime("%Y-%m-%d %H:%I")
		filename = '{} {}~{}미입고현황.xlsx'.format(account_name, start_date, end_date)
		data = excel_output(xl_template)
		subject = '{} {} 미입고현황'.format(account_name, now)
		# excel_gmail_send(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD, [mail_to], subject, mail_content, {filename: data})
		email = EmailMessage('{} {} 미입고현황'.format(account_name, now), mail_content, to=[mail_to])
		email.attach(filename, data, 'application/vnd.ms-excel')
		try:
			email.send(fail_silently=False)
		except SMTPAuthenticationError:
			HttpResponse('<h2>메일전송 실패</h2>')
		else:		
			return HttpResponseRedirect(request.META['HTTP_REFERER'])
		


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


class StockInPLV(SlicePaginatorMixin, ListView):
	model = StockRec
	template_name = 'stock/period_plv_list.html'
	paginate_by = 25

	def get_queryset(self):
		name = self.request.GET.get('name')

		queryset = StockRec.objects.filter(
				Q(buyitem__buy__slug__contains=name)|Q(date__contains=name)|Qfilter(self.request.GET, name,'indate'),
				date__range=get_date_range(self.request.GET), 
				amount__gt=0, 
				drug__narcotic_class__in=get_narcotic_classes(self.request.GET)
			)
		self.queryset = queryset
		return queryset

	def get_context_data(self, **kwargs):
		context = super(StockInPLV, self).get_context_data(**kwargs)
		context['form'] = DateRangeForm(self.request.GET)
		total_price = 0

		for s in self.queryset:
			total_price+=s.total_price
		context['total_price'] = total_price
		context['total_count'] = self.queryset.count()

		get_full_path = self.request.get_full_path()
		reg_pgprm = re.compile('&*page=\d*')
		get_full_path = reg_pgprm.sub('', get_full_path)
		context['request'] = {'get_full_path':get_full_path}

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



def period2excel(request):
	if request.method == 'GET':
		name = request.GET.get('name')
		queryset = StockRec.objects.filter(
				Q(buyitem__buy__slug__contains=name)|Q(date__contains=name)|Qfilter(request.GET, name,'indate'),
				date__range=get_date_range(request.GET), 
				amount__gt=0, 
				drug__narcotic_class__in=get_narcotic_classes(request.GET)
			)
		
		xl_template = [OrderedDict((('입고일자', obj.date), ('발주번호', obj.buyitem.buy.slug), ('거래처', obj.drug.account.name),('보험코드', obj.drug.edi) ,('약품명', obj.drug.name),('발주수량',obj.buyitem.amount), ('입고단가', obj.drug.price), ('입고수량', obj.amount), ('입고금액', obj.drug.price*obj.amount))) for obj in queryset]
		start_date = request.GET['start'].replace('-','')
		end_date = request.GET['end'].replace('-','')
		filename = '{}~{}Stock.xlsx'.format(start_date, end_date)
		data = excel_output(xl_template)
		response = HttpResponse(data, content_type='application/vnd.ms-excel')
		response['Content-Disposition'] = 'attachment; filename='+filename
		return response





# ________________________________________________API Modules________________________________________________


class BuyItemIncompleteAPITV(TemplateView):
    template_name = "stock/angular/incomplete_lv.html"



class BuyItemIncompleteAPILV(ListAPIView):
	serializer_class = ListBuyItemIncomplete

	def list(self, request, *args, **kwargs):
		# req = request.query_params
		# name = req.get('name')
		queryset = BuyItem.objects.all()[:500]
		# serializer = self.get_serializer(filter(lambda item: not item.is_completed, queryset), many=True)
		serializer = self.get_serializer(queryset, many=True)
		return Response(serializer.data)	



class StockRecStockinAPITV(TemplateView):
	template_name = 'stock/angular/period_plv_list.html'

	def get_context_data(self, **kwargs):
		context = super(self.__class__, self).get_context_data(**kwargs)
		context['form'] = DateRangeForm
		return context


class StockRecStockinAPVLV(ListAPIView):
	serializer_class = ListStockRecSerializer

	def list(self, request, *args, **kwargs):
		queryset = StockRec.objects.all()[:500]
		serializer = self.get_serializer(queryset, many=True)
		return Response(serializer.data)




























