from django.shortcuts import render, redirect
from annoying.decorators import render_to
from faker import Faker
from django.contrib.auth import logout

from AuthentificationApp.models import Employe, Role


@render_to('AuthentificationApp/login.html')
def login_view(request):
    ctx = {
        "TITLE_PAGE": "Espace d'authentification",
    }
    return ctx


def logout_view(request):
    logout(request)
    return redirect('AuthentificationApp:login')



@render_to('AuthentificationApp/users.html')
def users_view(request):
    roles = Role.objects.all().order_by('etiquette')
    users = Employe.objects.filter(deleted = False).order_by("created_at")
    ctx = {
        "TITLE_PAGE": "Gestion des utilisateurs et des droits",
        "roles": roles,
        "users": users,
        
    }
    return ctx

