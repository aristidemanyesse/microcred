
from django.db import models
from MainApp.models import Client
from CoreApp.models import BaseModel
from annoying.decorators import signals
from CoreApp.tools import GenerateTools
from FinanceApp.models import StatusPret, Transaction, TypeTransaction
from datetime import datetime
from django.db.models import Sum
# Create your models here.


class CompteFidelis(BaseModel):
    numero     = models.CharField(max_length=50, null=True, blank=True, unique=True)
    client     = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='fidelis')
    base       = models.DecimalField(max_digits=12, decimal_places=2, default=0, null=True, blank=True)
    nombre     = models.PositiveIntegerField(default=0)
    frais      = models.DecimalField(max_digits=12, decimal_places=2, default=0, null=True, blank=True)
    retire     = models.BooleanField(default=False)
    cloture_at = models.DateTimeField(null=True, blank=True)
    status     = models.ForeignKey(StatusPret, on_delete=models.CASCADE, related_name='fidelis', null=True, blank=True)
    employe    = models.ForeignKey('AuthentificationApp.Employe', on_delete=models.CASCADE, related_name='fidelis')
    
    
    def __str__(self):
        return f"Fidelis N°{self.numero}"
    
    
    def nombre_paye(self):
        return self.cases.filter(status__etiquette = StatusPret.TERMINE).count()

    def total_payes(self):
        return self.nombre_paye() *  self.base
    
    def total_retire(self):
        return self.transactions.filter(type_transaction__etiquette = TypeTransaction.RETRAIT_FIDELIS).aggregate(total=Sum('montant'))['total'] or 0
    
    def solde(self):
        if self.retire : return 0
        return self.total_payes() - self.total_retire()
    
    
    def deposer(self, employe, mode, commentaire):
        case = self.cases.filter(status__etiquette=StatusPret.EN_COURS).first()
        if case is not None:
            Transaction.objects.create(
                client           = self.client,
                fidelis          = self,
                type_transaction = TypeTransaction.objects.get(etiquette = TypeTransaction.DEPOT_FIDELIS),
                mode             = mode,
                commentaire      = f"Dépôt sur Fidélis N°{self.numero} // {commentaire}",
                montant          = self.base,
                employe          = employe,
            )
            case.status = StatusPret.objects.get(etiquette=StatusPret.TERMINE)
            case.save()
            if not self.cases.filter(status__etiquette=StatusPret.EN_COURS).exists():
                self.status = StatusPret.objects.get(etiquette=StatusPret.TERMINE)
                self.cloture_at = datetime.now()
                self.save()
                
    
    def retirer(self, employe, mode, commentaire):
        Transaction.objects.create(
            client           = self.client,
            fidelis          = self,
            type_transaction = TypeTransaction.objects.get(etiquette = TypeTransaction.RETRAIT_FIDELIS),
            mode             = mode,
            commentaire      = f"Fin de Fidélis N°{self.numero} // {commentaire}",
            montant          = self.solde() - self.frais,
            employe          = employe,
        )

        self.status = StatusPret.objects.get(etiquette = StatusPret.TERMINE)
        self.retire = True
        self.cloture_at = datetime.now() if self.cloture_at is None else self.cloture_at
        
        self.save()
        
        

class FidelisCase(BaseModel):
    fidelis = models.ForeignKey(CompteFidelis, on_delete=models.CASCADE, related_name='cases')
    level = models.PositiveIntegerField(default=0)
    status = models.ForeignKey(StatusPret, on_delete=models.CASCADE, related_name='cases')





@signals.pre_save(sender=CompteFidelis)
def sighandler(instance, **kwargs):
    if instance._state.adding:
        agence = instance.employe.agence
        instance.numero = GenerateTools.fidelisId(agence)
        instance.frais = instance.base
        instance.nombre += 1
        instance.status = StatusPret.objects.get(etiquette = StatusPret.EN_COURS)
        
        
        
@signals.post_save(sender=CompteFidelis)
def sighandler(instance, created, **kwargs):
    if created:
        i = 1
        while i <= instance.nombre:
            FidelisCase.objects.create(fidelis=instance, level=i, status = StatusPret.objects.get(etiquette = StatusPret.EN_COURS))
            i += 1
            
            
            
            
@signals.pre_save(sender=FidelisCase)
def sighandler(instance, **kwargs):
    if instance._state.adding:
        instance.status = StatusPret.objects.get(etiquette = StatusPret.EN_COURS)