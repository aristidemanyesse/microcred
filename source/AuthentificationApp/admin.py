from django.contrib import admin

from AuthentificationApp.models import *

# Register your models here.

@admin.register(Employe)
class EmployeAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'username', 'email', 'is_superuser')
    search_fields = ('first_name', 'last_name', 'username', 'email')
    
@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('libelle',)
    search_fields = ('libelle',)