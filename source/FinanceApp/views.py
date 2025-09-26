from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from annoying.decorators import render_to
from django.contrib.auth.decorators import login_required
from faker import Faker
from datetime import date, timedelta
from FinanceApp.models import CompteEpargne, Echeance, Interet, ModePayement, Penalite, Pret, StatusPret, Transaction
from django.core.paginator import Paginator



@render_to('FinanceApp/prets.html')
def prets_view(request):
    prets = Pret.objects.filter(status__etiquette = StatusPret.EN_COURS)
    ctx = {
        'TITLE_PAGE' : "Liste des prêts en cours",
        "prets": prets,
    }
    return ctx


@render_to('FinanceApp/demandes.html')
def demandes_view(request):
    prets = Pret.objects.filter(status__etiquette = StatusPret.EN_ATTENTE)
    paginator = Paginator(prets, 20)
    
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    
    ctx = {
        'TITLE_PAGE' : "Liste des demandes de prêts",
        "prets": page_obj,
        "page_obj": page_obj,
    }
    return ctx


@render_to('FinanceApp/echeances.html')
def echeances_view(request):
    today = date.today()
    echeances = Echeance.objects.filter(date_echeance__range = [today - timedelta(days=3), today + timedelta(days=5)]).exclude(status__etiquette__in = [StatusPret.ANNULEE, StatusPret.TERMINE]).order_by("-date_echeance")
    ctx = {
        'TITLE_PAGE' : "Liste des rétards d'échéances",
        "echeances": echeances,
    }
    return ctx



@render_to('FinanceApp/pret.html')
def pret_view(request, pk):
    try:
        pret = Pret.objects.get(pk=pk)
        echeances = Echeance.objects.filter(pret=pret).order_by("level")
        penalites = Penalite.objects.filter(echeance__pret=pret)
        transactions = Transaction.objects.filter(echeance__pret=pret).order_by("-created_at")
        modes = ModePayement.objects.all()
        ctx = {
            'TITLE_PAGE'  : "Fiche de prêt",
            "pret"        : pret,
            "echeances"   : echeances,
            "penalites"   : penalites,
            "transactions": transactions,
            "modes": modes,
        }
        return ctx
    except Exception as e:
        print("Erreur pret_view: ", e)
        return redirect('FinanceApp:prets')    


@render_to('FinanceApp/epargnes.html')
def epargnes_view(request):
    epargnes = CompteEpargne.objects.filter(status__etiquette = StatusPret.EN_COURS)
    ladate = date.today() - timedelta(days=3)
    ctx = {
        'TITLE_PAGE' : "Liste des comptes épargnes",
        "epargnes": epargnes,
        "ladate": ladate,
    }
    return ctx


@render_to('FinanceApp/epargne.html')
def epargne_view(request, pk):
    try:
        epargne = CompteEpargne.objects.get(pk=pk)
        transactions = epargne.transactions.filter().order_by("-created_at")
        interets = epargne.interets.filter().order_by("-created_at")
        ctx = {
            'TITLE_PAGE' : "Fiche compte épargne",
            "epargne": epargne,
            "transactions": transactions,
            "interets": interets,
            "modes": ModePayement.objects.all(),
        }
        return ctx
    except Exception as e:
        print("Erreur epargne_view: ", e)   
        return redirect('FinanceApp:epargnes') 
