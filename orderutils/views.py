from datetime import date, timedelta
from django.shortcuts import render

# Create your views here.
from django.views.generic import ListView, FormView, TemplateView
from StockAdmin.services.FKHIS.order_mon import get_order_object_list_test, get_order_object_list
from StockAdmin.services.FKHIS.order_selector import get_label_object_test, get_label_object

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
		context['form'] = LabelDateTimeform(self.request.GET or None)
		return context

	def get_queryset(self):
		default_today = date.today() + timedelta(0)
		default_tommorow = date.today() + timedelta(1)
		ord_start_date = self.request.GET.get('ord_start_date', default_tommorow.strftime('%Y-%m-%d'))
		ord_end_date = self.request.GET.get('ord_end_date', default_tommorow.strftime('%Y-%m-%d'))
		start_time = self.request.GET.get('start_t', str(default_today))
		end_time = self.request.GET.get('end_t', str(default_tommorow))
		ward = self.request.GET.get('ward')

		if not ward:
			return []
		ward = ward.split(", ")

		queryset = get_label_object_test(['S','P'], ward, ord_start_date, ord_end_date, start_time, end_time)
		return queryset


	
	

