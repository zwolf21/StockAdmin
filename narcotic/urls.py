from django.conf.urls import url

from .views import *

urlpatterns = [
	url(r'^opremain/$', OpRemainFV.as_view(), name='opremain'),
	url(r'^opstock/$', OpStockLV.as_view(), name='opstock'),
	url(r'^opstock/print/$', OpStockPrintTV.as_view(), name='opstock_print'),
]