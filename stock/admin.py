from django.contrib import admin
from .models import StockRec
# Register your models here.


class StockRecAdmin(admin.ModelAdmin):
    '''
        Admin View for StockRec
    '''
    list_display = ('buyitem','amount','date','frozen','inout',)
    list_filter = ('frozen','inout',)
    search_fields = ('buyitem',)

admin.site.register(StockRec, StockRecAdmin)