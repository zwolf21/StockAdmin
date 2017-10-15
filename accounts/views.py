from django.shortcuts import render
from django.views.generic import CreateView
from django.contrib.auth.forms import UserCreationForm


class RegisterView(CreateView):
	template_name = 'registration/register.html'
	form_class = UserCreationForm
	success_url = '/'


##TAG: 로그인 app 재활용법, login
# 1. accounts 폴더를 통째로 가져간다
# 2. settings.py INSTALLED_APPS 맨위에 accounts 를 등록한다.
# 3. 부트스트랩, 밑 static/custom/login 도 가져간다.
# 4. root urls.py 에 url(r'^accounts/', include('accounts.urls')),등록한다(namespace 지정하면 안됨!)

