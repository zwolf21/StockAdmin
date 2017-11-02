from django.shortcuts import render
from django.views.generic import FormView
from django.conf import settings
from django.http import HttpResponse

from .forms import GosiFileForm
from .service import get_compare_result


from pprint import pprint


class GosiFileFormView(FormView):
	template_name = 'gosicomp/gosicomp_form.html'
	form_class = GosiFileForm
	success_url = '.'

	def form_valid(self, form):
		excel = form.cleaned_data['excel']
		return get_compare_result(excel, file_contents=excel.file.read(), test=settings.TEST)

		

def gosi_listview(request):
	form = GosiFileForm(request.POST, request.FILES)
	if form.is_valid():
		excel = form.cleaned_data['excel']
		context = {
			'object_list': get_compare_result(excel, file_contents=excel.file.read(), test=settings.TEST, to_list=True)
		}
	else:
		context = {'form': form}
	return render(request, 'gosicomp/gosicomp_list.html', context)

