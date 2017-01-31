from django.contrib import admin
from .models import Info, Account

# Register your models here.


class AcountAdmin(admin.ModelAdmin):
    '''
        Admin View for Acount
    '''
    list_display = ('name','tel','email','address',)
admin.site.register(Account, AcountAdmin)

class InfoAdmin(admin.ModelAdmin):
    '''
        Admin View for Info
    '''
    list_display = ('firm','edi','name','standard_unit','purchase_standard','pkg_amount','total_stockin_amount','price','predict_weekly')
    list_filter = ('narcotic_class','create_date','etc_class','status','account',)
    search_fields = ('name','edi',)
admin.site.register(Info, InfoAdmin)

