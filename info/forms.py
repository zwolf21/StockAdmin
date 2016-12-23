from django import forms
from .models import Info

class CSVForm(forms.Form):
	csv = forms.FileField(label='CSV 또는 엑셀파일')
	# recreate = forms.BooleanField(label='기존 데이터 삭제 후 다시 만들기', required=False)


class InfoCVForm(forms.ModelForm):

	class Meta:
		model = Info
		fields = ['edi','name','name_as','firm','price','pkg_amount','purchase_standard','account','etc_class','standard_unit','narcotic_class']
	
	def __init__(self, *args, **kwargs):
		super(InfoCVForm, self).__init__(*args, **kwargs)
	
	