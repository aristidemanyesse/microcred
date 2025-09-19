from django.db import models
from annoying.decorators import signals
from datetime import date, timedelta
from CoreApp.tools import GenerateTools
from CoreApp.models import BaseModel 
# Create your models here.
class Agence(BaseModel):
    libelle     = models.CharField(max_length=100)
    adresse = models.TextField()
    ville   = models.CharField(max_length=50)
    code    = models.CharField(max_length=10, unique=True)


class TypeClient(BaseModel):
    PARTICULIER = 1
    ENTREPRISE = 2
    libelle = models.CharField(max_length=50)  # Physique / Morale
    etiquette = models.CharField(max_length=50)
    

class Genre(BaseModel):
    HOMME = 1
    FEMME = 2
    libelle = models.CharField(max_length=10)  # Homme / Femme
    etiquette = models.CharField(max_length=50)
    

class Client(BaseModel):
    numero         = models.CharField(max_length=50, null=True, blank=True, unique=True)
    agence         = models.ForeignKey(Agence, on_delete=models.CASCADE)
    type_client    = models.ForeignKey(TypeClient, on_delete=models.CASCADE)
    nom            = models.CharField(max_length=200)
    prenoms        = models.CharField(max_length=200, null=True, blank=True)
    genre          = models.ForeignKey(Genre, null=True, blank=True, on_delete=models.CASCADE)
    date_naissance = models.DateField(null=True, blank=True)
    profession     = models.TextField()
    adresse        = models.TextField()
    telephone      = models.CharField(max_length=20)
    email          = models.EmailField(null=True, blank=True)
    employe      = models.ForeignKey('AuthentificationApp.Employe', on_delete=models.CASCADE, related_name='clients')
    
    def __str__(self):
        return f"{self.prenoms or ''} {self.nom or ''}"
    
    def is_actif(self):
        ladate = date.today() - timedelta(days=360)
        return self.transactions.filter(created_at__gte = ladate).exists()
    
    def total_epargne(self):
        return sum(compte.solde for compte in self.epargnes.all())

    def total_prets_en_cours(self):
        return sum(pret.montant - pret.montant_rembourse for pret in self.pret_set.all() if pret.status.li.lower() == 'en cours')

    def total_penalites(self):
        return sum(penalite.montant for pret in self.pret_set.all() for penalite in pret.penalite_set.all())




@signals.pre_save(sender=Client)
def sighandler(instance, **kwargs):
    if instance._state.adding:
        instance.numero = GenerateTools.clientId(instance.agence)
