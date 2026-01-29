from django.contrib import admin

from FidelisApp.models import CompteFidelis, FidelisCase
from FinanceApp.admin import TransactionInline

# Register your models here.
class CompteFidelisInline(admin.TabularInline):
    model = CompteFidelis
    extra = 0
    can_delete = False
    fields = ("numero", "client", "base", "nombre", "frais", "retire", "status", "created_at", "deleted")
    readonly_fields = ("numero", "client", "base", "nombre", "frais", "retire", "status", "created_at", "deleted")


class FidelisCaseInline(admin.TabularInline):
    model = FidelisCase
    extra = 0
    can_delete = False
    fields = ("fidelis", "level", "status", "created_at", "deleted")
    readonly_fields = ("fidelis", "level", "status", "created_at", "deleted")
    
@admin.register(CompteFidelis)
class CompteFidelisAdmin(admin.ModelAdmin):
    list_display = ('numero', 'client', 'base', 'nombre', 'frais', 'retire', 'status', 'employe', 'created_at', "deleted")
    search_fields = ('numero', 'client__nom', 'client__prenoms')
    inlines = [FidelisCaseInline, TransactionInline]
    
@admin.register(FidelisCase)
class FidelisCaseAdmin(admin.ModelAdmin):
    list_display = ('fidelis', 'level', 'status', 'created_at', "deleted")
    search_fields = ('fidelis__libelle', 'fidelis__numero')
