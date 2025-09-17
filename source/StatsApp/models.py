from django.db import models
from MainApp.models import Agence, Client


# Create your models here.
class Rapport(models.Model):
    titre           = models.CharField(max_length=200)
    date_generation = models.DateTimeField(auto_now_add=True)
    fichier         = models.FileField(upload_to='rapports/')
    agence          = models.ForeignKey(Agence, null=True, blank=True, on_delete=models.SET_NULL)
    type_rapport    = models.CharField(max_length=50)  # ex: Clients, Prêts, Épargne


    def generate(self, type_rapport, agence=None):
        """Génération du rapport selon type et agence"""
        # Exemple : clients, prêts, épargne
        if type_rapport.lower() == 'clients':
            qs = Client.objects.all()
            if agence:
                qs = qs.filter(agence=agence)
            # générer fichier et l’enregistrer dans self.fichier
        # similaire pour prêts et épargne
        self.type_rapport = type_rapport
        self.save()