from django.contrib import admin

from FidelisApp.models import CompteFidelis, FidelisCase

# Register your models here.

@admin.register(CompteFidelis)
class CompteFidelisAdmin(admin.ModelAdmin):
    list_display = ('numero', 'client', 'base', 'nombre', 'frais', 'retire', 'status', 'employe')
    search_fields = ('numero', 'client__nom', 'client__prenom', 'client')
    
@admin.register(FidelisCase)
class FidelisCaseAdmin(admin.ModelAdmin):
    list_display = ('fidelis', 'level', 'status')
    search_fields = ('fidelis__libelle', 'fidelis__numero')
