import logging
from decimal import Decimal
from datetime import date, datetime, timedelta

from django.shortcuts import render, redirect
from django.db.models import Sum, Q
from django.db.models.functions import Coalesce
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from annoying.decorators import render_to

from FinanceApp.models import (
    CompteEpargne, Echeance, Garantie, Interet, ModaliteEcheance,
    ModePayement, Penalite, Pret, StatusPret, Transaction,
    TypeAmortissement, TypeTransaction,
)
from TresorApp.models import CompteAgence, TypeActivity

logger = logging.getLogger(__name__)


@render_to('FinanceApp/prets.html')
def prets_view(request):
    if not request.user.is_authenticated:
        return redirect('AuthentificationApp:login')
    
    if request.user.is_gestionnaire_epargne():
        return redirect('MainApp:dashboard')
    
    prets = Pret.objects.filter(status__etiquette = StatusPret.EN_COURS, deleted = False)
    valides = Pret.objects.filter(status__etiquette = StatusPret.VALIDE, deleted = False)
    status = StatusPret.objects.all()
    
    total = prets.aggregate(total=Sum('montant'))['total'] or 0
    rembourses = 0
    for pret in prets:
        rembourses += pret.montant_rembourse()
    reste_a_payer = total - rembourses
    
    cash = (
    Transaction.objects
        .filter(
            type_transaction__etiquette__in=[TypeTransaction.REMBOURSEMENT, TypeTransaction.OCTROIE_PRET],
            deleted=False
        )
        .aggregate(
            enc=Coalesce(Sum("montant", filter=Q(type_transaction__etiquette=TypeTransaction.REMBOURSEMENT)), Decimal("0.00")),
            dec=Coalesce(Sum("montant", filter=Q(type_transaction__etiquette=TypeTransaction.OCTROIE_PRET)),  Decimal("0.00")),
        )
    )
    cash_net = cash["enc"] - cash["dec"]

    profit = (
        Transaction.objects
        .filter(type_transaction__etiquette=TypeTransaction.REMBOURSEMENT, deleted=False)
        .aggregate(
            interets=Coalesce(Sum("interet_part"), Decimal("0.00")),
            penalites=Coalesce(Sum("penalite_part"), Decimal("0.00")),
        )
    )
    profit_reel = profit["interets"] + profit["penalites"]
    
    comptes = CompteAgence.objects.filter(activity__etiquette=TypeActivity.PRET)
    if request.user.agence:
        comptes = comptes.filter(agence=request.user.agence)
    compte = comptes.first()
    
    today = date.today()
    impayes = Echeance.objects.filter(deleted = False, date_echeance__lt = today).exclude(status__etiquette__in = [StatusPret.ANNULEE, StatusPret.TERMINE]).order_by("date_echeance")

    ctx = {
        'TITLE_PAGE' : "Liste des prêts en cours",
        "prets": valides.union(prets),
        "status": status,
        "profit_reel": profit_reel,
        "solde": compte.solde() if compte else 0,
        "reste_a_payer": reste_a_payer,
        "impayes": impayes.aggregate(total=Sum('montant_a_payer') - Sum('montant_paye'))['total'] or 0,
    }
    return ctx



@render_to('FinanceApp/pret.html')
def pret_view(request, pk):
    if not request.user.is_authenticated:
        return redirect('AuthentificationApp:login')
    
    if request.user.is_gestionnaire_epargne():
        return redirect('MainApp:dashboard')
    
    try:
        pret         = Pret.objects.get(pk=pk, deleted = False)
        echeances    = Echeance.objects.filter(pret=pret, deleted = False).order_by("level")
        penalites    = Penalite.objects.filter(echeance__pret=pret, deleted = False)
        transactions = Transaction.objects.filter(echeance__pret=pret, deleted = False).order_by("-created_at")
        modes        = ModePayement.objects.all()
        garanties    = Garantie.objects.filter(pret=pret, deleted = False)
        ctx = {
            'TITLE_PAGE'  : "Fiche de prêt",
            "pret"        : pret,
            "echeances"   : echeances,
            "penalites"   : penalites,
            "transactions": transactions,
            "modes"       : modes,
            "garanties"   : garanties,
        }
        return ctx
    except Exception as e:
        logger.exception("Erreur pret_view pk=%s", pk)
        return redirect('FinanceApp:prets')





