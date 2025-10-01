from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from annoying.decorators import render_to
from django.contrib.auth.decorators import login_required
from MainApp.models import Agence
from TresorApp.models import CompteAgence, Operation


@login_required()
@render_to('TresorApp/rapports.html')
def rapports_view(request):
    if not request.user.is_authenticated:
        return redirect('AuthentificationApp:login')
    
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
