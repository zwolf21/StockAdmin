from django import forms
from datetime import date, timedelta, time, datetime

class DateForm(forms.Form):
	date = forms.DateField(label='조회일자', initial=date.today()+timedelta(1))

class LabelDateTimeform(forms.Form):
	ord_start_date = forms.DateField(label='처방일자시작', initial=date.today() + timedelta(1))
	ord_end_date = forms.DateField(label='처방일자끝', initial=date.today() + timedelta(1))

	start_t = forms.DateTimeField(label='접수시작', initial=date.today())
	end_t = forms.DateTimeField(label='접수 끝시각', initial=date.today()+timedelta(1))

	date = forms.DateField(label='처방일자시작', initial=date.today() + timedelta(1))
	ward = forms.CharField(label='병동', initial='51, 52, 61, 71, 81, 92, IC')
	