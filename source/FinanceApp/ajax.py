from django.http import JsonResponse
from FinanceApp.models import ModePayement, Pret, StatusPret

    
    
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
                    paye = paye if paye <= montant else montant
                    echeance.regler(paye, request.user, ModePayement.objects.get(pk=mode), commentaire)
                    montant -= paye
                
                return JsonResponse({"status": True, "message": "Remboursement effectué avec succès !"})
            
        except Exception as e:
            print("--------------------", e)
            return JsonResponse({"status": False, "message": "Une erreur s'est produite lors de l'opération, veuillez recommencer !"})
                


