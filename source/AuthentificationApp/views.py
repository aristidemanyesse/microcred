from django.shortcuts import render, redirect
from annoying.decorators import render_to
from faker import Faker
from django.contrib.auth import logout


@render_to('AuthentificationApp/login.html')
def login_view(request):
    ctx = {}
    return ctx


def logout_view(request):
    logout(request)
    return redirect('AuthentificationApp:login')



@render_to('AuthentificationApp/users.html')
def users_view(request):
    ctx = {}
    return ctx

