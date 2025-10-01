from django.db import models
from annoying.decorators import signals
from MainApp.models import Client
from CoreApp.tools import GenerateTools
from CoreApp.models import BaseModel
from datetime import timedelta
from dateutil.relativedelta import relativedelta

# Create your models here.



class StatusPret(BaseModel):
    ANNULEE = "-1"
    EN_ATTENTE = "0"
    EN_COURS = "1"
    TERMINE = "2"
    RETARD = "3"
    libelle   = models.CharField(max_length=50)  # En cours / Terminé / Retard
    etiquette = models.CharField(max_length=50)
    classe    = models.CharField(max_length=50) 


class ModaliteEcheance(BaseModel):
    HEBDOMADAIRE = "1"
    MENSUEL = "2"
    BIMENSUEL = "3"
    TRIMESTRIEL = "4"
    SEMESTRIEL = "5"
    ANNUEL = "6"
    libelle = models.CharField(max_length=50) 
    libelle2 = models.CharField(max_length=50) 
    etiquette = models.CharField(max_length=50)
    
    def duree(self):
        if self.etiquette == ModaliteEcheance.HEBDOMADAIRE:
            return 7
        elif self.etiquette == ModaliteEcheance.MENSUEL:
            return 30
        elif self.etiquette == ModaliteEcheance.BIMENSUEL:
            return 60
        elif self.etiquette == ModaliteEcheance.TRIMESTRIEL:
            return 90
        elif self.etiquette == ModaliteEcheance.SEMESTRIEL:
            return 180
        elif self.etiquette == ModaliteEcheance.ANNUEL:
            return 360
    
    
class ModePayement(BaseModel):
    ESPECE = 1
    MOBILE = 3
    CHEQUE = 3
    VIREMENT = 4
    libelle = models.CharField(max_length=50)  # Espèces / Chèque / Virement
    etiquette = models.CharField(max_length=50)
    
class CompteEpargne(BaseModel):
    numero       = models.CharField(max_length=50, null=True, blank=True)
    client       = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='epargnes')
    solde_actuel = models.DecimalField(max_digits=12, decimal_places=2, default=0, null=True, blank=True)
    taux         = models.DecimalField(max_digits=5, decimal_places=2)
    modalite     = models.ForeignKey(ModaliteEcheance, on_delete=models.CASCADE, null=True, blank=True)
    status       = models.ForeignKey(StatusPret, on_delete=models.CASCADE, null=True, blank=True)
    employe      = models.ForeignKey('AuthentificationApp.Employe', on_delete=models.CASCADE, related_name='epargnes')
    commentaire  = models.TextField(null=True, blank=True)
    
    def __str__(self):
        return f"Epargne N°{self.numero}"
    
    def deposer(self, montant, employe, mode, commentaire = ""):
        Transaction.objects.create(
            compte           = self,
            client           = self.client,
            type_transaction = TypeTransaction.objects.get(etiquette = TypeTransaction.DEPOT), 
            mode             = mode,
            commentaire      = f"Approvisionnement de {montant} Fcfa sur le compte N°{self.numero} // {commentaire}",
            montant          = montant,
            employe          = employe
        )
        self.solde_actuel = self.solde()
        self.save()
        

    def retirer(self, montant, employe, mode, commentaire = ""):
        self.solde_actuel = self.solde()
        if self.solde_actuel >= montant:
            Transaction.objects.create(
                compte           = self,
                client           = self.client,
                type_transaction = TypeTransaction.objects.get(etiquette = TypeTransaction.RETRAIT),
                mode             = mode,
                commentaire      = f"Retrait de {montant} Fcfa du compte N°{self.numero} // {commentaire}",
                montant          = montant,
                employe          = employe
            )
            self.solde_actuel = self.solde()
            self.save()
        else:
            raise ValueError("Le solde du compte est insuffisant pour ce retrait.")
    
    
    def total_depots(self):
        return Transaction.objects.filter(compte=self, type_transaction__etiquette= TypeTransaction.DEPOT).aggregate(total=models.Sum('montant'))['total'] or 0
    
    def total_retraits(self):    
        return Transaction.objects.filter(compte=self, type_transaction__etiquette = TypeTransaction.RETRAIT).aggregate(total=models.Sum('montant'))['total'] or 0
    
    def total_interets(self):
        return Interet.objects.filter(compte=self).aggregate(total=models.Sum('montant'))['total'] or 0
    
    def solde(self):
        return self.total_depots() + self.total_interets() - self.total_retraits() 
        

