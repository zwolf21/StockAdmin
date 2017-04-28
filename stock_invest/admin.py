from django.contrib import admin

# Register your models here.

from .models import *


class InvestAdmin(admin.ModelAdmin):
	list_display = ('slug', 'date', 'commiter', )
admin.site.register(Invest, InvestAdmin)


class InvestItemAdmin(admin.ModelAdmin):
	list_display = ('drug', 'pkg', 'rest1', 'rest2', 'rest3', 'total', 'expire', )
	list_editable = ('pkg', 'rest1', 'rest2', 'rest3', 'expire')
	list_filter = ('invest', 'drug__invest_class', 'drug__etc_class' ,'completed', 'total',)
	search_fields = ('drug__name', )
admin.site.register(InvestItem, InvestItemAdmin)