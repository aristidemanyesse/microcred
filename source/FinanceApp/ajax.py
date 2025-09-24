from django.http import JsonResponse
from FinanceApp.models import CompteEpargne, ModePayement, Pret, StatusPret
from AuthentificationApp.models import Employe

    
    
def new_remboursement(request):
    if request.method == "POST":
        if not request.user.is_authenticated:
            return JsonResponse({"status": False, "message": "Vous devez être connecté pour effectuer ce remboursement !"})
        
        id = request.POST.get("id")
        mode = request.POST.get("mode")
        commentaire = request.POST.get("commentaire")
        
        try:
            montant = int(request.POST.get("montant")) 
            pret = Pret.objects.get(pk=id)
            if pret.status.etiquette == StatusPret.EN_COURS:
                if montant > pret.reste_a_payer():
                    return JsonResponse({"status": False, "message": "Le montant de remboursement est supérieur au montant restant à payer !"})
                if montant <= 0:
                    return JsonResponse({"status": False, "message": "Le montant de remboursement doit être supérieur à 0 !"})
                
                while montant > 0:
                    echeance = pret.echeances.filter(status__etiquette = StatusPret.EN_COURS).order_by("level").first()
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
            datas = request.POST
            pret = Pret.objects.get(pk=datas["pret_id"])
            pret.status = StatusPret.objects.get(etiquette = StatusPret.EN_COURS)
            pret.confirmateur = Employe.objects.get(pk=request.user.id) 
            pret.save()
            return JsonResponse({"status": True, "message": "Prêt validé avec succès !"})
        except Exception as e:
            print("--------------------", e)
            return JsonResponse({"status": False, "message": str(e)})
        
        

def new_depot(request):
    if request.method == "POST":
        try:
            datas = request.POST
            epargne = CompteEpargne.objects.get(pk=datas["id"])
            mode = ModePayement.objects.get(pk=datas["mode"])
            commentaire = datas["commentaire"]
            montant = int(datas["montant"])
            
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
            datas = request.POST
            epargne = CompteEpargne.objects.get(pk=datas["id"])
            mode = ModePayement.objects.get(pk=datas["mode"])
            commentaire = datas["commentaire"]
            montant = int(datas["montant"])
            
            if epargne.solde_actuel >= montant:
                epargne.retirer(montant, request.user, mode, commentaire)
                return JsonResponse({"status": True, "message": "Retrait effectué avec succès !"})
            else:
                return JsonResponse({"status": False, "message": "Le solde du compte est insuffisant pour ce retrait."})
        except Exception as e:
            print("--------------------", e)
            return JsonResponse({"status": False, "message": str(e)})