from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login
from rest_framework_simplejwt.tokens import RefreshToken
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from faker import Faker
from AuthentificationApp.models import Employe



def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }
    
    
    
@csrf_exempt
def login_ajax(request):
    try:
        if request.method == "POST":
            username = request.POST.get("username")
            password = request.POST.get("password")
            employe = authenticate(request, username=username, password=password)

            if employe is not None and not employe.is_superuser:
                if not employe.is_active:
                    return JsonResponse({'status': False, 'message': "L'accès est déjà refusé à cet employé, veuillez d'abord le débloquer !"})
                
                if employe.is_new:
                    request.session['user_id'] = str(employe.id)
                    return JsonResponse({'status': True, "is_new": employe.is_new, "id": employe.id})
                
                else:
                    login(request, employe)
                    tokens = get_tokens_for_user(employe)
                    request.session['access_token'] = tokens['access']
                    request.session.employe = employe
                    return JsonResponse({'status': True, "is_new": employe.is_new})
                
            else:
                return JsonResponse({'status': False, 'message': "Nom d'utilisateur ou mot de passe incorrect"})

        return JsonResponse({'message': 'Méthode non autorisée'}, status=405)
    
    except Exception as e:
        print("--------------------", e)
        return JsonResponse({"status": False, "message": str(e)})



@csrf_exempt
def first_user(request):
    if request.method == "POST":
        user_id   = request.session.get('user_id')
        username  = request.POST.get("username")
        password  = request.POST.get("password1")
        password1 = request.POST.get("password2")
        
        if password == "" or username == "":
            return JsonResponse({'status': False, 'message': "Le mot de passe et l'identifiant ne peuvent pas être vides"})
        elif password != password1:
            return JsonResponse({'status': False, 'message': "Les mots de passe ne correspondent pas"})
        elif len(password) < 8:
            return JsonResponse({'status': False, 'message': "Le mot de passe doit contenir au moins 8 caractères"})
        else:
            user = Employe.objects.filter(username=username).exclude(id = user_id).first()
            if user is not None and not user.is_superuser:
                return JsonResponse({'status': False, 'message': "Cet identifiant est déjà utilisé"})
            else:
                user = Employe.objects.filter(id = user_id).first()
                user.username = username
                user.set_password(password)
                user.is_new = False
                user.save()
                login(request, user)
                return JsonResponse({'status': True})
    
    return JsonResponse({'message': 'Méthode non autorisée'}, status=405)




@login_required
def reset_password(request):
    if request.method == "POST":
        datas = request.POST
        try:
            if request.user.is_employe():
                return JsonResponse({"status": False, "message": "Vous n'avez pas le droit de modifier le mot de passe !"})
            
            employe = Employe.objects.get(pk = datas["id"])
            if employe == request.user:
                return JsonResponse({"status":False, "message": "Vous ne pouvez pas modifier votre propre mot de passe !"})

            if "password" in datas and not request.user.check_password(datas["password"]):
                return JsonResponse({"status":False, "message": "Le mot de passe est incorrect !"})

            if employe.is_staff:
                return JsonResponse({"status": False, "message": "Vous ne pouvez pas supprimer cet utilisateur, il est protégé !"})
            if not employe.is_active:
                return JsonResponse({"status": False, "message": "L'accès est déjà refusé à cet employé, veuillez d'abord le débloquer !"})

            faker = Faker()
            employe.username = faker.user_name()
            employe.brut = faker.password(length=8, special_chars=False, digits=True, lower_case=False, upper_case=False)
            employe.is_new = True
            employe.set_password(employe.brut)
            employe.save()

            return JsonResponse({"status": True})

        except Exception as e:
            print("--------------------", e)
            return JsonResponse({"status": False, "message": "Une erreur s'est produite lors de l'opération, veuillez recommencer !"})
    