class Interet(BaseModel):
    compte        = models.ForeignKey(CompteEpargne, on_delete=models.CASCADE, related_name="interets")
    montant       = models.DecimalField(max_digits=12, decimal_places=2)
    description   = models.TextField(null=True, blank=True)


class TypeTransaction(BaseModel):
    DEPOT = "1"
    RETRAIT = "2"
    REMBOURSEMENT = "3"
    libelle = models.CharField(max_length=50)  # Dépôt / Retrait
    etiquette = models.CharField(max_length=50)

    

class Pret(BaseModel):
    numero          = models.CharField(max_length=50, null=True, blank=True, unique=True)
    client          = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='prets')
    base            = models.DecimalField(max_digits=12, decimal_places=2)
    taux            = models.DecimalField(max_digits=5, decimal_places=2)
    montant         = models.DecimalField(max_digits=12, decimal_places=2, default=0, null=True, blank=True)
    modalite        = models.ForeignKey(ModaliteEcheance, on_delete=models.CASCADE)
    nombre_modalite = models.PositiveIntegerField()
    status          = models.ForeignKey(StatusPret, on_delete=models.CASCADE, null=True, blank=True,)
    employe         = models.ForeignKey('AuthentificationApp.Employe', on_delete=models.CASCADE, related_name='prets')
    confirmateur    = models.ForeignKey('AuthentificationApp.Employe', on_delete=models.CASCADE, related_name='confirm_prets', null=True, blank=True)
    commentaire     = models.TextField(null=True, blank=True)
    
    def total(self):
        total = 0
        for echeance in self.echeances.all():
            total += echeance.total()
        return total
    
    def montant_rembourse(self):
        return Transaction.objects.filter(echeance__pret=self, type_transaction__etiquette = TypeTransaction.REMBOURSEMENT).aggregate(total=models.Sum('montant'))['total'] or 0
    
    def reste_a_payer(self):
        return self.total() - self.montant_rembourse()
    
    def echeances_success(self):
        echeances = self.echeances.filter(status__etiquette = StatusPret.TERMINE)
        return echeances
    
    def progress(self):
        total = self.echeances.count()
        if total == 0:
            return 0
        success = self.echeances_success().count()
        return round((success / total) * 100)
    
    def penalites(self):
        datas = self.echeances.exclude(status__etiquette = StatusPret.ANNULEE).aggregate(total=models.Count('penalites'))['total'] or 0
        return datas
    
    def penalites_montant(self):
        return self.echeances.exclude(status__etiquette = StatusPret.ANNULEE).aggregate(total=models.Sum('penalites__montant'))['total'] or 0


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
                echeance.status = StatusPret.objects.get(nom='OK')
                echeance.save()
                montant -= restant
            else:
                echeance.montant_paye += montant
                echeance.status = StatusPret.objects.get(nom='Partiellement payé')
                echeance.save()
                montant = 0
        # Mettre à jour montant remboursé du prêt
        self.montant_rembourse = sum(e.montant_paye for e in self.echeance_set.all())
        # Mise à jour status du prêt
        if self.montant_rembourse >= self.montant:
            self.status = StatusPret.objects.get(nom='Terminé')
        elif self.echeance_set.filter(status__nom='En retard').exists():
            self.status = StatusPret.objects.get(nom='Retard')
        else:
            self.status = StatusPret.objects.get(nom='En cours')
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
    pret            = models.ForeignKey(Pret, on_delete=models.CASCADE, related_name='echeances')
    level           = models.PositiveIntegerField(default=0)
    date_echeance   = models.DateField()
    montant_a_payer = models.DecimalField(max_digits=12, decimal_places=2)
    montant_paye    = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status          = models.ForeignKey(StatusPret, on_delete=models.CASCADE)
    
    def total(self):
        return self.montant_a_payer + self.penalites_montant()
    
    def montant_restant(self):
        return self.total() - self.montant_paye
    
    def penalites_montant(self):
        return self.penalites.aggregate(total=models.Sum('montant'))['total'] or 0
    
    
    def regler(self, montant, employe, mode, commentaire):
        if montant > self.montant_restant():
            raise ValueError("Le montant de remboursement est supérieur au montant restant à payer !")
        if montant <= 0:
            raise ValueError("Le montant de remboursement doit être supérieur à 0 !")
        self.montant_paye += montant
        if self.montant_paye >= self.montant_a_payer:
            self.status = StatusPret.objects.get(etiquette = StatusPret.TERMINE)
        self.save()

        Transaction.objects.create(
            echeance         = self,
            client           = self.pret.client,
            mode             = mode,
            type_transaction = TypeTransaction.objects.get(etiquette = TypeTransaction.REMBOURSEMENT),
            commentaire      = f"Remboursement échéance N°{self.level} du prêt N°{self.pret.numero} --- {commentaire}",
            montant          = montant,
            employe          = employe
        )

        
        

