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
    list_display = ('edi','firm','code','name', 'name_as','standard_unit','purchase_standard','pkg_amount', 'invest_class','price',)
    list_filter = ('narcotic_class','create_date','etc_class','status','account', 'standard_unit', 'invest_class')
    list_editable = ('firm', 'name','name_as', 'pkg_amount', 'price', 'standard_unit', 'invest_class', 'purchase_standard',  )
    search_fields = ('name','edi',)
admin.site.register(Info, InfoAdmin)

