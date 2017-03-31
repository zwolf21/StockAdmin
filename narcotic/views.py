from django.shortcuts import render, render_to_response
from django.views.generic import FormView
from django.http import HttpResponse
# Create your views here.
from dateutil import parser

from .modules.FKHIS.narc_parser import get_opremain_contents
from .forms import DataRangeForm


class OpRemainFV(FormView):
	template_name = 'narcotic/opremain.html'
	form_class = DataRangeForm

	def form_valid(self, form):
		start = self.request.POST.get('start')
		end = self.request.POST.get('end')
		print(start, end)
		content = get_opremain_contents(start, end)
		fname = '{}~{}OpRemain.xlsx'.format(str(start), str(end))
		print(fname)
		response = HttpResponse(content, content_type='application/vnd.ms-excel')
		response['Content-Disposition'] = 'attachment; filename='+fname
		# response['Content-Disposition'] = 'attachment; filename='+'aaa.xls'
		return response