@render_to('FinanceApp/archivage_prets.html')
def archivage_prets(request):
    if not request.user.is_authenticated:
        return redirect('AuthentificationApp:login')
    
    if request.user.is_gestionnaire_epargne():
        return redirect('MainApp:dashboard')
    
    prets = Pret.objects.filter(deleted = False, status__etiquette__in = [StatusPret.ANNULEE, StatusPret.TERMINE])
    status = StatusPret.objects.all()
    ctx = {
        'TITLE_PAGE' : "Archives des prêts en cours",
        "prets": prets,
        "status": status,
    }
    return ctx




@render_to('FinanceApp/simulateur_prets.html')
def prets_simulateur_view(request):
    if not request.user.is_authenticated:
        return redirect('AuthentificationApp:login')
    
    if request.user.is_gestionnaire_epargne():
        return redirect('MainApp:dashboard')
    
    if request.method == "GET":
        epargnes = CompteEpargne.objects.filter(deleted = False, status__etiquette = StatusPret.EN_COURS)
        modalites = ModaliteEcheance.objects.all()
        ctx = {
            'TITLE_PAGE' : "Simulateur d'épargne",
            "epargnes": epargnes,
            "modalites": modalites,
            "amortissements": TypeAmortissement.objects.all(),
        }
        return ctx
    
    elif request.method == "POST":
        base = int(request.POST.get("base").replace(" ", ""))
        taux = float(request.POST.get("taux").replace(" ", "").replace(",", "."))
        
        duree = int(request.POST.get("duree"))
        modalite_duree = request.POST.get("modalite_duree", None)
        modalite_duree = ModaliteEcheance.objects.get(pk=modalite_duree)
        amortissement = request.POST.get("amortissement", None)
        amortissement = TypeAmortissement.objects.get(pk=amortissement)
        
        
        tableaux = []
        total_a_payer = base * (1 + taux/100)
        total_reglement = 0
        total_interets = 0
        i = 0
        
        if amortissement.etiquette == TypeAmortissement.BASE:
            principal = round(base / duree, 2)
            interet = round(principal * taux / 100, 2)
            while i < duree:
                date_echeance = date.today()
                for _ in range(i+1):
                    date_echeance += modalite_duree.duree()
                    
                reste = base - (principal * (i+1))
                tableaux.append({
                    "taux"     : taux,
                    "principal": principal,
                    "interet"  : interet,
                    "total"    : principal + interet,
                    "date"     : date_echeance,
                    "reste"    : reste,
                    "total_a_payer"   : total_a_payer,
                })
                total_reglement += principal + interet
                total_interets += interet
                i+=1
            
  
        
        elif amortissement.etiquette == TypeAmortissement.ANNUITE:
            i = taux / 100 / modalite_duree.duree_par_annee()  # taux d'intérêt par année
            n = duree           # nombre de périodes
            r = i / (1 - (1 + i) ** -n)
            annuite = round(base * r, 2)
            reste = base

            for periode in range(1, n + 1):
                interet = reste * i
                principal = annuite - interet
                reste = reste - principal
                
                date_echeance = date.today()
                for _ in range(periode):
                    date_echeance += modalite_duree.duree()

                tableaux.append({
                    "taux": taux,
                    "principal": round(principal, 2),
                    "interet": round(interet, 2),
                    "total": round(annuite, 2),
                    "date": date_echeance,
                    "reste": round(reste, 2),
                })
                total_reglement += round(annuite, 2)
                total_interets += round(interet, 2)
            
            if reste != 0:
                tableaux[-1]["interet"] += round(reste, 2)
                tableaux[-1]["total"] += round(reste, 2)
                tableaux[-1]["reste"] = 0
        
        ctx = {
            'TITLE_PAGE'     : "Simulateur de prêt",
            "base"           : base,
            "total_interets" : total_interets,
            "total_reglement": total_reglement,
            "taux"           : taux,
            "duree"          : duree,
            "modalite_duree" : modalite_duree,
            "tableaux"       : tableaux,
            "modalites"      : ModaliteEcheance.objects.all(),
            "amortissements" : TypeAmortissement.objects.all(),
            "amortissement"  : amortissement,
        }
        return ctx
    
    
    

