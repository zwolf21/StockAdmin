from rest_framework.serializers import ModelSerializer, SerializerMethodField
from rest_framework import serializers

from info.models import Info, Account
from buy.models import BuyItem, Buy
from stock.models import StockRec

class ListInfoSerializer(ModelSerializer):
	class Meta:
		model = Info
		fields = ('edi', 'name', 'name_as', 'code', 'firm', 'price', 'pkg_amount', 'narcotic_class', 'account', 'status', 'etc_class', 
				'last_stockin_date', 'last_stockin_amount', 'last_stockin_amount', 'predict_weekly', 'weekly_avg_stockin')
		depth = 1


class CreateBuyItemSerializer(ModelSerializer):
	class Meta:
		model = BuyItem
		fields = ('drug', 'amount', )


class ListBuyItemIncomplete(ModelSerializer):
	class Meta:
		model = BuyItem
		fields = ('buy', 'drug', 'amount' ,'stockin_amount', 'end', )
		depth = 1



class StockRecSubAccountSerializer(ModelSerializer):
	class Meta:
		model = Account
		fields = ('name', )


class StockRecSubInfoSerializer(ModelSerializer):
	account = StockRecSubAccountSerializer()
	
	class Meta:
		model = Info
		fields = ('name', 'name_as', 'price', 'etc_class', 'account', )

class BuyItemSubBuySerializer(ModelSerializer):
	class Meta:
		model = Buy
		fields = ('slug', )


class StockRecSubBuyItemSerializer(ModelSerializer):
	buy = BuyItemSubBuySerializer()
	class Meta:
		model = BuyItem
		fields = ('buy', )



class ListStockRecSerializer(ModelSerializer):
	drug = StockRecSubInfoSerializer()
	buyitem = StockRecSubBuyItemSerializer()
	class Meta:
		model = StockRec
		fields = ('id', 'buyitem', 'drug',  'amount', 'date', 'total_price', )
		