from django.conf.urls import patterns, include, url
from django.contrib import admin

from .views import *
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'StockAdmin.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/', include('django.contrib.auth.urls')),
    url(r'^autocomplete$', autocomplete, name='autocomplete'),
    url(r'^$', Home.as_view(), name='home'),
    url(r'^info/', include('info.urls','info')),
    url(r'^stock/', include('stock.urls','stock')),
    url(r'^buy/', include('buy.urls','buy')),
    url(r'^narcotic/', include('narcotic.urls','narcotic')),
    url(r'^stock-invest/', include('stock_invest.urls','stock_invest')),
    url(r'^orderutils/', include('orderutils.urls','orderutils')),
)