@render_to('FinanceApp/demandes.html')
def demandes_view(request):
    if not request.user.is_authenticated:
        return redirect('AuthentificationApp:login')
    
    if request.user.is_gestionnaire_epargne():
        return redirect('MainApp:dashboard')
    
    prets = Pret.objects.filter(deleted = False, status__etiquette = StatusPret.EN_ATTENTE)
    total = prets.aggregate(total=Sum('base'))['total'] or 0
    paginator = Paginator(prets, 20)
    
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    
    ctx = {
        'TITLE_PAGE' : "Liste des demandes de prêts",
        "prets": page_obj,
        "page_obj": page_obj,
        "total": total,
    }
    return ctx


@render_to('FinanceApp/echeances.html')
def echeances_view(request):
    if not request.user.is_authenticated:
        return redirect('AuthentificationApp:login')
    
    if request.user.is_gestionnaire_epargne():
        return redirect('MainApp:dashboard')
    
    today = date.today()
    echeances = Echeance.objects.filter(deleted = False, date_echeance__range = [today, today + timedelta(days=7)]).exclude(status__etiquette__in = [StatusPret.ANNULEE, StatusPret.TERMINE]).order_by("date_echeance")
    status = StatusPret.objects.all()
    ctx = {
        'TITLE_PAGE' : "Liste des échéances à venir",
        "echeances": echeances,
        "status": status,
    }
    return ctx


@render_to('FinanceApp/impayes.html')
def impayes_view(request):
    if not request.user.is_authenticated:
        return redirect('AuthentificationApp:login')
    
    if request.user.is_gestionnaire_epargne():
        return redirect('MainApp:dashboard')
    
    today = date.today()
    impayes = Echeance.objects.filter(deleted = False, date_echeance__lt = today).exclude(status__etiquette__in = [StatusPret.ANNULEE, StatusPret.TERMINE]).order_by("date_echeance")
    status = StatusPret.objects.all()
    ctx = {
        'TITLE_PAGE' : "Liste des impayés",
        "impayes": impayes,
        "status": status,
    }
    return ctx


@render_to('FinanceApp/invoice.html')
def invoice(request, pk):
    if not request.user.is_authenticated:
        return redirect('AuthentificationApp:login')
    
    try:
        transaction = Transaction.objects.get(pk = pk)
        avance = 0
        penalite = 0
        total = 0
        reste = 0
        if transaction.echeance:
            if request.user.is_gestionnaire_epargne():
                return redirect('MainApp:dashboard')
            
            penalite = transaction.echeance.penalites_montant()
            avance = transaction.echeance.transactions.filter(deleted = False, created_at__lt = transaction.created_at).aggregate(total=Sum('montant'))['total'] or 0
            total = transaction.echeance.montant_a_payer + penalite - avance
            reste = total - transaction.montant
        else:
            if request.user.is_gestionnaire_pret():
                return redirect('MainApp:dashboard')

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
        logger.exception("Erreur invoice pk=%s", pk)
        return redirect('FinanceApp:prets')


@render_to('FinanceApp/releve_pret.html')
def releve_pret(request, pk):
    if not request.user.is_authenticated:
        return redirect('AuthentificationApp:login')

    if request.user.is_gestionnaire_epargne():
        return redirect('MainApp:dashboard')

    try:
        pret = Pret.objects.get(pk=pk)
        echeances = pret.echeances.filter(deleted=False).filter(
            Q(status__etiquette=StatusPret.TERMINE) | Q(montant_paye__gt=0)
        ).order_by("level")
        reste = pret.echeances.filter(deleted=False).exclude(
            status__etiquette__in=[StatusPret.TERMINE, StatusPret.ANNULEE]
        ).count()
        ctx = {
            'TITLE_PAGE': "Réçu de transaction",
            "pret":       pret,
            "echeances":  echeances,
            "reste":      reste,
            "now":        datetime.now(),
        }
        return ctx

    except Exception as e:
        logger.exception("Erreur releve_pret pk=%s", pk)
        return redirect('FinanceApp:prets')



@render_to('FinanceApp/epargnes.html')
def epargnes_view(request):
    if not request.user.is_authenticated:
        return redirect('AuthentificationApp:login')
    
    if request.user.is_gestionnaire_pret():
        return redirect('MainApp:dashboard')
        
    epargnes = CompteEpargne.objects.filter(deleted = False, status__etiquette = StatusPret.EN_COURS)
    ladate = date.today() - timedelta(days=3)
    ctx = {
        'TITLE_PAGE' : "Liste des comptes épargnes",
        "epargnes": epargnes,
        "ladate": ladate,
    }
    return ctx


