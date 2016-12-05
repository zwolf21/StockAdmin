from django import forms
from .models import BuyItem, Buy
from datetime import date

class CreateBuyForm(forms.ModelForm):
	date = forms.DateField(initial=date.today(), widget=forms.TextInput(attrs={'tabindex':'-1','readonly':'readonly'}))

	class Meta:
		model = Buy
		fields = ['date']


class BuyItemAddForm(forms.ModelForm):
	# name = forms.CharField(label='약품명', required=False)
	amount = forms.IntegerField(label='수량', required=False, help_text='위아래 방향키로 수량조절')


	class Meta:
		model = BuyItem
		fields = ['amount','comment']
		help_texts = {'amount':('위아래 방향키로 수량 조절')}

