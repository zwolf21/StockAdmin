from datetime import date, timedelta, datetime
from django.shortcuts import render, render_to_response
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

# Create your views here.
from django.views.generic import ListView, FormView, TemplateView
from StockAdmin.services.FKHIS.order_mon import get_order_object_list_test, get_order_object_list
from StockAdmin.services.FKHIS.order_selector import get_label_object_test, get_label_object, get_chemo_label_object_test, get_chemo_label_object

from .forms import DateForm, LabelDateTimeform
from .utils import LabelRecordParser, ord_types

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
		return queryset


class LabelCollectFV(FormView):
	template_name = 'orderutils/label_collect.html'
	form_class = LabelDateTimeform

	def get_success_url(self):
		context = self.get_context_data()
		return context['collect_history_list'][0]['url']

	def get_context_data(self, **kwargs):
		context = super(LabelCollectFV, self).get_context_data(**kwargs)
		lbl = LabelRecordParser()
		context['collect_history_list'] = lbl.get_collect_object_list()

		collect_date, seq, ord_tp = self.kwargs.get('date'), self.kwargs.get('seq'), self.kwargs.get('ord_tp')

		if collect_date and seq and ord_tp:
			collect = lbl.select_collect(collect_date, ord_tp, seq=int(seq))
			context['object_list'] = collect['records']
			context['form'] = LabelDateTimeform(collect['form_data'])
			context['now_history'] = True
			context['ord_type'] = ord_types[ord_tp]
		else:
			context['last_collect'] = lbl.get_last_collect()
		
		return context

	def form_valid(self, form):
		ord_start_date = form.data['ord_start_date']
		ord_end_date = form.data['ord_end_date']
		start_dt = form.data['start_t']
		end_dt = form.data['end_t']
		ward_str = form.data['ward']
		ord_tp = form.data['ord_tp']
		wards = ward_str.split(', ')
		
		if ord_tp == 'ch':
			agg, detail = get_chemo_label_object(wards, ord_start_date, ord_end_date, start_dt, end_dt)
		else:
			agg, detail = get_label_object(['S', 'P'], [ord_types[ord_tp]], wards, ord_start_date, ord_end_date, start_dt, end_dt)
		lbl = LabelRecordParser()
		if agg:
			lbl.save_queryset(agg, detail, ord_tp, form.data)

		return super(LabelCollectFV, self).form_valid(form)


def label_history_clear(request):
	if request.method == "POST":
		lbl = LabelRecordParser()
		lbl.clear_history()
	return HttpResponseRedirect(reverse('orderutils:labelcollect'))

	
	

