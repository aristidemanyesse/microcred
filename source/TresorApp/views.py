
# Create your views here.
from django.shortcuts import render, redirect
from annoying.decorators import render_to
from django.contrib.auth.decorators import login_required
from MainApp.models import Agence
from TresorApp.models import CompteAgence, Operation
from django.db.models import Q, Sum
from datetime import datetime, date, timedelta
from FinanceApp.models import CompteEpargne, Echeance, Interet, Penalite, Pret, StatusPret, Transaction, TypeTransaction
from FidelisApp.models import CompteFidelis
import pytz
utc=pytz.UTC


@login_required()
@render_to('TresorApp/compte.html')
def compte_view(request, pk):
    if not request.user.is_authenticated:
        return redirect('AuthentificationApp:login')
    
    if not request.user.is_chef():
        return redirect('MainApp:dashboard')
    
    compte = CompteAgence.objects.get(deleted = False, pk = pk)
    operations = Operation.objects.filter(deleted = False).filter(Q(compte_credit = compte) | Q(compte_debit = compte)).order_by("-created_at")
    agences = Agence.objects.all()
    ctx = {
        'TITLE_PAGE' : "Fiche de compte",
        "compte": compte,
        "agences": agences,
        "operations": operations,
    }
    return ctx




@render_to('TresorApp/releve_compte.html')
def releve_view(request, pk):
    if not request.user.is_authenticated:
        return redirect('AuthentificationApp:login')
    
    if not request.user.is_chef():
        return redirect('MainApp:dashboard')
    
    try:
        compte     = CompteAgence.objects.get(deleted = False, pk = pk)
        operations = Operation.objects.filter(deleted = False).filter(Q(compte_credit = compte) | Q(compte_debit = compte)).order_by("created_at")
        
        base = compte.base
        for operation in operations:
            if operation.compte_debit == compte:
                base -= operation.montant
            else:
                base += operation.montant
            operation.avoir = base
        operations = sorted(operations, key=lambda x: x.created_at, reverse=True)
        
        ctx = {
            'TITLE_PAGE': "Relevé de compte",
            "compte"    : compte,
            "operations": operations,
            "now"       : datetime.now(),
        }
        return ctx
    
    except Exception as e:
        print("Erreur invoice_view: ", e)
        return redirect('TresorApp:rapports')
    
    
    
    
