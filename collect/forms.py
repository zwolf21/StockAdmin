import datetime
from django import forms
from django.forms import CheckboxSelectMultiple
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




WARDS_CHOICES = [('51', '51'), ('52', '52'), ('61', '61'), ('71', '71'), ('72', '72'), ('81', '81'), ('91', '91'), ('92', '92'), ('IC', 'IC')]

class CollectCreateForm(forms.Form):
    date = forms.DateField(initial=datetime.date.today(), required=False)
    start_date = forms.DateField(initial=datetime.date.today() + datetime.timedelta(1))
    end_date = forms.DateField(initial=datetime.date.today() + datetime.timedelta(1))
    start_dt = forms.DateTimeField(initial=datetime.date.today())
    end_dt = forms.DateTimeField(initial=datetime.datetime.now())
    wards = forms.MultipleChoiceField(choices=WARDS_CHOICES, initial=[e[0] for e in WARDS_CHOICES], widget=CheckboxSelectMultiple(renderer=HorizontalCheckboxRenderer))
    kind = forms.ChoiceField(choices=[('영양수액', '영양수액'), ('라벨', '라벨')], initial='라벨')
    types = forms.MultipleChoiceField(choices=[('정기', '정기'), ('추가', '추가'), ('응급', '응급'), ('퇴원', '퇴원')], initial=['정기'], widget=CheckboxSelectMultiple(renderer=HorizontalCheckboxRenderer))
