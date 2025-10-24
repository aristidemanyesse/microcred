from datetime import timedelta
import decimal
from django.http import JsonResponse
from FinanceApp.models import CompteEpargne, Echeance, ModePayement, Pret, StatusPret, Transaction, TypeTransaction
from AuthentificationApp.models import Employe
from django.db.models import Sum
from rest_framework.decorators import api_view
from django.http import JsonResponse
from django.db.models import Sum, Case, When, DecimalField
from django.db.models.functions import TruncMonth
from django.utils.timezone import now
from dateutil.relativedelta import relativedelta
import calendar

    
def new_remboursement(request):
    if request.method == "POST":
        if not request.user.is_authenticated:
            return JsonResponse({"status": False, "message": "Vous devez être connecté pour effectuer ce remboursement !"})
        
        if request.user.is_gestionnaire_epargne():
            return JsonResponse({"status": False, "message": "Vous n'avez pas le droit de faire un remboursement !"})
        
        id = request.POST.get("id")
        mode = request.POST.get("mode")
        commentaire = request.POST.get("commentaire")
        
        try:
            montant = decimal.Decimal(request.POST.get("montant").replace(" ", "").replace(",", "."))
            pret = Pret.objects.get(pk=id)
            print( pret.reste_a_payer())

            if pret.status.etiquette == StatusPret.EN_COURS:
                if montant > pret.reste_a_payer():
                    return JsonResponse({"status": False, "message": "Le montant de remboursement est supérieur au montant restant à payer !"})
                if montant <= 0:
                    return JsonResponse({"status": False, "message": "Le montant de remboursement doit être supérieur à 0 !"})
                
                while montant > 0:
                    echeance = pret.echeances.filter(status__etiquette = StatusPret.EN_COURS).order_by("level").first()
                    if echeance is None:
                        break
                    paye = echeance.montant_restant()
                    if paye <= 0:
                        echeance.status = StatusPret.objects.get(etiquette = StatusPret.TERMINE)
                        echeance.save()
                        continue
                    paye = paye if paye <= montant else montant
                    echeance.regler(paye, request.user, ModePayement.objects.get(pk=mode), commentaire)
                    montant -= paye
                
                return JsonResponse({"status": True, "message": "Remboursement effectué avec succès !"})
            
        except Exception as e:
            print("--------------------", e)
            return JsonResponse({"status": False, "message": str(e)})
                


def confirm_pret(request):
    if request.method == "POST":
        try:
            if not request.user.is_chef():
                return JsonResponse({"status": False, "message": "Vous n'avez pas le droit de valider ce prêt !"})
            
            datas = request.POST
            pret  = Pret.objects.get(pk=datas["pret_id"])
            pret.confirm_pret(request.user)
            
            return JsonResponse({"status": True, "message": "Prêt validé avec succès !"})
        except Exception as e:
            print("--------------------", e)
            return JsonResponse({"status": False, "message": str(e)})
        


def decaissement(request):
    if request.method == "POST":
        try:
            if not request.user.is_chef():
                return JsonResponse({"status": False, "message": "Vous n'avez pas le droit de valider ce prêt !"})
            
            datas = request.POST
            pret  = Pret.objects.get(pk=datas["pret_id"])
            pret.decaissement(request.user)
            
            return JsonResponse({"status": True, "message": "Décaissement du prêt effectué avec succès !"})
        except Exception as e:
            print("--------------------", e)
            return JsonResponse({"status": False, "message": str(e)})
        
        

def new_depot(request):
    if request.method == "POST":
        try:
            if request.user.is_gestionnaire_pret():
                return JsonResponse({"status": False, "message": "Vous n'avez pas le droit de déposer de l'argent !"})
            
            datas       = request.POST
            epargne     = CompteEpargne.objects.get(pk=datas["id"])
            mode        = ModePayement.objects.get(pk=datas["mode"])
            commentaire = datas["commentaire"]
            montant     = decimal.Decimal(datas["montant"].replace(" ", ""))
            
            if montant > 0:
                epargne.deposer(montant, request.user, mode, commentaire)
                return JsonResponse({"status": True, "message": "Dépot effectué avec succès !"})
            else:
                return JsonResponse({"status": False, "message": "Le montant de dépot doit être supérieur à 0."})
        except Exception as e:
            print("--------------------", e)
            return JsonResponse({"status": False, "message": str(e)})
        
        
        
def new_retrait(request):
    if request.method == "POST":
        try:
            if request.user.is_gestionnaire_pret():
                return JsonResponse({"status": False, "message": "Vous n'avez pas le droit de retirer de l'argent !"})
            
            datas = request.POST
            epargne = CompteEpargne.objects.get(pk=datas["id"])
            mode = ModePayement.objects.get(pk=datas["mode"])
            commentaire = datas["commentaire"]
            montant = decimal.Decimal(datas["montant"].replace(" ", ""))
            
            if epargne.solde_actuel >= montant:
                epargne.retirer(montant, request.user, mode, commentaire)
                return JsonResponse({"status": True, "message": "Retrait effectué avec succès !"})
            else:
                return JsonResponse({"status": False, "message": "Le solde du compte est insuffisant pour ce retrait."})
        except Exception as e:
            print("--------------------", e)
            return JsonResponse({"status": False, "message": str(e)})
        
        
        
@api_view(['GET'])
def stats_finance(request):
    today = now().date()
    start_date = (today.replace(day=1) - relativedelta(months=11))

    # Récupération groupée
    qs = (Transaction.objects
            .filter(created_at__gte=start_date, created_at__lte=today + timedelta(days=1))
            .annotate(month=TruncMonth("created_at"))
            .values("month")
            .annotate(
                depots=Sum(
                    Case(
                        When(type_transaction__etiquette=TypeTransaction.DEPOT, then="montant"),
                        default=0,
                        output_field=DecimalField(),
                    )
                ),
                retraits=Sum(
                    Case(
                        When(type_transaction__etiquette=TypeTransaction.RETRAIT, then="montant"),
                        default=0,
                        output_field=DecimalField(),
                    )
                ),
                remboursements=Sum(
                    Case(
                        When(type_transaction__etiquette=TypeTransaction.REMBOURSEMENT, then="montant"),
                        default=0,
                        output_field=DecimalField(),
                    )
                ),
                depot_fidelis=Sum(
                    Case(
                        When(type_transaction__etiquette=TypeTransaction.DEPOT_FIDELIS, then="montant"),
                        default=0,
                        output_field=DecimalField(),
                    )
                ),
                retrait_fidelis=Sum(
                    Case(
                        When(type_transaction__etiquette=TypeTransaction.RETRAIT_FIDELIS, then="montant"),
                        default=0,
                        output_field=DecimalField(),
                    )
                ),
          )
          .order_by("month")
    )

    # Indexer les résultats par mois pour lookup rapide
    results_map = {row["month"].strftime("%Y-%m"): row for row in qs}

    # Générer 12 mois consécutifs
    results = []
    for i in range(12):
        month_date = (start_date + relativedelta(months=i))
        key = month_date.strftime("%Y-%m")
        label = month_date.strftime("%b %Y")  # ex: "Sep 2025"

        row = results_map.get(key, None)
        results.append({
            "mois": label,
            "depots": float(row["depots"] if row else 0),
            "retraits": float(row["retraits"] if row else 0),
            "remboursements": float(row["remboursements"] if row else 0),
            "depot_fidelis": float(row["depot_fidelis"] if row else 0), 
            "retrait_fidelis": float(row["retrait_fidelis"] if row else 0),
        })

    return JsonResponse(results, safe=False)
