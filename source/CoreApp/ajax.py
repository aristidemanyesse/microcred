from django.shortcuts import render
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required, permission_required
from django.http import JsonResponse
import json, uuid
from django.urls import reverse
from settings import settings as parametres
from django.utils.translation import gettext as _
from datetime import datetime
from faker import Faker
import CoreApp.tools as tools
from MainApp.forms import *
from FinanceApp.forms import *
from AuthentificationApp.forms import *
from TresorApp.forms import *
from FinanceApp.models import StatusPret

# Create your views here.
@login_required
def save(request):
    if request.method == "POST":
        datas = request.POST
        datas._mutable = True

        for key in datas:
            if datas[key] == "on": datas[key]=True

        if "base" in datas: datas["base"] = float(datas["base"].replace(" ", ""))
        if "taux" in datas: datas["taux"] = float(datas["taux"].replace(" ", "").replace(",", "."))
        if "taux_penalite" in datas: datas["taux_penalite"] = float(datas["taux_penalite"].replace(" ", "").replace(",", "."))
        if "montant" in datas: datas["montant"] = float(datas["montant"].replace(" ", ""))
        
        try:
            modelform = datas["modelform"]
            MyForm = globals()[modelform]

            if (MyForm) :
                MyModel = tools.form_to_model(modelform)
                content_type = ContentType.objects.get(model= MyModel.lower())
                MyModel = content_type.model_class()
                if modelform in ["EmployeForm"] and "id" not in datas:
                    faker = Faker()
                    psd = faker.password(length=8, special_chars=False, digits=True, upper_case=False, lower_case=True)
                    datas["username"] = faker.user_name()
                    datas["password"] = psd
                    datas["brut"] = psd
                    datas["date_joined"] = datetime.now()
                    
                if "id" in datas and datas["id"] != "":
                    obj = MyModel.objects.get(pk=datas["id"])
                    form = MyForm(datas, request.FILES, instance = obj)
                        
                else:
                    datas["id"] = str(uuid.uuid4())
                    form = MyForm(datas, request.FILES)
                    
                    
                

                if form.is_valid():
                    if 'image' in request.FILES and request.FILES["image"] != "":
                        image = request.FILES.get('image')
                        form.image = image

                    item = form.save()
                    if modelform == "ClientForm":
                        return JsonResponse({"status":True, "url" : reverse("MainApp:client", args=[item.id])})
                    if modelform == "LivreurForm":
                        return JsonResponse({"status":True, "url" : reverse("LivraisonApp:livreur_detail", args=[item.id])})
                    return JsonResponse({"status":True, "message": "Opération effectuée avec succes !"})
                
                else:
                    errors = form.errors.get_json_data()
                    errors_values = list((list(errors.values())[0][0]).values())
                    errors_keys = list(errors.keys())
                    return JsonResponse({"status":False, "message":"{} : {}".format(errors_keys[0], errors_values[0])})
                
            # return JsonResponse({"status":False, "message": _("Le formulaire n'est pas valide !")})
        except Exception as e:
            print("erreur save eryu :", e)
            return JsonResponse({"status":False, "message": _("Erreur lors du processus. Veuillez recommencer : ")+str(e)})



@login_required
def mise_a_jour(request):
    if request.method == "POST":
        datas = request.POST
        datas._mutable = True
        for key in datas:
            if datas[key] == "on": 
                datas[key]=True

        try:
            if (datas["model"]) != "":
                modelform = datas["model"]
                content_type = ContentType.objects.get(model= modelform.lower())
                MyModel = content_type.model_class()

                item = MyModel.objects.get(pk=datas["id"])

                mydict = item.__dict__
                del mydict["_state"]
                del mydict["id"]
                mydict[datas["name"]] = datas["val"]
                MyModel.objects.filter(pk=datas["id"]).update(**mydict)

                return JsonResponse({"status": True})

        except Exception as e:
            print("--------------------", e)
            return JsonResponse({"status": False, "message": _("Une erreur s'est produite lors de l'opération, veuillez recommencer !")})



@login_required
def supprimer(request):
    if request.method == "POST":
        datas = request.POST
        try:
            if request.user.is_employe():
                return JsonResponse({"status": False, "message": "Vous n'avez pas le droit de supprimer cet élément !"})
            
            modelform = datas["model"]
            content_type = ContentType.objects.get(model= modelform.lower())
            MyModel = content_type.model_class()

            if "password" in datas and not request.user.check_password(datas["password"]):
                return JsonResponse({"status":False, "message": _("Le mot de passe est incorrect !")})

            obj = MyModel.objects.get(pk=datas["id"])
            if obj.protected:
                return JsonResponse({"status":False, "message": _("Vous ne pouvez pas supprimer cet element, il est protégé !")})

            if hasattr(obj, "etat"):
                obj.status = StatusPret.objects.get(etiquette = StatusPret.ANNULE)
            else:
                obj.deleted = True
            obj.save()
            return JsonResponse({"status":True, "message": _("Suppression effectuée avec succes !")})

        except Exception as e:
            print("erreur save :", e)
            return JsonResponse({"status":False, "message": _("Erreur lors du processus. Veuillez recommencer : ")+str(e)})



@login_required
def change_active(request):
    if request.method == "POST":
        datas = request.POST

        try:
            if request.user.is_employe():
                return JsonResponse({"status": False, "message": "Vous n'avez pas le droit de modifier l'état de cet élément !"})
            
            modelform = datas["model"]
            content_type = ContentType.objects.get(model= modelform.lower())
            MyModel = content_type.model_class()
            
            if "password" in datas and not request.user.check_password(datas["password"]):
                return JsonResponse({"status":False, "message": _("Le mot de passe est incorrect !")})

            obj = MyModel.objects.get(pk=datas["id"])
            if datas["model"] == "Employe":
                if obj == request.user:
                    return JsonResponse({"status": False, "message": "Vous ne pouvez pas bloquer votre propre compte !"})
                
                obj.is_active = not obj.is_active
                obj.save()
            else:
                obj.active = not obj.active
                obj.save()

            return JsonResponse({"status":True, "message": _("Suppression effectuée avec succes !")})

        except Exception as e:
            print("erreur save :", e)
            return JsonResponse({"status":False, "message": _("Erreur lors du processus. Veuillez recommencer : ")+str(e)})



def refresh_password(request):
    if request.method == "POST":
        try:
            if request.user.is_employe():
                return JsonResponse({"status": False, "message": "Vous n'avez pas le droit de modifier le mot de passe !"})
            
            datas = request.POST
            faker = Faker()
            psd = faker.password(length=8, special_chars=False, digits=True, upper_case=False, lower_case=True)
            
            if "password" in datas and not request.user.check_password(datas["password"]):
                return JsonResponse({"status":False, "message": _("Le mot de passe est incorrect !")})
            
            employe = Employe.objects.get(pk=datas["id"])
            employe.brut = psd
            employe.is_new = True
            employe.username = faker.user_name()
            employe.set_password(psd)
            employe.save()
            return JsonResponse({"status": True})
        except Exception as e:
            print("Erreur refresh_password : ", e)
            return JsonResponse({"status": False, "message": _("Une erreur s'est produite lors de l'opération, veuillez recommencer !")})