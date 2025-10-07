from django.http import JsonResponse
from FinanceApp.models import  ModePayement
from django.http import JsonResponse

from FidelisApp.models import CompteFidelis

def new_depot(request):
    if request.method == "POST":
        try:
            if request.user.is_gestionnaire_pret():
                return JsonResponse({"status": False, "message": "Vous n'avez pas le droit de déposer de l'argent !"})
            
            datas       = request.POST
            compte      = CompteFidelis.objects.get(pk=datas["id"])
            mode        = ModePayement.objects.get(pk=datas["mode"])
            commentaire = datas["commentaire"]
            
            compte.deposer(request.user, mode, commentaire)
            return JsonResponse({"status": True, "message": "Dépot effectué avec succès !"})
        
        except Exception as e:
            print("--------------------", e)
            return JsonResponse({"status": False, "message": str(e)})
        
        
        
def new_retrait(request):
    if request.method == "POST":
        try:
            if request.user.is_gestionnaire_pret():
                return JsonResponse({"status": False, "message": "Vous n'avez pas le droit de retirer de l'argent !"})
            
            datas       = request.POST
            compte      = CompteFidelis.objects.get(pk=datas["id"])
            mode        = ModePayement.objects.get(pk=datas["mode"])
            commentaire = datas["commentaire"]
            
            compte.retirer(request.user, mode, commentaire)
            return JsonResponse({"status": True, "message": "Retrait effectué avec succès !"})
        
        except Exception as e:
            print("--------------------", e)
            return JsonResponse({"status": False, "message": str(e)})
        
        
        
        
        
  