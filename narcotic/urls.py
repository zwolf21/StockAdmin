from django.conf.urls import url

from .views import *

urlpatterns = [
	url(r'^opremain/$', OpRemainFV.as_view(), name='opremain')
]