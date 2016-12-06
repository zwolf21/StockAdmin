from django.conf.urls import url, patterns
from .views import *


urlpatterns = patterns('',

	# views
	url(r'^list/$', BuyLV.as_view(), name='buy_list'),
	url(r'^detail/(?P<slug>[-\w]+)/$', BuyDV.as_view(), name='buy_detail'),
	url(r'^printBuy/(?P<slug>[-\w]+)/$', BuyDVprint.as_view(), name='buy_print'),
	url(r'^update/(?P<slug>[-\w]+)/$', BuyUV.as_view(), name='buy_update'),

	url(r'^listUp/$', BuyItemLV.as_view(), name='buyitem_listup'),
	url(r'^item/add/$', BuyItemCV.as_view(), name='buyitem_add'),
	url(r'^item/update/(?P<pk>\d+)/$', BuyItemUV.as_view(), name='buyitem_update'),
	url(r'^item/delete/(?P<pk>\d+)/$', BuyItemDelV.as_view(), name='buyitem_delete'),
	url(r'^narcotic/(?P<slug>[-\w]+)/$', NarcoticLV.as_view(), name='narcotic'),


	# functions
	url(r'^gen/$', gen_buy, name='buy_gen'),
	url(r'^commit/(?P<slug>[-\w]+)/$', buy_commit, name='commit'),
	url(r'^cartRollBack/(?P<slug>[-\w]+)/$', roll_back2cart, name='cart_rollback'),

	

	


)

















