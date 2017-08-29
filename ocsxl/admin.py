from django.contrib import admin

from .models import OcsFile


class OcsFileAdmin(admin.ModelAdmin):
	list_display = 'filename', 'description', 'created', 
admin.site.register(OcsFile, OcsFileAdmin)

