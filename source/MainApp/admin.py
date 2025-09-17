from django.contrib import admin

from MainApp.models import *

# Register your models here.

@admin.register(Agence)
class AgenceAdmin(admin.ModelAdmin):
    list_display = ('libelle', 'adresse', 'ville', 'code')
    search_fields = ('libelle', 'adresse', 'ville', 'code')
    
    
@admin.register(TypeClient)
class TypeClientAdmin(admin.ModelAdmin):
    list_display = ('libelle', 'etiquette')
    search_fields = ('libelle',)
    
    
@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('libelle', 'etiquette')
    search_fields = ('libelle',)
    
    
@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('agence', 'type_client', 'nom', 'prenoms', 'genre', 'date_naissance', 'adresse', 'telephone', 'email')
    search_fields = ('agence__id', 'agence__libelle', 'nom', 'prenoms', 'genre__libelle', 'genre__etiquette', 'type_client__libelle', 'type_client__etiquette')
    list_filter = ('type_client', 'genre')