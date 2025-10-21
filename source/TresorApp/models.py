from django.db import models
from annoying.decorators import signals
from CoreApp.models import BaseModel
from MainApp.models import Agence

# Create your models here.


class CompteAgence(BaseModel):
    libelle   = models.CharField(max_length=50, null=True, blank=True)
    agence    = models.ForeignKey(Agence, on_delete=models.CASCADE, related_name='comptes')
    principal = models.BooleanField(default=False)
    base      = models.DecimalField(max_digits=12, decimal_places=2, default=0, null=True, blank=True)

    def __str__(self):
        return str(self.libelle)
    

    def total_depots(self, start=None, end=None):
        qs = Operation.objects.filter(compte_credit=self)
        if start and end:
            qs = qs.filter(created_at__date__range = [start, end])
        return qs.aggregate(total=models.Sum('montant'))['total'] or 0
    
    def total_retraits(self, start=None, end=None):
        qs = Operation.objects.filter(compte_debit=self)
        if start and end:
            qs = qs.filter(created_at__date__range = [start, end])
        return qs.aggregate(total=models.Sum('montant'))['total'] or 0
    
    def solde(self, start=None, end=None):
        total = self.total_depots(start, end) - self.total_retraits(start, end)
        if start is None or (start and start > self.created_at.date()):
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
    








@signals.post_save(sender=Agence)
def sighandler(instance, created, **kwargs):
    if created:
        principal = not CompteAgence.objects.filter(agence=instance, principal = True).exists()
        libelle = f"Compte principal" if principal else instance.libelle
        CompteAgence.objects.create(agence=instance, principal = principal, libelle=libelle)



@signals.pre_save(sender=Operation)
def sighandler(instance, **kwargs):
    if instance._state.adding:
        if instance.compte_debit is None and instance.compte_credit is None:
            raise ValueError("Vous ne pouvez pas effectuer un transfert sans compte !")
        
        if instance.compte_debit == instance.compte_credit:
            raise ValueError("Vous ne pouvez pas effectuer un transfert entre le même compte !")
