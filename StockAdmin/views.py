from info.models import Info
from django.db.models import Q
# from django.http import JsonResponse
from django.views.generic import TemplateView
from django.http import HttpResponse
from json import dumps
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.admin.views.decorators import staff_member_required
import operator



class LoginRequiredMixin(object):
	@classmethod
	def as_view(cls, **initkwargs):
		view = super(LoginRequiredMixin, cls).as_view(**initkwargs)
		return login_required(view)

class PermissionRequiredMixin(object):
	@classmethod
	def as_view(cls, **initkwargs):
		view = super(PermissionRequiredMixin, cls).as_view(**initkwargs)
		return permission_required(view)

class Staff_memberRequiredMixin(object):
	@classmethod
	def as_view(cls, **initkwargs):
		view = super(Staff_memberRequiredMixin, cls).as_view(**initkwargs)
		return staff_member_required(view)


def autocomplete(request):
	if request.is_ajax():
		kw = request.GET['term']
		# qry = reduce(operator.__and__, (Q(name__contains=word) for word in kw))
		# print(dir(qry))
		queryset = Info.objects.filter(Q(name_as__contains=kw), status=1).iterator()
		ret = []
		for drug in queryset:
			ret.append({
					'drug_name':drug.name,
					'pkg_amount':drug.pkg_amount,
					'acc_amount':drug.total_stockin_amount,
					'incompletes':drug.total_incomplete_amount,
					'stockin_last':drug.last_stockin_date.strftime('%Y-%m-%d') if drug.last_stockin_date else ''
				})
		
		return HttpResponse(dumps(ret), content_type="application/json")



class Home(TemplateView):
	template_name = 'home.html'
