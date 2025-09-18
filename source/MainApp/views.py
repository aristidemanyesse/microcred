from django.shortcuts import render
from annoying.decorators import render_to
from django.contrib.auth.decorators import login_required
from faker import Faker
from datetime import date
from FinanceApp.models import CompteEpargne, Echeance, Penalite, Pret, StatusPret
from MainApp.models import Client


@login_required()
@render_to('MainApp/dashboard.html')
def dashboard_view(request):
    prets = Pret.objects.filter(status__etiquette = StatusPret.EN_COURS)
    epargnes = CompteEpargne.objects.filter(status__etiquette = StatusPret.EN_COURS)
    clients = Client.objects.filter()
    echeances = Echeance.objects.filter(date_echeance__lte = date.today())
    penalites = Penalite.objects.filter(created_at__date= date.today())
    ctx = {
        'TITLE_PAGE' : "Tableau de bord",
        "prets": prets,
        "epargnes": epargnes,
        "clients": clients,
        "echeances": echeances,
        "penalites": penalites,
    }
    return ctx



@render_to('MainApp/clients.html')
def clients_view(request):
    clients = Client.objects.filter(agence=request.user.agence)
    ctx = {
        'TITLE_PAGE' : "Liste des souscripteurs",
        "clients": clients,
    }
    return ctx



@render_to('MainApp/client.html')
def client_view(request):
    clients = Client.objects.filter()
    ctx = {
        'TITLE_PAGE' : "Fiche client",
        "clients": clients,
    }
    return ctx



@render_to('MainApp/prets.html')
def prets_view(request):
    ctx = {
        'TITLE_PAGE' : "Liste des prêts en cours",
    }
    return ctx


@render_to('MainApp/demandes.html')
def demandes_view(request):
    ctx = {
        'TITLE_PAGE' : "Liste des demandes de prêts",
    }
    return ctx


@render_to('MainApp/echeances.html')
def echeances_view(request):
    ctx = {
        'TITLE_PAGE' : "Liste des rétards d'échéances",
    }
    return ctx


@render_to('MainApp/penalites.html')
def penalites_view(request):
    ctx = {
        'TITLE_PAGE' : "Liste des pénalités",
    }
    return ctx


@render_to('MainApp/pret.html')
def pret_view(request):
    faker = Faker("fr_FR")
    ctx = {
        'TITLE_PAGE' : "Fiche prêt",
        "faker": faker,
    }
    return ctx


@render_to('MainApp/epargnes.html')
def epargnes_view(request):
    faker = Faker("fr_FR")
    ctx = {
        'TITLE_PAGE' : "Liste des comptes épargnes",
        "faker": faker,
    }
    return ctx


@render_to('MainApp/epargne.html')
def epargne_view(request):
    faker = Faker("fr_FR")
    ctx = {
        'TITLE_PAGE' : "Fiche compte épargne",
        "faker": faker,
    }
    return ctx


@render_to('MainApp/rapports.html')
def rapports_view(request):
    ctx = {
        'TITLE_PAGE' : "Rapports Stats",
    }
    return ctx
