from django.contrib import admin

from AuthentificationApp.models import *

# Register your models here.

@admin.register(Employe)
class EmployeAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'username', 'email', 'is_superuser', "is_staff", "is_active")
    search_fields = ('first_name', 'last_name', 'username', 'email')
    
@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('libelle',)
    search_fields = ('libelle',)
    
    
@admin.register(Connexion)
class ConnexionAdmin(admin.ModelAdmin):
    list_display = ('employe', 'ip', 'user_agent')
    search_fields = ('employe__id', 'employe__nom', 'employe__prenoms')