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
	can_delete = True,
	can_order = True,
	widgets = {
		'pkg': forms.NumberInput(attrs={})
	}
)


InvestCreateForm = modelform_factory(
	model = Invest,
	fields = ['date']
)

# inlineformset_factory(parent_model, model, form, formset, fk_name, fields, exclude, extra, can_order, can_delete, max_num, formfield_callback, widgets, validate_max, localized_fields, labels, help_texts, error_messages, min_num, validate_min, field_classes)
# modelform_factory(model, form, fields, exclude, formfield_callback, widgets, localized_fields, labels, help_texts, error_messages, field_classes)