class Penalite(BaseModel):
    echeance         = models.ForeignKey(Echeance, on_delete=models.CASCADE, related_name='penalites')
    montant          = models.DecimalField(max_digits=12, decimal_places=2)
    description      = models.TextField(null=True, blank=True)
    
    def payer_penalite(self, montant):
        if montant >= self.montant:
            montant -= self.montant
            self.montant = 0
        else:
            self.montant -= montant
        self.save()
        return montant



class Transaction(BaseModel):
    numero           = models.CharField(max_length=50)
    client           = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='transactions')
    compte           = models.ForeignKey(CompteEpargne, null=True, blank=True, on_delete=models.CASCADE, related_name='transactions')
    echeance         = models.ForeignKey(Echeance, null=True, blank=True, on_delete=models.CASCADE, related_name='transactions')
    mode             = models.ForeignKey(ModePayement, null=True, blank=True, on_delete=models.CASCADE)
    type_transaction = models.ForeignKey(TypeTransaction, on_delete=models.CASCADE)
    montant          = models.DecimalField(max_digits=12, decimal_places=2)
    commentaire      = models.TextField(null=True, blank=True)
    employe          = models.ForeignKey('AuthentificationApp.Employe', on_delete=models.CASCADE, related_name='transactions')


   
   
   
@signals.pre_save(sender=CompteEpargne)
def sighandler(instance, **kwargs):
    if instance._state.adding:
        instance.status = StatusPret.objects.get(etiquette = StatusPret.EN_COURS)
        instance.numero = GenerateTools.epargneId(instance.client.agence)


@signals.pre_save(sender=Transaction)
def sighandler(instance, **kwargs):
    if instance._state.adding:
        code = instance.compte.client.agence if instance.compte else (instance.echeance.pret.client.agence if instance.echeance else None)
        instance.numero = GenerateTools.transactionId(code)



@signals.pre_save(sender=Pret)
def sighandler(instance, **kwargs):
    if instance._state.adding:
        instance.numero = GenerateTools.pretId(instance.client.agence)
        instance.montant = instance.base + (instance.base * instance.taux / 100)
        instance.status = StatusPret.objects.get(etiquette = StatusPret.EN_ATTENTE)


@signals.post_save(sender=Pret)
def sighandler(instance, created, **kwargs):
    if created:
        date_echeance = instance.created_at.date()
        montant = instance.montant / instance.nombre_modalite
    
    else:
        if instance.status.etiquette == StatusPret.EN_COURS and len(instance.echeances.filter()) == 0:
            i = 0
            while i < instance.nombre_modalite:
                i += 1
                if instance.modalite.etiquette == ModaliteEcheance.HEBDOMADAIRE:
                    date_echeance += timedelta(days=7)
                elif instance.modalite.etiquette == ModaliteEcheance.MENSUEL:
                    date_echeance += timedelta(days=30)
                elif instance.modalite.etiquette == ModaliteEcheance.BIMENSUEL:
                    date_echeance += timedelta(days=60)
                elif instance.modalite.etiquette == ModaliteEcheance.TRIMESTRIEL:
                    date_echeance += timedelta(days=90)
                elif instance.modalite.etiquette == ModaliteEcheance.SEMESTRIEL:
                    date_echeance += timedelta(days=180)
                elif instance.modalite.etiquette == ModaliteEcheance.ANNUEL:
                    date_echeance += relativedelta(days=360)

                Echeance.objects.create(
                    pret            = instance,
                    level           = i,
                    montant_a_payer = montant,
                    date_echeance   = date_echeance,
                    status          = StatusPret.objects.get(etiquette = StatusPret.EN_COURS),
                )
                


@signals.post_save(sender=Interet)
def sighandler(instance, created, **kwargs):
    if created:
        instance.compte.solde_actuel = instance.compte.solde()
        instance.compte.save()
    