from django.contrib import admin
from .models import Buy, BuyItem
# Register your models here.
class BuyAdmin(admin.ModelAdmin):
    '''
        Admin View for Buy
    '''
    list_display = ('slug','date','commiter',)
    list_filter = ('commiter',)

admin.site.register(Buy, BuyAdmin)

class BuyItemAdmin(admin.ModelAdmin):
    '''
        Admin View for BuyItem
    '''
    list_display = ('drug_code','drug','buy','amount','incomplete_amount','stockin_amount','comment','is_completed','end','by','create_date')
    list_filter = ('end','buy',)

admin.site.register(BuyItem, BuyItemAdmin)