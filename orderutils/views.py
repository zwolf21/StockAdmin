from datetime import date, timedelta
from django.shortcuts import render

# Create your views here.
from django.views.generic import ListView, FormView, TemplateView
from StockAdmin.services.FKHIS.order_mon import get_order_object_list_test, get_order_object_list
from StockAdmin.services.FKHIS.order_selector import get_label_objet_test, get_label_object

from .forms import DateForm, LabelDateTimeform

class OrderStateLV(ListView):
	template_name = 'orderutils/order_state.html'

	def get_context_data(self, **kwargs):
	    context = super(OrderStateLV, self).get_context_data(**kwargs)
	    context['form'] = DateForm()
	    return context

	def get_queryset(self):
		default_date = date.today() + timedelta(1)
		order_date = self.request.GET.get('date', default_date.strftime('%Y%m%d'))
		queryset = get_order_object_list(order_date)
		# print(queryset)
		return queryset



class LabelCollectLV(ListView):
	template_name = 'orderutils/label_collect.html'

	def get_context_data(self, **kwargs):
		context = super(LabelCollectLV, self).get_context_data(**kwargs)
		context['form'] = LabelDateTimeform()
		return context

	def get_queryset(self):
		collect_date = self.request.GET.get('date')
		start_time = self.request.GET.get('start_t')
		end_time = self.request.GET.get('end_t')
		words = self.request.GET.get('words', '51')
		words = words.split(' ,')
		print(collect_date)
		print(start_time)
		print(end_time)
		print(words)
		queryset = get_label_objet_test(['S', 'P'], words, collect_date, start_time, end_time)
		return queryset
	
	

