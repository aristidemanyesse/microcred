
# Create your views here.
from django.shortcuts import render, redirect
from annoying.decorators import render_to
from django.contrib.auth.decorators import login_required
from MainApp.models import Agence
from TresorApp.models import CompteAgence, Operation
from django.db.models import Q
from datetime import datetime


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
def rapports_view(request):
    if not request.user.is_authenticated:
        return redirect('AuthentificationApp:login')
    
    if request.user.is_employe():
        return redirect('MainApp:dashboard')
    
    comptes = CompteAgence.objects.filter().order_by("created_at")
    agences = Agence.objects.all()
    operations = Operation.objects.filter().order_by("-created_at")
    ctx = {
        'TITLE_PAGE' : "Rapports Stats",
        "comptes": comptes,
        "agences": agences,
        "operations": operations,
    }
    return ctx
