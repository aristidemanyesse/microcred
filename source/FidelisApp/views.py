from django.shortcuts import render, redirect
from annoying.decorators import render_to
from datetime import datetime
from FidelisApp.models import CompteFidelis
from FinanceApp.models import ModePayement, StatusPret, TypeTransaction
from django.db.models import Q
# Create your views here.


@render_to('FidelisApp/comptes.html')
def comptes(request):
    if not request.user.is_authenticated:
        return redirect('AuthentificationApp:login')
    
    if request.user.is_gestionnaire_epargne():
        return redirect('MainApp:dashboard')
    
    comptes = CompteFidelis.objects.filter(deleted = False).filter(Q(status__etiquette = StatusPret.EN_COURS) | Q(retire=False))
    payes = sum([compte.nombre_paye()*compte.base for compte in comptes])
    reste = sum([compte.nombre * compte.base for compte in comptes]) - payes
    
    ctx = {
        'TITLE_PAGE' : "Liste des comptes Fidelis",
        "comptes": comptes,
        "payes": payes,
        "reste": reste,
    }
    
    return ctx



@render_to('FidelisApp/compte.html')
def compte_view(request, pk):
    try:
        if not request.user.is_authenticated:
            return redirect('AuthentificationApp:login')
        
        if request.user.is_gestionnaire_epargne():
            return redirect('MainApp:dashboard')
        
        compte       = CompteFidelis.objects.get(pk = pk, deleted = False)
        transactions = compte.transactions.filter(deleted = False)
        cases        = compte.cases.filter(status__etiquette = StatusPret.TERMINE, deleted = False)
        payes        = range(compte.nombre_paye())
        data         = range(compte.nombre - compte.nombre_paye())
        
        ctx = {
            'TITLE_PAGE'  : "Fiche compte Fidelis",
            "compte"      : compte,
            "cases"       : cases,
            "data"        : data,
            "payes"       : payes,
            "transactions": transactions,
            "modes"       : ModePayement.objects.all(),
        }
        return ctx
    
    except Exception as e:
        print("Erreur : ", str(e))
        return redirect('FidelisApp:comptes')




@render_to('FidelisApp/archives.html')
def archivage(request):
    if not request.user.is_authenticated:
        return redirect('AuthentificationApp:login')
    
    if request.user.is_gestionnaire_epargne():
        return redirect('MainApp:dashboard')

    comptes = CompteFidelis.objects.filter(deleted = False).filter(Q(status__etiquette = StatusPret.ANNULEE) | Q(status__etiquette = StatusPret.TERMINE, retire=True))
    ctx = {
        'TITLE_PAGE' : "Archives des comptes Fidelis",
        "comptes": comptes,
    }
    
    return ctx




@render_to('FidelisApp/releve_fidelis.html')
def releve_view(request, pk):
    try:
        if not request.user.is_authenticated:
            return redirect('AuthentificationApp:login')
        
        if request.user.is_gestionnaire_epargne():
            return redirect('FidelisApp:comptes')
    
        compte = CompteFidelis.objects.get(pk = pk, deleted = False)
        transactions = compte.transactions.filter(deleted = False).order_by('created_at')
        
        
        datas = []
        base = 0
        for item in transactions:
            base = (base + item.montant) if item.type_transaction.etiquette == TypeTransaction.DEPOT_FIDELIS else (base - item.montant)
            datas.append({
                "type" : "Transaction",
                "title" : f"{item.type_transaction} | {item.numero}",
                "montant" : item.montant,
                "avoir": round(base, 2),
                "created_at" : item.created_at,
            })
        
        ctx = {
            'TITLE_PAGE' : "Relévé de compte Fidelis",
            "compte": compte,
            "datas": datas,
            "modes": ModePayement.objects.all(),
            "now" : datetime.now(),
        }
        return ctx
    
    except Exception as e:
        print("Error : ", str(e))
        return redirect('FidelisApp:comptes')