from django import forms
from datetime import date, timedelta, time

class DateForm(forms.Form):
	date = forms.DateField(label='조회일자', initial=date.today()+timedelta(1))

class LabelDateTimeform(forms.Form):
	start_t = forms.TimeField(label='시작시간', initial=time(0,0,0))
	end_t = forms.TimeField(label='끝시간', initial=time(23,59,59))
	date = forms.DateField(label='처방일자', initial=date.today() + timedelta(1))
	words = forms.CharField(label='병동', initial='51, 52, 61, 71, 81, 92, IC')
	