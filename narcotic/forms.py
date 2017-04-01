from django import forms
from datetime import date, timedelta

class DataRangeForm(forms.Form):
	start = forms.DateField(label='시작일', initial=date.today())
	end = forms.DateField(label='종료일', initial=date.today())


class OpSelectForm(forms.Form):
	narcotic = forms.BooleanField(label='마약', initial=True, widget=forms.CheckboxInput(attrs={'class':'badgebox','tabindex':'-1'}), required=False)
	psychotic = forms.BooleanField(label='향정', initial=True, widget=forms.CheckboxInput(attrs={'class':'badgebox','tabindex':'-1'}), required=False)
	date = forms.DateField(label='재고일자', initial=date.today())