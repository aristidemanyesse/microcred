from django.shortcuts import render, redirect
from annoying.decorators import render_to
from django.contrib.auth.decorators import login_required
from faker import Faker
from datetime import date, timedelta
from FinanceApp.models import CompteEpargne, Echeance, Interet, ModePayement, Penalite, Pret, StatusPret
from MainApp.models import Client, Genre, TypeClient


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
        "types": TypeClient.objects.all(),
        "genres": Genre.objects.all(),
        "particulier": TypeClient.objects.filter(etiquette = TypeClient.PARTICULIER).first(),
        "entreprise": TypeClient.objects.filter(etiquette = TypeClient.ENTREPRISE).first(),
    }
    return ctx



@render_to('MainApp/client.html')
def client_view(request, pk):
    try:
        client = Client.objects.get(pk=pk)
        epargnes = CompteEpargne.objects.filter(client=client, status__etiquette = StatusPret.EN_COURS)
        prets = Pret.objects.filter(client=client, status__etiquette = StatusPret.EN_COURS)
        transactions = client.transactions.filter().order_by("-created_at")[:5]
        
        ctx = {
            'TITLE_PAGE' : "Fiche client",
            "client": client,
            "genres": Genre.objects.all(),
            "particulier": TypeClient.objects.filter(etiquette = TypeClient.PARTICULIER).first(),
            "entreprise": TypeClient.objects.filter(etiquette = TypeClient.ENTREPRISE).first(),
            "epargnes": epargnes,
            "prets": prets,
            "transactions": transactions,
        }
        return ctx
    except Exception as e:
        print("Erreur client_view: ", e)
        return redirect('MainApp:clients')



@render_to('MainApp/rapports.html')
def rapports_view(request):
    ctx = {
        'TITLE_PAGE' : "Rapports Stats",
    }
    return ctx
