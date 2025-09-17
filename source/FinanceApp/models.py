from django.db import models
from annoying.decorators import signals
from MainApp.models import Client
from CoreApp.tools import GenerateTools
from CoreApp.models import BaseModel
from datetime import timedelta
from dateutil.relativedelta import relativedelta

# Create your models here.
class CompteEpargne(BaseModel):
    numero       = models.CharField(max_length=50)
    client        = models.ForeignKey(Client, on_delete=models.CASCADE)
    date_creation = models.DateField(auto_now_add=True)
    
    def __str__(self):
        return f"Epargne N°{self.numero}"
    
    def deposer(self, montant):
        Transaction.objects.create(
            compte=self,
            type_transaction=TypeTransaction.objects.get(etiquette = TypeTransaction.DEPOT), 
            montant=montant
        )

    def retirer(self, montant):
        if self.solde() >= montant:
            Transaction.objects.create(
                compte=self,
                type_transaction=TypeTransaction.objects.get(etiquette = TypeTransaction.RETRAIT),
                montant=montant
            )
        else:
            raise ValueError("Solde insuffisant")
        
    
    def solde(self):
        depots = Transaction.objects.filter(compte=self, type_transaction__etiquette= TypeTransaction.DEPOT).aggregate(total=models.Sum('montant'))['total'] or 0
        retraits = Transaction.objects.filter(compte=self, type_transaction__etiquette = TypeTransaction.RETRAIT).aggregate(total=models.Sum('montant'))['total'] or 0
        return depots - retraits
        

class Interet(BaseModel):
    compte        = models.ForeignKey(CompteEpargne, on_delete=models.CASCADE)
    montant       = models.DecimalField(max_digits=12, decimal_places=2)
    description   = models.TextField(null=True, blank=True)


class TypeTransaction(BaseModel):
    DEPOT = 1
    RETRAIT = 2
    libelle = models.CharField(max_length=50)  # Dépôt / Retrait
    etiquette = models.CharField(max_length=50)
    

class Transaction(BaseModel):
    numero       = models.CharField(max_length=50)
    compte           = models.ForeignKey(CompteEpargne, on_delete=models.CASCADE)
    type_transaction = models.ForeignKey(TypeTransaction, on_delete=models.CASCADE)
    montant          = models.DecimalField(max_digits=12, decimal_places=2)
    date_transaction = models.DateTimeField(auto_now_add=True)
    commentaire      = models.TextField(null=True, blank=True)



class StatutPret(BaseModel):
    ANNULEE = 0
    EN_COURS = 1
    TERMINE = 2
    RETARD = 3
    libelle = models.CharField(max_length=50)  # En cours / Terminé / Retard
    etiquette = models.CharField(max_length=50)
    
    


class ModaliteEcheance(BaseModel):
    HEBDOMADAIRE = "1"
    MENSUEL = "2"
    BIMENSUEL = "3"
    TRIMESTRIEL = "4"
    SEMESTRIEL = "5"
    ANNUEL = "6"
    libelle = models.CharField(max_length=50) 
    etiquette = models.CharField(max_length=50)
    
    

class Pret(BaseModel):
    numero          = models.CharField(max_length=50)
    client          = models.ForeignKey(Client, on_delete=models.CASCADE)
    base            = models.DecimalField(max_digits=12, decimal_places=2)
    taux            = models.DecimalField(max_digits=5, decimal_places=2)
    montant         = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    modalite        = models.ForeignKey(ModaliteEcheance, on_delete=models.CASCADE)
    nombre_modalite = models.PositiveIntegerField()
    statut          = models.ForeignKey(StatutPret, on_delete=models.CASCADE)
    
    def montant_restant(self):
        return self.montant - self.montant_rembourse

    def appliquer_paiement(self, montant):
        """Applique un paiement sur le prêt et sur les échéances et pénalités"""
        # Trier les échéances par date
        for echeance in self.echeance_set.order_by('date_echeance'):
            if montant <= 0:
                break
            # Appliquer d’abord sur les pénalités
            for penalite in echeance.penalite_set.all():
                if montant >= penalite.montant:
                    montant -= penalite.montant
                    penalite.montant = 0
                    penalite.save()
                else:
                    penalite.montant -= montant
                    penalite.save()
                    montant = 0
            # Appliquer sur l’échéance
            restant = echeance.montant_a_payer - echeance.montant_paye
            if montant >= restant:
                echeance.montant_paye = echeance.montant_a_payer
                echeance.statut = StatutPret.objects.get(nom='OK')
                echeance.save()
                montant -= restant
            else:
                echeance.montant_paye += montant
                echeance.statut = StatutPret.objects.get(nom='Partiellement payé')
                echeance.save()
                montant = 0
        # Mettre à jour montant remboursé du prêt
        self.montant_rembourse = sum(e.montant_paye for e in self.echeance_set.all())
        # Mise à jour statut du prêt
        if self.montant_rembourse >= self.montant:
            self.statut = StatutPret.objects.get(nom='Terminé')
        elif self.echeance_set.filter(statut__nom='En retard').exists():
            self.statut = StatutPret.objects.get(nom='Retard')
        else:
            self.statut = StatutPret.objects.get(nom='En cours')
        self.save()

    def calcul_penalites(self, taux=0.02):
        """Calcul automatique des pénalités sur les échéances en retard"""
        from datetime import date
        for echeance in self.echeance_set.all():
            if echeance.date_echeance < date.today() and echeance.montant_paye < echeance.montant_a_payer:
                # calcul par semaine de retard
                semaines_retard = (date.today() - echeance.date_echeance).days // 7
                montant_penalite = echeance.montant_a_payer * taux * semaines_retard
                # créer ou mettre à jour la pénalité
                penalite, created = Penalite.objects.get_or_create(pret=self, echeance=echeance)
                penalite.montant = montant_penalite
                penalite.save()


    

