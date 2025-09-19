from django.shortcuts import render
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required, permission_required
from django.http import JsonResponse
import json, uuid
from django.urls import reverse
from settings import settings as parametres
from django.utils.translation import gettext as _


import CoreApp.tools as tools
from MainApp.forms import *

# Create your views here.
@login_required
def save(request):
    if request.method == "POST":
        datas = request.POST
        datas._mutable = True
        for key in datas:
            if datas[key] == "on": datas[key]=True

        try:
            modelform = datas["modelform"]
            MyForm = globals()[modelform]

            if (MyForm) :
                MyModel = tools.form_to_model(modelform)
                content_type = ContentType.objects.get(model= MyModel.lower())
                MyModel = content_type.model_class()
                if "id" in datas and datas["id"] != "":
                    obj = MyModel.objects.get(pk=datas["id"])
                    form = MyForm(datas, request.FILES, instance = obj)
                    # if modelform in ["EmployeForm", "LivreurForm", "ClientForm"]:
                    #     obj.user.first_name = obj.user.first_name if "first_name" not in datas else datas["first_name"]
                    #     obj.user.last_name = obj.user.last_name if "last_name" not in datas else datas["last_name"]
                    #     obj.user.save()
                        
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
            modelform = datas["model"]
            content_type = ContentType.objects.get(model= modelform.lower())
            MyModel = content_type.model_class()

            if "password" in datas and not request.user.check_password(datas["password"]):
                return JsonResponse({"status":False, "message": _("Le mot de passe est incorrect !")})

            obj = MyModel.objects.get(pk=datas["id"])
            if obj.proteger:
                return JsonResponse({"status":False, "message": _("Vous ne pouvez pas supprimer cet element, il est protégé !")})

            if hasattr(obj, "etat"):
                obj.etat = Etat.objects.get(etiquette = Etat.ANNULE)
            else:
                obj.supprimer = True
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
            modelform = datas["model"]
            content_type = ContentType.objects.get(model= modelform.lower())
            MyModel = content_type.model_class()

            obj = MyModel.objects.get(pk=datas["id"])
            if datas["model"] == "Employe":
                obj.user.is_active = not obj.user.is_active
                obj.user.save()
            else:
                obj.active = not obj.active
                obj.save()

            return JsonResponse({"status":True, "message": _("Suppression effectuée avec succes !")})

        except Exception as e:
            print("erreur save :", e)
            return JsonResponse({"status":False, "message": _("Erreur lors du processus. Veuillez recommencer : ")+str(e)})



def filter_date(request):
    if request.method == "POST":
        datas = request.POST
        request.session["date1"] = datas["debut"]
        request.session["date2"] = datas["fin"]
        return JsonResponse(dict(request.session))



def session(request):
    if request.method == "POST":
        datas = request.POST
        request.session[datas["name"]] = datas["value"]
        return JsonResponse(dict(request.session))



def delete_session(request):
    if request.method == "POST":
        datas = request.POST
        if datas["name"] in request.session:
            del request.session[datas["name"]]
        return JsonResponse(dict(request.session))
    



def change_language(request):
    if request.method == "POST":
        datas = request.POST
        request.session["language"] = datas["lang"]

    return HttpResponse("")