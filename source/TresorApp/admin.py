from django.contrib import admin

from TresorApp.models import CompteAgence, Operation

# Register your models here.

@admin.register(CompteAgence)
class CompteAgenceAdmin(admin.ModelAdmin):
    list_display = ('libelle', 'principal', 'base')
    list_filter = ('principal',)

@admin.register(Operation)
class OperationAdmin(admin.ModelAdmin):
    list_display = ('libelle', 'montant', 'compte_debit', 'compte_credit', 'employe')
    list_filter = ('employe',)