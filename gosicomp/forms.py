from django import forms

from pprint import pprint

from .gosi_compare import is_excel, is_gosi_file




class GosiFileForm(forms.Form):
	excel = forms.FileField(label='고시파일')

	def clean_excel(self):
		excel = self.cleaned_data.get('excel')

		if not is_excel(excel.name):
			print(excel.name)
			raise forms.ValidationError('엑셀파일이 아닙니다')
		# else:
		# 	if not is_gosi_file(excel.file.read()):
		# 		excel.file.seek(0)
		# 		raise forsm.ValidationError('고시파일이 아닌것 같습니다')
		return excel