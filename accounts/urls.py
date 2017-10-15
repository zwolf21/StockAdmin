from django.conf.urls import url, include

from django.views.generic import TemplateView
from django.contrib import admin

from .views import RegisterView

##TAG: 로그인urlconf, login url, 사용자 등록은 따로 구현해야함
urlpatterns = [
	url(r'^', include('django.contrib.auth.urls')),
	url(r'^register/$', RegisterView.as_view(), name='register'),
]