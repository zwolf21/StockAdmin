from django.forms.models import inlineformset_factory, modelform_factory
from .models import Invest, InvestItem

InvestInlineFormSet = inlineformset_factory(Invest, InvestItem,
	fields = ('drug', 'pkg', 'rest1', 'rest2', 'rest3', 'total', 'expire', 'complete', 'completed', ),
	max_num = 200, can_order=True, can_delete = True, extra=0
)

InvestCreateForm = modelform_factory(Invest, fields=['date'])