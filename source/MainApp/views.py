from django.shortcuts import render
from annoying.decorators import render_to
from faker import Faker



@render_to('MainApp/dashboard.html')
def dashboard_view(request):
    ctx = {
        'TITLE_PAGE' : "Tableau de bord",
    }
    return ctx



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



@render_to('MainApp/prets.html')
def prets_view(request):
    return render(request, 'MainApp/prets.html')


@render_to('MainApp/demandes.html')
def demandes_view(request):
    return render(request, 'MainApp/demandes.html')


@render_to('MainApp/echeances.html')
def echeances_view(request):
    return render(request, 'MainApp/echeances.html')


@render_to('MainApp/penalites.html')
def penalites_view(request):
    return render(request, 'MainApp/penalites.html')


@render_to('MainApp/pret.html')
def pret_view(request):
    faker = Faker("fr_FR")
    ctx = {
        "faker": faker,
    }
    return ctx


@render_to('MainApp/epargnes.html')
def epargnes_view(request):
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


@render_to('MainApp/rapports.html')
def rapports_view(request):
    ctx = {}
    return ctx
