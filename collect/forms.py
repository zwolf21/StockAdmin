import datetime
from django.core.urlresolvers import reverse
from django import forms
from django.forms.formsets import formset_factory
from django.forms import CheckboxSelectMultiple, Textarea, DateInput, DateTimeInput
from django.utils.encoding import force_text
from django.utils.html import format_html
from django.utils.safestring import mark_safe

_today = lambda :datetime.date.today()

WARDS_CHOICES = [('51', '51'), ('52', '52'), ('61', '61'), ('71', '71'), ('81', '81'), ('92', '92'), ('IC', 'IC')]

WARDS = [e[0] for e in WARDS_CHOICES]

FORMSET_INITIAL = \
[
        {
            'date': _today,
            'kinds': ['LABEL'],
            'wards': WARDS,
            'types': ['ST'],
        },
        {
            'date': _today,
            'kinds': ['NUT'],
            'wards': WARDS,
            'types': ['ST'],
        },
        {
            'date': _today,
            'kinds': ['INJ'],
            'wards': WARDS,
            'types': ['ST'],
        },
        {
            'date': _today,
            'kinds': ['INJ'],
            'wards': WARDS,
            'types': ['AD', 'EM'],
        },  
]


class HorizontalCheckboxRenderer(forms.CheckboxSelectMultiple.renderer):
    def render(self):
        output = [format_html(u'{0}', force_text(widget)) for widget in self]
        return mark_safe('\n'.join(output))


class CollectForm(forms.Form):
    date = forms.DateField(initial=_today, widget=DateInput)
    kinds = forms.MultipleChoiceField(choices=[('LABEL', '라벨'), ('INJ', '주사'), ('NUT', '영양수액'),], widget=CheckboxSelectMultiple(renderer=HorizontalCheckboxRenderer))
    types = forms.MultipleChoiceField(choices=[('ST', '정기'), ('AD', '추가'), ('EM', '응급'), ('OT', '퇴원')], initial=['ST'], widget=CheckboxSelectMultiple(renderer=HorizontalCheckboxRenderer))
    wards = forms.MultipleChoiceField(choices=WARDS_CHOICES, initial=WARDS, widget=CheckboxSelectMultiple(renderer=HorizontalCheckboxRenderer))
    start_date = forms.DateField(widget=DateInput(attrs={'readonly': 'readonly'}))
    end_date = forms.DateField(widget=DateInput(attrs={'readonly': 'readonly'}))
    start_dt = forms.DateTimeField(widget=DateTimeInput(attrs={'readonly': 'readonly'}))
    end_dt = forms.DateTimeField(widget=DateTimeInput(attrs={'readonly': 'readonly'}))

    def __init__(self, kinds=None, *args, **kwargs):
        super(CollectForm, self).__init__(*args, **kwargs)
        if kinds: 
            self.fields['kinds'].initial = kinds



CollectFormset = formset_factory(CollectForm, extra=4, max_num=4)


class ConfigForm(forms.Form):
    kind = forms.ChoiceField(choices=[('LABEL', '라벨'), ('INJ', '주사'), ('NUT', '영양수액')])
    extras = forms.CharField(required=False, widget=Textarea)
    excludes = forms.CharField(required=False, widget=Textarea)
    exclude_groups = forms.CharField(required=False, widget=Textarea(attrs={'rows': 3, 'cols': 60}))









