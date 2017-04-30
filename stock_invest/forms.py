from django.forms.models import inlineformset_factory, modelform_factory
from django import forms
from .models import Invest, InvestItem
from django.contrib.admin.widgets import AdminDateWidget 


InvestInlineFormSet = inlineformset_factory(
	parent_model = Invest, 
	model = InvestItem,
	fields = ['pkg', 'rest1', 'rest2', 'rest3', 'expire', 'complete'],
	max_num = 200,
	extra=0,
	widgets = {
		'pkg': forms.NumberInput(attrs={})
	}
)


InvestCreateForm = modelform_factory(
	model = Invest,
	fields = ['date']
)

# modelform_factory(model, form, fields, exclude, formfield_callback, widgets, localized_fields, labels, help_texts, error_messages, field_classes)