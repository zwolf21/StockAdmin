import datetime
from django import forms
from django.forms import CheckboxSelectMultiple, Textarea
from django.utils.encoding import force_text
from django.utils.html import format_html
from django.utils.safestring import mark_safe


class HorizontalCheckboxRenderer(forms.CheckboxSelectMultiple.renderer):
    def render(self):
        id_ = self.attrs.get('id', None)
        # start_tag = format_html('<div id="{0}">', id_) if id_ else '<div>'
        output = []
        for widget in self:
            output.append(format_html(u'{0}', force_text(widget)))
        # output.append('</span>')
        return mark_safe('\n'.join(output))



WARDS_CHOICES = [('51', '51'), ('52', '52'), ('61', '61'), ('71', '71'), ('81', '81'), ('92', '92'), ('IC', 'IC')]

class CollectCreateForm(forms.Form):
    date = forms.DateField(initial=datetime.date.today(), required=False)
    start_date = forms.DateField(initial=datetime.date.today() + datetime.timedelta(1))
    end_date = forms.DateField(initial=datetime.date.today() + datetime.timedelta(1))
    start_dt = forms.DateTimeField(initial=datetime.date.today())
    end_dt = forms.DateTimeField(initial=datetime.datetime.now())
    wards = forms.MultipleChoiceField(choices=WARDS_CHOICES, initial=[e[0] for e in WARDS_CHOICES], widget=CheckboxSelectMultiple(renderer=HorizontalCheckboxRenderer))
    kind = forms.ChoiceField(choices=[('NUT', '영양수액'), ('LABEL', '라벨')], initial='LABEL')
    types = forms.MultipleChoiceField(choices=[('ST', '정기'), ('AD', '추가'), ('EM', '응급'), ('OUT', '퇴원')], initial=['ST'], widget=CheckboxSelectMultiple(renderer=HorizontalCheckboxRenderer))
    exclude_names = forms.CharField(required=False, widget=Textarea())
