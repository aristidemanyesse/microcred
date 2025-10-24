from django.shortcuts import render
from django.db.models import Sum, Q
# Create your views here.
from django.shortcuts import render, redirect
from annoying.decorators import render_to
from django.contrib.auth.decorators import login_required
from faker import Faker
from datetime import date, timedelta
from FinanceApp.models import CompteEpargne, Echeance, Garantie, Interet, ModaliteEcheance, ModePayement, Penalite, Pret, StatusPret, Transaction, TypeAmortissement, TypeTransaction
from django.core.paginator import Paginator
from datetime import datetime


@render_to('FinanceApp/prets.html')
def prets_view(request):
    if not request.user.is_authenticated:
        return redirect('AuthentificationApp:login')
    
    if request.user.is_gestionnaire_epargne():
        return redirect('MainApp:dashboard')
    
    prets = Pret.objects.filter(status__etiquette = StatusPret.EN_COURS)
    status = StatusPret.objects.all()
    
    total = prets.aggregate(total=Sum('montant'))['total'] or 0
    rembourses = 0
    for pret in prets:
        rembourses += pret.montant_rembourse()
        
    reste_a_payer = total - rembourses
    
    ctx = {
        'TITLE_PAGE' : "Liste des prêts en cours",
        "prets": prets,
        "status": status,
        "total": total,
        "rembourses": rembourses,
        "reste_a_payer": reste_a_payer,
    }
    return ctx



@render_to('FinanceApp/pret.html')
def pret_view(request, pk):
    if not request.user.is_authenticated:
        return redirect('AuthentificationApp:login')
    
    if request.user.is_gestionnaire_epargne():
        return redirect('MainApp:dashboard')
    
    try:
        pret         = Pret.objects.get(pk=pk)
        echeances    = Echeance.objects.filter(pret=pret).order_by("level")
        penalites    = Penalite.objects.filter(echeance__pret=pret)
        transactions = Transaction.objects.filter(echeance__pret=pret).order_by("-created_at")
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
        print("Erreur pret_view: ", e)
        return redirect('FinanceApp:prets')    





@render_to('FinanceApp/archivage_prets.html')
def archivage_prets(request):
    if not request.user.is_authenticated:
        return redirect('AuthentificationApp:login')
    
    if request.user.is_gestionnaire_epargne():
        return redirect('MainApp:dashboard')
    
    prets = Pret.objects.filter(status__etiquette__in = [StatusPret.ANNULEE, StatusPret.TERMINE])
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
        epargnes = CompteEpargne.objects.filter(status__etiquette = StatusPret.EN_COURS)
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
                reste = base - (principal * (i+1))
                tableaux.append({
                    "taux"     : taux,
                    "principal": principal,
                    "interet"  : interet,
                    "total"    : principal + interet,
                    
                    "date"     : date.today() + timedelta(days=(i+1) * modalite_duree.duree()),
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

                tableaux.append({
                    "taux": taux,
                    "principal": round(principal, 2),
                    "interet": round(interet, 2),
                    "total": round(annuite, 2),
                    "date": date.today() + timedelta(days=periode * modalite_duree.duree()),
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
    
    prets = Pret.objects.filter(status__etiquette = StatusPret.EN_ATTENTE)
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
            avance = transaction.echeance.transactions.filter(created_at__lt = transaction.created_at).aggregate(total=Sum('montant'))['total'] or 0
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
        print("Erreur invoice_view: ", e)
        return redirect('FinanceApp:prets')




@render_to('FinanceApp/releve_pret.html')
def releve_pret(request, pk):
    if not request.user.is_authenticated:
        return redirect('AuthentificationApp:login')
    
    if request.user.is_gestionnaire_epargne():
        return redirect('MainApp:dashboard')

    try:
        pret = Pret.objects.get(pk = pk)
        echeances = pret.echeances.filter(Q(status__etiquette = StatusPret.TERMINE) | Q(montant_paye__gt = 0)).order_by("level")
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



@render_to('FinanceApp/epargnes.html')
def epargnes_view(request):
    if not request.user.is_authenticated:
        return redirect('AuthentificationApp:login')
    
    if request.user.is_gestionnaire_pret():
        return redirect('MainApp:dashboard')
        
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
    if not request.user.is_authenticated:
        return redirect('AuthentificationApp:login')
    
    if request.user.is_gestionnaire_pret():
        return redirect('MainApp:dashboard')
    
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




@render_to('FinanceApp/archivage_epargnes.html')
def archivage_epargnes(request):
    if not request.user.is_authenticated:
        return redirect('AuthentificationApp:login')
    
    if request.user.is_gestionnaire_pret():
        return redirect('MainApp:dashboard')
        
    epargnes = CompteEpargne.objects.filter(status__etiquette__in = [StatusPret.ANNULEE, StatusPret.TERMINE])
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
        
        epargne = CompteEpargne.objects.get(pk = pk)
        transactions = epargne.transactions.filter().order_by('created_at')
        interets = epargne.interets.filter().order_by('created_at')
        items = list(transactions) + list(interets)
        sorted(items, key=lambda x: x.created_at)
        
        
        datas = []
        base = 0
        for item in items:
            print(item.created_at)
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
        print("Erreur invoice_view: ", e)
        return redirect('FinanceApp:epargnes')
    


@render_to('FinanceApp/simulateur_epargne.html')
def epargnes_simulateur_view(request):
    if not request.user.is_authenticated:
        return redirect('AuthentificationApp:login')
    
    if request.user.is_gestionnaire_pret():
        return redirect('MainApp:dashboard')
    
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