class Echeance(BaseModel):
    pret            = models.ForeignKey(Pret, on_delete=models.CASCADE)
    date_echeance   = models.DateField()
    montant_a_payer = models.DecimalField(max_digits=12, decimal_places=2)
    montant_paye    = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    statut          = models.ForeignKey(StatutPret, on_delete=models.CASCADE)
    
    def montant_restant(self):
        """Retourne le montant restant à payer pour cette échéance (hors pénalités)"""
        return self.montant_a_payer - self.montant_paye
    

class Penalite(BaseModel):
    echeance         = models.ForeignKey(Echeance, on_delete=models.CASCADE)
    montant          = models.DecimalField(max_digits=12, decimal_places=2)
    date_application = models.DateField(auto_now_add=True)
    description      = models.TextField(null=True, blank=True)
    
    def payer_penalite(self, montant):
        if montant >= self.montant:
            montant -= self.montant
            self.montant = 0
        else:
            self.montant -= montant
        self.save()
        return montant




@signals.pre_save(sender=CompteEpargne)
def sighandler(instance, **kwargs):
    if instance._state.adding:
        instance.numero = GenerateTools.epargneId(instance.client.agence)


@signals.pre_save(sender=Transaction)
def sighandler(instance, **kwargs):
    if instance._state.adding:
        instance.numero = GenerateTools.transactionId(instance.compte.client.agence)



@signals.pre_save(sender=Pret)
def sighandler(instance, **kwargs):
    if instance._state.adding:
        instance.numero = GenerateTools.pretId(instance.client.agence)
        instance.montant = instance.base + (instance.base * instance.taux / 100)
        instance.statut = StatutPret.objects.get(etiquette = StatutPret.EN_COURS)


@signals.post_save(sender=Pret)
def sighandler(instance, created, **kwargs):
    if created:
        date_echeance = instance.created_at.date()
        montant = instance.montant / instance.nombre_modalite
        if instance.modalite.etiquette == ModaliteEcheance.HEBDOMADAIRE:
            i = 0
            while i < instance.nombre_modalite:
                i += 1
                date_echeance += timedelta(days=7)
                Echeance.objects.create(
                    pret            = instance,
                    montant_a_payer = montant,
                    date_echeance   = date_echeance,
                    statut          = StatutPret.objects.get(etiquette = StatutPret.EN_COURS),
                )
                
        elif instance.modalite.etiquette == ModaliteEcheance.MENSUEL:
            i = 0
            while i < instance.nombre_modalite:
                i += 1
                date_echeance += timedelta(days=30)
                Echeance.objects.create(
                    pret            = instance,
                    montant_a_payer = montant,
                    date_echeance   = date_echeance,
                    statut          = StatutPret.objects.get(etiquette = StatutPret.EN_COURS),
                )
                
        elif instance.modalite.etiquette == ModaliteEcheance.BIMENSUEL:
            i = 0
            while i < instance.nombre_modalite:
                i += 1
                date_echeance += timedelta(days=60)
                Echeance.objects.create(
                    pret            = instance,
                    montant_a_payer = montant,
                    date_echeance   = date_echeance,
                    statut          = StatutPret.objects.get(etiquette = StatutPret.EN_COURS),
                )
                
        elif instance.modalite.etiquette == ModaliteEcheance.TRIMESTRIEL:
            i = 0
            while i < instance.nombre_modalite:
                i += 1
                date_echeance += timedelta(days=90)
                Echeance.objects.create(
                    pret            = instance,
                    montant_a_payer = montant,
                    date_echeance   = date_echeance,
                    statut          = StatutPret.objects.get(etiquette = StatutPret.EN_COURS),
                )
                
        elif instance.modalite.etiquette == ModaliteEcheance.SEMESTRIEL:
            i = 0
            while i < instance.nombre_modalite:
                i += 1
                date_echeance += timedelta(days=180)
                Echeance.objects.create(
                    pret            = instance,
                    montant_a_payer = montant,
                    date_echeance   = date_echeance,
                    statut          = StatutPret.objects.get(etiquette = StatutPret.EN_COURS),
                )
                
        elif instance.modalite.etiquette == ModaliteEcheance.ANNUEL:
            i = 0
            while i < instance.nombre_modalite:
                i += 1
                date_echeance += relativedelta(days=360)
                Echeance.objects.create(
                    pret            = instance,
                    montant_a_payer = montant,
                    date_echeance   = date_echeance,
                    statut          = StatutPret.objects.get(etiquette = StatutPret.EN_COURS),
                )
        else:
            raise ValueError("Modalité non valide")
