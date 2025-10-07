
# Create your views here.
from django.shortcuts import render, redirect
from annoying.decorators import render_to
from django.contrib.auth.decorators import login_required
from MainApp.models import Agence
from TresorApp.models import CompteAgence, Operation
from django.db.models import Q, Sum
from datetime import datetime, date, timedelta

from FinanceApp.models import CompteEpargne, Echeance, Interet, Pret, StatusPret, Transaction, TypeTransaction


@login_required()
@render_to('TresorApp/compte.html')
def compte_view(request, pk):
    if not request.user.is_authenticated:
        return redirect('AuthentificationApp:login')
    
    if request.user.is_employe():
        return redirect('MainApp:dashboard')
    
    compte = CompteAgence.objects.get(pk = pk)
    operations = Operation.objects.filter(Q(compte_credit = compte) | Q(compte_debit = compte)).order_by("-created_at")
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
    
    if request.user.is_employe():
        return redirect('MainApp:dashboard')
    
    try:
        compte     = CompteAgence.objects.get(pk = pk)
        operations = Operation.objects.filter(Q(compte_credit = compte) | Q(compte_debit = compte)).order_by("created_at")
        
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
    
    if request.user.is_employe():
        return redirect('MainApp:dashboard')
    
    start = datetime.strptime(start, '%Y-%m-%d').date() or date.today() - timedelta(days=7)
    end = datetime.strptime(end, '%Y-%m-%d').date() or date.today()

    comptes = CompteAgence.objects.filter().order_by("created_at")
    operations = Operation.objects.filter(created_at__range = [start, end]).order_by("created_at")
    
    comptes__ = []
    for compte in comptes:
        comptes__.append({
            "libelle": compte.libelle,
            "depots": compte.total_depots(start, end),
            "retraits": compte.total_retraits(start, end),
            "solde": compte.solde(start, end),
        })
    
    transactions = Transaction.objects.filter(created_at__range = [start, end], type_transaction__etiquette = TypeTransaction.REMBOURSEMENT)
    new_comptes_pret = Pret.objects.filter(created_at__range = [start, end], status__etiquette = StatusPret.EN_COURS).count()
    total_recouvrements = transactions.aggregate(total=Sum('montant'))['total'] or 0
    total_recouvrements_attempts = Echeance.objects.filter(date_echeance__range = [start, end]).exclude(status__etiquette = StatusPret.ANNULEE).aggregate(total=Sum('montant_a_payer'))['total'] or 0
    total_beneficies_pret = 0
    for echeance in Echeance.objects.filter(id__in = transactions.values_list('echeance_id', flat=True)):
        total_beneficies_pret += echeance.interet if echeance.montant_paye > echeance.interet else echeance.montant_paye
        
        
    new_comptes_epargnes = CompteEpargne.objects.filter(created_at__range = [start, end], status__etiquette = StatusPret.EN_COURS).count()
    total_depots = Transaction.objects.filter(created_at__range = [start, end], type_transaction__etiquette = TypeTransaction.DEPOT).aggregate(total=Sum('montant'))['total'] or 0
    total_retraits = Transaction.objects.filter(created_at__range = [start, end], type_transaction__etiquette = TypeTransaction.RETRAIT).aggregate(total=Sum('montant'))['total'] or 0
    total_interets = Interet.objects.filter(created_at__range = [start, end]).aggregate(total=Sum('montant'))['total'] or 0
    
    ctx = {
        'TITLE_PAGE' : "Rapports Stats",
        "comptes": comptes,
        "comptes__": comptes__,
        "operations": operations,
        
        "new_comptes_pret": new_comptes_pret,
        "total_recouvrements": total_recouvrements,
        "total_recouvrements_attempts": total_recouvrements_attempts,
        "total_beneficies_pret" : total_beneficies_pret,
        
        "new_comptes_epargnes": new_comptes_epargnes,
        "total_depots": total_depots,
        "total_retraits": total_retraits,
        "total_interets": total_interets,
        
        "start": start.strftime("%d/%m/%Y"),
        "end": end.strftime("%d/%m/%Y"),
    }
    return ctx
