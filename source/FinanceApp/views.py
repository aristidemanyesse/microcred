from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from annoying.decorators import render_to
from django.contrib.auth.decorators import login_required
from faker import Faker
from datetime import date, timedelta
from FinanceApp.models import CompteEpargne, Echeance, Interet, ModaliteEcheance, ModePayement, Penalite, Pret, StatusPret, Transaction
from django.core.paginator import Paginator



@render_to('FinanceApp/prets.html')
def prets_view(request):
    prets = Pret.objects.filter(status__etiquette = StatusPret.EN_COURS)
    ctx = {
        'TITLE_PAGE' : "Liste des prêts en cours",
        "prets": prets,
    }
    return ctx


@render_to('FinanceApp/simulateur_pret.html')
def prets_simulateur_view(request):
    if request.method == "GET":
        prets = Pret.objects.filter(status__etiquette = StatusPret.EN_COURS)
        modalites = ModaliteEcheance.objects.all()
        ctx = {
            'TITLE_PAGE' : "Simulateur de prêts",
            "prets": prets,
            "modalites": modalites,
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






@render_to('FinanceApp/simulateur_epargne.html')
def epargnes_simulateur_view(request):
    if request.method == "GET":
        epargnes = CompteEpargne.objects.filter(status__etiquette = StatusPret.EN_COURS)
        modalites = ModaliteEcheance.objects.all()
        ctx = {
            'TITLE_PAGE' : "Simulateur d'épargne",
            "epargnes": epargnes,
            "modalites": modalites,
        }
        return ctx
    
    elif request.method == "POST":
        base = int(request.POST.get("base"))
        taux = float(request.POST.get("taux"))
        modalite = request.POST.get("modalite")
        modalite = ModaliteEcheance.objects.get(pk=modalite)
        
        duree = request.POST.get("duree")
        modalite_duree = request.POST.get("modalite_duree")
        modalite_duree = ModaliteEcheance.objects.get(pk=modalite_duree)
        
        regulier = int(request.POST.get("regulier"))
        modalite_regulier = request.POST.get("modalite_regulier")
        modalite_regulier = ModaliteEcheance.objects.get(pk=modalite_regulier)
        
        duree_echeance = modalite.duree()
        duree_epargne = int(duree) * modalite_duree.duree()
        duree_approvisonnement = modalite_regulier.duree()
        
        start = date.today()
        next = date.today() + timedelta(days=duree_approvisonnement)
        tableaux = []
        base__ = base
        while start <= date.today() + timedelta(days=duree_epargne):
            total_regulier = 0
            while next <= start:
                total_regulier += regulier
                next += timedelta(days=duree_approvisonnement)
            
            tableaux.append({
                "date"    : start,
                "base"    : base__,
                "regulier": total_regulier,
                "total"   : base__ + total_regulier,
                "interet" : round((base__ + total_regulier) * taux/100, 2),
                "avoir"   : round((base__ + total_regulier + round((base__ + total_regulier) * taux/100, 2)), 2)
            })
            base__ = round((base__ + total_regulier + round((base__ + total_regulier) * taux/100, 2)), 2)
            start += timedelta(days=duree_echeance)
        
        ctx = {
            'TITLE_PAGE' : "Simulateur d'épargne",
            "base": base,
            "taux": taux,
            "regulier": regulier,
            "modalite": modalite,
            "duree": duree,
            "modalite_regulier": modalite_regulier,
            "modalite_duree": modalite_duree,
            "tableaux": tableaux,
            "modalites": ModaliteEcheance.objects.all(),
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
