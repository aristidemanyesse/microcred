from django.contrib import admin

from TresorApp.models import CompteAgence, Operation, TypeActivity

# Register your models here.

@admin.register(TypeActivity)
class TypeActivityAdmin(admin.ModelAdmin):
    list_display = ('libelle', 'etiquette')

@admin.register(CompteAgence)
class CompteAgenceAdmin(admin.ModelAdmin):
    list_display = ('libelle', 'activity', 'base', 'created_at', "deleted")
    list_filter = ('activity',)

@admin.register(Operation)
class OperationAdmin(admin.ModelAdmin):
    list_display = ('libelle', 'montant', 'compte_debit', 'compte_credit', 'employe', 'created_at', "deleted")
    list_filter = ('employe', 'created_at')
    search_fields = ('employe',)