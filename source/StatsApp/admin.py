from django.contrib import admin

from StatsApp.models import Rapport

# Register your models here.

@admin.register(Rapport)
class RapportAdmin(admin.ModelAdmin):
    list_display = ('titre', 'date_generation', 'type_rapport')
    search_fields = ('titre',)