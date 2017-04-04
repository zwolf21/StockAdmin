from datetime import date, timedelta
from django.shortcuts import render

# Create your views here.
from django.views.generic import ListView, FormView, TemplateView
from StockAdmin.services.FKHIS.order_mon import get_order_object_list_test, get_order_object_list

from .forms import DateForm

class OrderStateLV(ListView):
	template_name = 'orderutils/order_state.html'

	def get_context_data(self, **kwargs):
	    context = super(OrderStateLV, self).get_context_data(**kwargs)
	    context['form'] = DateForm()
	    return context

	def get_queryset(self):
		default_date = date.today() + timedelta(1)
		order_date = self.request.GET.get('date', default_date.strftime('%Y%m%d'))
		queryset = get_order_object_list_test(order_date)
		# print(queryset)
		return queryset





