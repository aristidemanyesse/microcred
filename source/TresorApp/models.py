from django.db import models
from annoying.decorators import signals
from CoreApp.models import BaseModel
from MainApp.models import Agence
from datetime import datetime

# Create your models here.


class TypeActivity(BaseModel):
    PRET = "1"
    FIDELIS = "2"
    EPARGNE = "3"
    libelle = models.CharField(max_length=50)
    etiquette = models.CharField(max_length=50)

class CompteAgence(BaseModel):
    libelle   = models.CharField(max_length=50, null=True, blank=True)
    agence    = models.ForeignKey(Agence, on_delete=models.CASCADE, related_name='comptes')
    activity  = models.ForeignKey(TypeActivity, on_delete=models.CASCADE, related_name='comptes', null=True, blank=True)
    base      = models.DecimalField(max_digits=12, decimal_places=2, default=0, null=True, blank=True)

    def __str__(self):
        return str(self.libelle)
    

    def total_depots(self, start:datetime=None, end:datetime=None):
        start = start or self.created_at
        end = end or datetime.now()
        qs = Operation.objects.filter(compte_credit=self)
        if start and end:
            qs = qs.filter(created_at__range = [start, end])
        return qs.aggregate(total=models.Sum('montant'))['total'] or 0
    
    def total_retraits(self, start:datetime=None, end:datetime=None):
        start = start or self.created_at
        end = end or datetime.now()
        qs = Operation.objects.filter(compte_debit=self)
        if start and end:
            qs = qs.filter(created_at__range = [start, end])
        return qs.aggregate(total=models.Sum('montant'))['total'] or 0
    
    def solde(self, start:datetime=None, end:datetime=None):
        start = start or self.created_at
        end = end or datetime.now()
        total = self.total_depots(start, end) - self.total_retraits(start, end)
        if start is None or (start and start > self.created_at):
            return total
        return total + self.base


class Operation(BaseModel):
    libelle       = models.CharField(max_length=50, null=True, blank=True)
    montant       = models.DecimalField(max_digits=12, decimal_places=2, default=0, null=True, blank=True)
    compte_debit  = models.ForeignKey(CompteAgence, on_delete=models.CASCADE, related_name='debits', null=True, blank=True)
    compte_credit = models.ForeignKey(CompteAgence, on_delete=models.CASCADE, related_name='credits', null=True, blank=True)
    transaction   = models.ForeignKey('FinanceApp.Transaction', on_delete=models.CASCADE, related_name='operations', null=True, blank=True)
    employe       = models.ForeignKey('AuthentificationApp.Employe', on_delete=models.CASCADE, related_name='operations')
    commentaire   = models.TextField(null=True, blank=True)
    
    def __str__(self):
        return str(self.libelle)
    
    def debit_amount_before(self):
        return self.compte_debit.solde(end=self.created_at) if self.compte_debit else 0
    
    def credit_amount_before(self):
        return self.compte_credit.solde(end=self.created_at) if self.compte_credit else 0
    





@signals.post_save(sender=Agence)
def sighandler(instance, created, **kwargs):
    if created:
        for letype in TypeActivity.objects.all():
            compte, _ = CompteAgence.objects.get_or_create(agence=instance, activity=letype, libelle=f"Compte {letype.libelle}")
            if _:
                compte.base = 0
                compte.save()



@signals.pre_save(sender=Operation)
def sighandler(instance, **kwargs):
    if instance._state.adding:
        if instance.compte_debit is None and instance.compte_credit is None:
            raise ValueError("Vous ne pouvez pas effectuer un transfert sans compte !")
        
        if instance.compte_debit == instance.compte_credit:
            raise ValueError("Vous ne pouvez pas effectuer un transfert entre le même compte !")
