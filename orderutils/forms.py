from django import forms
from datetime import date, timedelta

class DateForm(forms.Form):
	date = forms.DateField(label='조회일자', initial=date.today()+timedelta(1))
