from django import forms


class CSVForm(forms.Form):
	csv = forms.FileField(label='CSV 또는 엑셀파일')
	# recreate = forms.BooleanField(label='기존 데이터 삭제 후 다시 만들기', required=False)