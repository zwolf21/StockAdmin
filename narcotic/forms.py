from django import forms
from datetime import date, timedelta

class DataRangeForm(forms.Form):
	start = forms.DateField(label='시작일', initial=date.today())
	end = forms.DateField(label='종료일', initial=date.today())