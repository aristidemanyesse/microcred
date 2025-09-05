from django.shortcuts import render
from annoying.decorators import render_to
from faker import Faker


def login_view(request):
    return render(request, 'MainApp/login.html')

def dashboard_view(request):
    return render(request, 'MainApp/dashboard.html')

@render_to('MainApp/clients.html')
def clients_view(request):
    faker = Faker("fr_FR")
    ctx = {
        "faker": faker,
    }
    return ctx



@render_to('MainApp/client.html')
def client_view(request):
    faker = Faker("fr_FR")
    ctx = {
        "faker": faker,
    }
    return ctx


def credits_view(request):
    return render(request, 'MainApp/credits.html')

@render_to('MainApp/credit.html')
def credit_view(request):
    faker = Faker("fr_FR")
    ctx = {
        "faker": faker,
    }
    return ctx


@render_to('MainApp/epargne.html')
def epargne_view(request):
    faker = Faker("fr_FR")
    ctx = {
        "faker": faker,
    }
    return ctx

def rapports_view(request):
    return render(request, 'MainApp/rapports.html')
