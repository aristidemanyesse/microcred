from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from annoying.decorators import render_to
from django.contrib.auth.decorators import login_required
from faker import Faker
from datetime import date, timedelta
from FinanceApp.models import CompteEpargne, Echeance, Interet, ModaliteEcheance, ModePayement, Penalite, Pret, StatusPret, Transaction, TypeTransaction
from MainApp.models import Agence, Client, Genre, TypeClient
from django.db.models import Count, Sum, Case, When, DecimalField
from django.utils.timezone import now
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from TresorApp.models import CompteAgence, Operation


@login_required()
@render_to('TresorApp/rapports.html')
def rapports_view(request):
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
