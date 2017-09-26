import datetime
from django import forms
from django.forms import CheckboxSelectMultiple, Textarea, DateInput, DateTimeInput
from django.utils.encoding import force_text
from django.utils.html import format_html
from django.utils.safestring import mark_safe


def get_form_class(kind=None, app='collect', test=False, **kwargs):
    if test:
        return CollectFormTest if app == 'collect' else StaticForm

    if kind == 'LABEL':
        return CollectLabelForm if app == 'collect' else StaticLabelForm
    elif kind == 'NUT':
        return CollectNutForm if app == 'collect' else StaticNutForm
    elif kind == 'INJ':
        return CollectInjForm if app == 'collect' else StaticInjForm
    else:
        return CollectForm if app == 'collect' else StaticForm


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

class CollectForm(forms.Form):
    date = forms.DateField(initial=datetime.date.today())
    types = forms.MultipleChoiceField(choices=[('ST', '정기'), ('AD', '추가'), ('EM', '응급'), ('OT', '퇴원')], initial=['ST'], widget=CheckboxSelectMultiple(renderer=HorizontalCheckboxRenderer))
    wards = forms.MultipleChoiceField(choices=WARDS_CHOICES, initial=[e[0] for e in WARDS_CHOICES], widget=CheckboxSelectMultiple(renderer=HorizontalCheckboxRenderer))
    start_date = forms.DateField()
    end_date = forms.DateField()
    start_dt = forms.DateTimeField()
    end_dt = forms.DateTimeField()


class CollectLabelForm(CollectForm):
    kind = forms.ChoiceField(choices=[('LABEL', '라벨')], initial='LABEL')

class CollectNutForm(CollectForm):
    kind = forms.ChoiceField(choices=[('NUT', '영양수액')], initial='NUT')
    # excludes = forms.CharField(required=False, widget=Textarea(attrs={'rows':5, 'cols': 20, 'placeholder': '제외할 약품 입력 후 엔터키'}))
    # extras = forms.CharField(required=False, widget=Textarea(attrs={'rows':5, 'cols': 20, 'placeholder': '추가할 약품 입력 후 엔터키'}))

class CollectInjForm(CollectForm):
    kind = forms.ChoiceField(choices=[('INJ', '주사')], initial='INJ')
    # excludes = forms.CharField(required=False, widget=Textarea(attrs={'rows':5, 'cols': 20, 'placeholder': '제외할 약품 입력 후 엔터키'}))
    # extras = forms.CharField(required=False, widget=Textarea(attrs={'rows':5, 'cols': 20, 'placeholder': '추가할 약품 입력 후 엔터키'}))



test_date = datetime.date(2017, 9 ,20)
test_dt = test_date - datetime.timedelta(1)

class CollectFormTest(forms.Form):
    date = forms.DateField(initial=datetime.date.today(), widget=DateInput())
    types = forms.MultipleChoiceField(choices=[('ST', '정기'), ('AD', '추가'), ('EM', '응급'), ('OT', '퇴원')], initial=['ST'], widget=CheckboxSelectMultiple(renderer=HorizontalCheckboxRenderer))
    wards = forms.MultipleChoiceField(choices=WARDS_CHOICES, initial=[e[0] for e in WARDS_CHOICES], widget=CheckboxSelectMultiple(renderer=HorizontalCheckboxRenderer))
    start_date = forms.DateField(initial=test_date, widget=DateInput(attrs={'type': 'date'}))
    end_date = forms.DateField(initial=test_date, widget=DateInput(attrs={'type': 'date'}))
    start_dt = forms.DateTimeField(initial=test_dt, widget=DateTimeInput(attrs={'type': 'datetime'}))
    end_dt = forms.DateTimeField(initial=test_date, widget=DateTimeInput(attrs={'type': 'datetime'}))
    kind = forms.ChoiceField(choices=[('NUT', '영양수액'), ('LABEL', '라벨'), ('INJ', '주사')], initial='NUT')



class StaticForm(forms.Form):
    excludes = forms.CharField(required=False, widget=Textarea(attrs={'rows':20, 'cols': 30, 'placeholder': '제외할 약품 입력 후 엔터키'}))
    extras = forms.CharField(required=False, widget=Textarea(attrs={'rows':20, 'cols': 30, 'placeholder': '추가할 약품 입력 후 엔터키'}))

class StaticLabelForm(StaticForm):
    kind = forms.ChoiceField(choices=[('LABEL', '라벨')], initial='LABEL')

class StaticNutForm(StaticForm):
    kind = forms.ChoiceField(choices=[('NUT', '영양수액')], initial='NUT')

class StaticInjForm(StaticForm):
    kind = forms.ChoiceField(choices=[('INJ', '주사')], initial='INJ')




