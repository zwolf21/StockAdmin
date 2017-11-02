from django.shortcuts import render
from django.views.generic import FormView

from .forms import GosiFileForm
from .sevice import get_edi_code_from_gosi, get_compare_result


from pprint import pprint


class GosiFileFormView(FormView):
	template_name = 'gosicomp/gosicomp_form.html'
	form_class = GosiFileForm
	success_url = '.'

	def form_valid(self, form):
		# pprint(form.cleaned_data)
		excel = form.cleaned_data['excel']
		edis = get_compare_result(excel, file_contents=excel.file.read())
		return edis
		# return super(GosiFileFormView, self).form_valid(form)
