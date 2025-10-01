from django.shortcuts import render
from django.db.models import Sum
# Create your views here.
from django.shortcuts import render, redirect
from annoying.decorators import render_to
from django.contrib.auth.decorators import login_required
from faker import Faker
from datetime import date, timedelta
from FinanceApp.models import CompteEpargne, Echeance, Interet, ModaliteEcheance, ModePayement, Penalite, Pret, StatusPret, Transaction
from django.core.paginator import Paginator
from datetime import datetime


@render_to('FinanceApp/prets.html')
def prets_view(request):
    prets = Pret.objects.filter(status__etiquette = StatusPret.EN_COURS)
    status = StatusPret.objects.all()
    ctx = {
        'TITLE_PAGE' : "Liste des prêts en cours",
        "prets": prets,
        "status": status,
    }
    return ctx


@render_to('FinanceApp/simulateur_prets.html')
def prets_simulateur_view(request):
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
        
        duree = request.POST.get("duree")
        modalite_duree = request.POST.get("modalite_duree", None)
        modalite_duree = ModaliteEcheance.objects.get(pk=modalite_duree)
        
        
        tableaux = []
        total_reglement = 0
        total = base * (1 + taux/100)
        echeance = round(total / int(duree), 2)
        i = 0
        while i < int(duree):
            total_reglement += echeance
            reste = round(total - total_reglement, 2)
            tableaux.append({
                "base"    : base,
                "taux"    : taux,
                "total"   : total,
                
                "date"    : date.today() + timedelta(days=(i+1) * modalite_duree.duree()),
                "echeance": echeance if reste > 0 else (echeance + reste),
                "reste"   : reste if reste > 0 else 0,
            })
            i+=1
            
        if reste > 0:
            tableaux[-1]["echeance"] += reste
            tableaux[-1]["reste"] = 0
        
        ctx = {
            'TITLE_PAGE' : "Simulateur d'épargne",
            "base": base,
            "taux": taux,
            "duree": duree,
            "modalite_duree": modalite_duree,
            "tableaux": tableaux,
            "modalites": ModaliteEcheance.objects.all(),
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
    echeances = Echeance.objects.filter(date_echeance__range = [today - timedelta(days=5), today + timedelta(days=5)]).exclude(status__etiquette__in = [StatusPret.ANNULEE, StatusPret.TERMINE]).order_by("date_echeance")
    status = StatusPret.objects.all()
    ctx = {
        'TITLE_PAGE' : "Liste des rétards d'échéances",
        "echeances": echeances,
        "status": status,
    }
    return ctx


@render_to('FinanceApp/invoice.html')
def invoice(request, pk):
    try:
        transaction = Transaction.objects.get(pk = pk)
        avance = 0
        penalite = 0
        total = 0
        reste = 0
        if transaction.echeance:
            penalite = transaction.echeance.penalites_montant()
            avance = transaction.echeance.transactions.filter(created_at__lt = transaction.created_at).aggregate(total=Sum('montant'))['total'] or 0
            total = transaction.echeance.montant_a_payer + penalite - avance
            reste = total - transaction.montant

        ctx = {
            'TITLE_PAGE' : "Réçu de transaction",
            "transaction": transaction,
            "avance": avance,
            "penalite": penalite,
            "total": total,
            "reste": reste,
            "now": datetime.now(),
        }
        return ctx
    
    except Exception as e:
        print("Erreur invoice_view: ", e)
        return redirect('FinanceApp:prets')




@render_to('FinanceApp/releve_pret.html')
def releve_pret(request, pk):
    try:
        pret = Pret.objects.get(pk = pk)
        echeances = pret.echeances.filter(status__etiquette = StatusPret.TERMINE).order_by("level")
        reste = pret.echeances.exclude(status__etiquette__in = [StatusPret.TERMINE, StatusPret.ANNULEE]).count()
        ctx = {
            'TITLE_PAGE' : "Réçu de transaction",
            "pret" : pret,
            "echeances": echeances,
            "reste": reste,
            "now": datetime.now(),
        }
        return ctx
    
    except Exception as e:
        print("Erreur invoice_view: ", e)
        return redirect('FinanceApp:prets')





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




@render_to('FinanceApp/releve_epargne.html')
def releve_epargne(request, pk):
    try:
        epargne = CompteEpargne.objects.get(pk = pk)
        transactions = epargne.transactions.filter()
        interets = epargne.interets.filter()
        items = list(transactions) + list(interets)
        sorted(items, key=lambda x: x.created_at)
        
        
        datas = []
        base = 0
        for item in items:
            if type(item) == Interet:
                base += item.montant
                datas.append({
                    "type" : "Interet",
                    "title" : f"Intérêt {epargne.modalite} de {epargne.taux}% payé",
                    "montant" : item.montant,
                    "avoir": round(base, 2),
                    "created_at" : item.created_at,
                })
            else:
                base = (base + item.montant) if item.type_transaction.etiquette == "1" else (base - item.montant)
                datas.append({
                    "type" : "Transaction",
                    "title" : f"{item.type_transaction} N°{item.numero}",
                    "montant" : item.montant,
                    "avoir": round(base, 2),
                    "created_at" : item.created_at,
                })
                
        ctx = {
            'TITLE_PAGE' : "Réçu de transaction",
            "epargne" : epargne,
            "datas": datas,
            "now": datetime.now(),
        }
        return ctx
    
    except Exception as e:
        print("Erreur invoice_view: ", e)
        return redirect('FinanceApp:epargnes')
    


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
            
            interet = 0 if start == date.today() else round((base__ + total_regulier) * taux/100, 2)
            tableaux.append({
                "date"    : start,
                "base"    : base__,
                "regulier": total_regulier,
                "total"   : round(base__ + total_regulier, 2),
                "interet" : interet,
                "avoir"   : round((base__ + total_regulier + interet), 2)
            })
            base__ = round((base__ + total_regulier + interet), 2)
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
