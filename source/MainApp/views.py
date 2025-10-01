from django.shortcuts import render, redirect
from annoying.decorators import render_to
from django.contrib.auth.decorators import login_required
from faker import Faker
from datetime import date, timedelta
from FinanceApp.models import CompteEpargne, Echeance, Interet, ModaliteEcheance, ModePayement, Penalite, Pret, StatusPret, Transaction, TypeTransaction
from MainApp.models import Client, Genre, TypeClient
from django.db.models import Count, Sum, Case, When, DecimalField
from django.utils.timezone import now
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated


@login_required()
@render_to('MainApp/dashboard.html')
def dashboard_view(request):
    if not request.user.is_authenticated:
        return redirect('AuthentificationApp:login')

    today = now().date()
    start_month = today.replace(day=1)
    
    
    prets = Pret.objects.filter(status__etiquette = StatusPret.EN_COURS)
    epargnes = CompteEpargne.objects.filter(status__etiquette = StatusPret.EN_COURS)
    comptes_mois = CompteEpargne.objects.filter(status__etiquette = StatusPret.EN_COURS, created_at__date__year=start_month.year, created_at__date__month=start_month.month).count()
    clients = Client.objects.filter()
    
    echeances = (Echeance.objects
        .filter(date_echeance__lte=today, status__etiquette = StatusPret.RETARD)
        .aggregate(
            nombre=Count("id"),
            montant_total=Sum("montant_a_payer")
        )
    )
    

    penalites = (Penalite.objects
        .filter(created_at__date__gte=start_month, created_at__date__lte=today)
        .aggregate(
            nombre=Count("id"),
            montant_total=Sum("montant")
        )
    )
    
    stats = (Transaction.objects
        .filter(created_at__date__gte=start_month, created_at__date__lte=today)
        .aggregate(
            # Remboursements
            remboursements_total=Sum(
                Case(
                    When(type_transaction__etiquette=TypeTransaction.REMBOURSEMENT, then="montant"),
                    output_field=DecimalField(),
                )
            ),

            # Dépôts
            depots_total=Sum(
                Case(
                    When(type_transaction__etiquette=TypeTransaction.DEPOT, then="montant"),
                    output_field=DecimalField(),
                )
            ),

            # Retraits
            retraits_total=Sum(
                Case(
                    When(type_transaction__etiquette=TypeTransaction.RETRAIT, then="montant"),
                    output_field=DecimalField(),
                )
            ),
        )
    )


    ctx = {
        'TITLE_PAGE' : "Tableau de bord",
        "prets": prets,
        "epargnes": epargnes,

        "clients": clients,
        "echeances_count": echeances["nombre"] or 0,
        "echeances_montant": echeances["montant_total"] or 0,
        
        "penalites_count": penalites["nombre"],
        "penalites_montant": penalites["montant_total"],
        
        "remboursements_montant": stats["remboursements_total"],
        "depots_montant": stats["depots_total"],
        "retraits_montant": stats["retraits_total"],
    }
    return ctx



@login_required()
@permission_classes([IsAuthenticated])
@render_to('MainApp/clients.html')
def clients_view(request):
    if not request.user.is_authenticated:
        return redirect('AuthentificationApp:login')
    
    clients = Client.objects.filter(agence=request.user.agence, deleted=False)
    ctx = {
        'TITLE_PAGE' : "Liste des souscripteurs",
        "clients": clients,
        "types": TypeClient.objects.all(),
        "genres": Genre.objects.all(),
        "particulier": TypeClient.objects.filter(etiquette = TypeClient.PARTICULIER).first(),
        "entreprise": TypeClient.objects.filter(etiquette = TypeClient.ENTREPRISE).first(),
    }
    return ctx


@login_required()
@render_to('MainApp/client.html')
def client_view(request, pk):
    if not request.user.is_authenticated:
        return redirect('AuthentificationApp:login')
    
    try:
        client = Client.objects.get(pk=pk, deleted=False)
        epargnes = CompteEpargne.objects.filter(client=client, status__etiquette = StatusPret.EN_COURS)
        prets = Pret.objects.filter(client=client, status__etiquette__in = [StatusPret.EN_COURS, StatusPret.EN_ATTENTE])
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
            "modalites": ModaliteEcheance.objects.all(),
        }
        return ctx
    except Exception as e:
        print("Erreur client_view: ", e)
        return redirect('MainApp:clients')



@render_to('MainApp/rapports.html')
def rapports_view(request):
    if not request.user.is_authenticated:
        return redirect('AuthentificationApp:login')
    
    ctx = {
        'TITLE_PAGE' : "Rapports Stats",
    }
    return ctx