@render_to('FinanceApp/epargne.html')
def epargne_view(request, pk):
    if not request.user.is_authenticated:
        return redirect('AuthentificationApp:login')
    
    if request.user.is_gestionnaire_pret():
        return redirect('MainApp:dashboard')
    
    try:
        epargne = CompteEpargne.objects.get(deleted = False, pk=pk)
        transactions = epargne.transactions.filter(deleted = False).order_by("-created_at")
        interets = epargne.interets.filter(deleted = False).order_by("-created_at")
        ctx = {
            'TITLE_PAGE' : "Fiche compte épargne",
            "epargne": epargne,
            "transactions": transactions,
            "interets": interets,
            "modes": ModePayement.objects.all(),
        }
        return ctx
    except Exception as e:
        logger.exception("Erreur epargne_view pk=%s", pk)
        return redirect('FinanceApp:epargnes')




@render_to('FinanceApp/archivage_epargnes.html')
def archivage_epargnes(request):
    if not request.user.is_authenticated:
        return redirect('AuthentificationApp:login')
    
    if request.user.is_gestionnaire_pret():
        return redirect('MainApp:dashboard')
        
    epargnes = CompteEpargne.objects.filter(deleted = False, status__etiquette__in = [StatusPret.ANNULEE, StatusPret.TERMINE])
    ladate = date.today() - timedelta(days=3)
    ctx = {
        'TITLE_PAGE' : "Archives des comptes épargnes",
        "epargnes": epargnes,
        "ladate": ladate,
    }
    return ctx




@render_to('FinanceApp/releve_epargne.html')
def releve_epargne(request, pk):
    try:
        if not request.user.is_authenticated:
            return redirect('AuthentificationApp:login')
        
        if request.user.is_gestionnaire_pret():
            return redirect('MainApp:dashboard')
        
        epargne = CompteEpargne.objects.get(deleted = False, pk = pk)
        transactions = epargne.transactions.filter(deleted = False).order_by('created_at')
        interets = epargne.interets.filter(deleted = False).order_by('created_at')
        items = sorted(list(transactions) + list(interets), key=lambda x: x.created_at)

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
                base = (base + item.montant) if item.type_transaction.etiquette == TypeTransaction.DEPOT else (base - item.montant)
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
        logger.exception("Erreur releve_epargne pk=%s", pk)
        return redirect('FinanceApp:epargnes')
    


@render_to('FinanceApp/simulateur_epargne.html')
def epargnes_simulateur_view(request):
    if not request.user.is_authenticated:
        return redirect('AuthentificationApp:login')
    
    if request.user.is_gestionnaire_pret():
        return redirect('MainApp:dashboard')
    
    if request.method == "GET":
        epargnes = CompteEpargne.objects.filter(deleted = False, status__etiquette = StatusPret.EN_COURS)
        modalites = ModaliteEcheance.objects.all()
        ctx = {
            'TITLE_PAGE' : "Simulateur d'épargne",
            "epargnes": epargnes,
            "modalites": modalites,
        }
        return ctx
    
    elif request.method == "POST":
        base = int(request.POST.get("base").replace(" ", ""))
        taux = float(request.POST.get("taux").replace(" ", "").replace(",", "."))
        
        modalite = request.POST.get("modalite")
        modalite = ModaliteEcheance.objects.get(pk=modalite)
        
        duree = request.POST.get("duree")
        modalite_duree = request.POST.get("modalite_duree")
        modalite_duree = ModaliteEcheance.objects.get(pk=modalite_duree)
        
        regulier = int(request.POST.get("regulier").replace(" ", ""))
        modalite_regulier = request.POST.get("modalite_regulier")
        modalite_regulier = ModaliteEcheance.objects.get(pk=modalite_regulier)
        
        duree_echeance = (date.today() - date.today() + modalite.duree()).days
        duree_epargne = int(duree) * (date.today() - date.today() + modalite_duree.duree()).days
        duree_approvisonnement = (date.today() - date.today() + modalite_regulier.duree()).days 
        
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