@login_required()
@render_to('TresorApp/rapports.html')
def rapports_view(request, start=None, end=None):
    if not request.user.is_authenticated:
        return redirect('AuthentificationApp:login')
    
    if not request.user.is_chef():
        return redirect('MainApp:dashboard')
    
    start = datetime.strptime(start, '%Y-%m-%d') if start else datetime.strptime(str(date.today()), '%Y-%m-%d') - timedelta(days=7)
    start = utc.localize(start)
    end = datetime.strptime(end, '%Y-%m-%d') + timedelta(days=1) if end else datetime.now()
    end = utc.localize(end)
    request.session["start"] = start.isoformat()
    request.session["end"] = end.isoformat()
    

    prets = Pret.objects.filter(deleted = False, created_at__date__range = [start, end]).exclude(status__etiquette__in = [StatusPret.EN_ATTENTE, StatusPret.ANNULEE])
    new_comptes_pret = prets.count()
    total_montant_pret = prets.aggregate(total=Sum('base'))['total'] or 0
    transactions = Transaction.objects.filter(deleted = False, created_at__date__range = [start, end], type_transaction__etiquette = TypeTransaction.REMBOURSEMENT)
    total_recouvrements = transactions.aggregate(total=Sum('montant'))['total'] or 0
    total_recouvrements_attempts = Echeance.objects.filter(deleted = False, date_echeance__range = [start, end]).exclude(status__etiquette = StatusPret.ANNULEE).aggregate(total=Sum('montant_a_payer'))['total'] or 0
    total_beneficies_pret = 0
    total_penalites = 0
    for echeance in Echeance.objects.filter(deleted = False, id__in = transactions.values_list('echeance_id', flat=True)):
        total_beneficies_pret += echeance.interet if echeance.montant_paye > echeance.interet else echeance.montant_paye
    total_penalites = Penalite.objects.filter(deleted = False, created_at__date__range = [start, end]).aggregate(total=Sum('montant'))['total'] or 0
    total_beneficies_pret_previsionnels = Pret.objects.filter(deleted = False, created_at__date__range = [start, end]).exclude(status__etiquette__in = [StatusPret.EN_ATTENTE, StatusPret.ANNULEE]).aggregate(total=Sum('interet'))['total'] or 0
        
    new_comptes_epargnes = CompteEpargne.objects.filter(deleted = False, created_at__date__range = [start, end]).count()
    total_depots = Transaction.objects.filter(deleted = False, created_at__date__range = [start, end], type_transaction__etiquette = TypeTransaction.DEPOT).aggregate(total=Sum('montant'))['total'] or 0
    total_retraits = Transaction.objects.filter(deleted = False, created_at__date__range = [start, end], type_transaction__etiquette = TypeTransaction.RETRAIT).aggregate(total=Sum('montant'))['total'] or 0
    total_interets = Interet.objects.filter(deleted = False, created_at__date__range = [start, end]).aggregate(total=Sum('montant'))['total'] or 0
    total_beneficies_pret_previsionnels += total_interets
    
    new_comptes_fidelis = CompteFidelis.objects.filter(deleted = False, created_at__date__range = [start, end]).count()
    
    total_depots_fidelis = Transaction.objects.filter(deleted = False, created_at__date__range = [start, end], type_transaction__etiquette = TypeTransaction.DEPOT_FIDELIS).aggregate(total=Sum('montant'))['total'] or 0
    
    total_retraits_fidelis = Transaction.objects.filter(deleted = False, created_at__date__range = [start, end], type_transaction__etiquette = TypeTransaction.RETRAIT_FIDELIS).aggregate(total=Sum('montant'))['total'] or 0
    
    total_benefices_fidelis = CompteFidelis.objects.filter(deleted = False, cloture_at__date__range = [start, end]).aggregate(total=Sum('frais'))['total'] or 0
    
    total_benefices_fidelis_previsionnels = CompteFidelis.objects.filter(deleted = False, created_at__date__range = [start, end]).aggregate(total=Sum('frais'))['total'] or 0
    
    ctx = {
        'TITLE_PAGE' : "Rapports Stats",
        
        "new_comptes_pret"                     : new_comptes_pret,
        "total_recouvrements"                  : total_recouvrements,
        "total_montant_pret"                   : total_montant_pret,
        "total_beneficies_pret"                : total_beneficies_pret,
        "total_penalites"                      : total_penalites,
        "total_beneficies_net"                 : total_beneficies_pret + total_penalites,
        "total_beneficies_pret_previsionnels"  : total_beneficies_pret_previsionnels,
        
        "new_comptes_epargnes"                 : new_comptes_epargnes,
        "total_depots"                         : total_depots,
        "total_retraits"                       : total_retraits,
        "total_interets"                       : total_interets,
        
        "new_comptes_fidelis"                  : new_comptes_fidelis,
        "total_depots_fidelis"                 : total_depots_fidelis,
        "total_retraits_fidelis"               : total_retraits_fidelis,
        "total_benefices_fidelis"              : total_benefices_fidelis,
        "total_benefices_fidelis_previsionnels": total_benefices_fidelis_previsionnels,
        
        "start": start.strftime("%d/%m/%Y"),
        "end": end.strftime("%d/%m/%Y"),
    }
    return ctx
    
    
    
    
@login_required()
@render_to('TresorApp/tresorerie.html')
def tresorerie(request, start=None, end=None):
    if not request.user.is_authenticated:
        return redirect('AuthentificationApp:login')
    
    if not request.user.is_chef():
        return redirect('MainApp:dashboard')
    
    start = datetime.strptime(start, '%Y-%m-%d') if start else datetime.strptime(str(date.today()), '%Y-%m-%d') - timedelta(days=7)
    start = utc.localize(start)
    end = datetime.strptime(end, '%Y-%m-%d') + timedelta(days=1) if end else datetime.now()
    end = utc.localize(end)
    request.session["start"] = start.isoformat()
    request.session["end"] = end.isoformat()

    comptes = CompteAgence.objects.filter(deleted = False).order_by("created_at")
    operations = Operation.objects.filter(deleted = False, created_at__date__range = [start, end]).order_by("-created_at")
    
    comptes__ = []
    for compte in comptes:
        comptes__.append({
            "id"       : compte.id,
            "libelle"  : compte.libelle,
            "solde"    : compte.solde(),
            "depots"   : compte.total_depots(start, end),
            "retraits" : compte.total_retraits(start, end),
            "resultats": compte.solde(start, end),
        })
    
   
    ctx = {
        'TITLE_PAGE' : "Trésorerie ",
        "comptes": comptes,
        "comptes__": comptes__,
        "operations": operations,
        
        "start": start.strftime("%d/%m/%Y"),
        "end": end.strftime("%d/%m/%Y"),
    }
    return ctx
