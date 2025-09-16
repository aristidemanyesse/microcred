from django.shortcuts import render
from annoying.decorators import render_to
from faker import Faker


@render_to('AuthentificationApp/login.html')
def login_view(request):
    ctx = {}
    return ctx




@render_to('AuthentificationApp/users.html')
def users_view(request):
    ctx = {}
    return ctx

