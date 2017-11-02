from django import forms

class GosiFileForm(forms.Form):
	excel = forms.FileField(label='고시파일')