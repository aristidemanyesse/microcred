from django.db import models
from annoying.decorators import signals
from MainApp.models import Client
from CoreApp.tools import GenerateTools
from CoreApp.models import BaseModel
from dateutil.relativedelta import relativedelta
from datetime import date, timedelta
import calendar
from TresorApp.models import Operation


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
    ESPECE = "1"
    MOBILE = "2"
    CHEQUE = "3"
    VIREMENT = "4"
    libelle = models.CharField(max_length=50)  # Espèces / Chèque / Virement
    etiquette = models.CharField(max_length=50)



class TypeAmortissement(BaseModel):
    BASE      = "1"
    CAPITAL   = "2"
    ANNUITE   = "3"
    libelle   = models.CharField(max_length=50)  # Espèces / Chèque / Virement
    etiquette = models.CharField(max_length=50)
    
    
class CompteEpargne(BaseModel):
    numero                = models.CharField(max_length=50, null=True, blank=True)
    client                = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='epargnes')
    solde_actuel          = models.DecimalField(max_digits=12, decimal_places=2, default=0, null=True, blank=True)
    taux                  = models.DecimalField(max_digits=5, decimal_places=2)
    modalite              = models.ForeignKey(ModaliteEcheance, on_delete=models.CASCADE, null=True, blank=True)
    status                = models.ForeignKey(StatusPret, on_delete=models.CASCADE, null=True, blank=True)
    employe               = models.ForeignKey('AuthentificationApp.Employe', on_delete=models.CASCADE, related_name='epargnes')
    derniere_date_interet = models.DateField(null=True, blank=True)
    commentaire           = models.TextField(null=True, blank=True)
    
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
        
    
    def calculer_interet_prorata(self, today = None):
        today = today or date.today()
        periodicite = self.modalite.etiquette

        # ---- Durée de la période (en jours) ----
        if periodicite == ModaliteEcheance.HEBDOMADAIRE:
            jours_periode = 7
            debut_periode = today - timedelta(days=today.weekday())
            
        elif periodicite == ModaliteEcheance.MENSUEL:
            jours_periode = calendar.monthrange(today.year, today.month)[1]
            debut_periode = date(today.year, today.month, 1)
            
        elif periodicite == ModaliteEcheance.BIMENSUEL:
            mois_ref = today.month - ((today.month - 1) % 2)
            debut_periode = date(today.year, mois_ref, 1)
            fin_periode = date(today.year + (mois_ref+1)//12, ((mois_ref+1-1)%12)+1, 1)
            jours_periode = (fin_periode - debut_periode).days
            
        elif periodicite == ModaliteEcheance.TRIMESTRIEL:
            mois_ref = today.month - ((today.month - 1) % 3)
            debut_periode = date(today.year, mois_ref, 1)
            fin_periode = date(today.year + (mois_ref+2)//12, ((mois_ref+2-1)%12)+1, 1)
            jours_periode = (fin_periode - debut_periode).days
            
        elif periodicite == ModaliteEcheance.SEMESTRIEL:
            mois_ref = today.month - ((today.month - 1) % 6)
            debut_periode = date(today.year, mois_ref, 1)
            fin_periode = date(today.year + (mois_ref+5)//12, ((mois_ref+5-1)%12)+1, 1)
            jours_periode = (fin_periode - debut_periode).days
            
        elif periodicite == ModaliteEcheance.ANNUEL:
            debut_periode = date(today.year, 1, 1)
            jours_periode = 366 if calendar.isleap(today.year) else 365

        # ---- Prorata si compte ouvert après le début de la période ----
        debut_effectif = max(self.created_at, debut_periode)
        jours_ecoules = (today - debut_effectif).days + 1
        prorata = jours_ecoules / jours_periode

        # ---- Intérêt ----
        interet = self.solde * (float(self.taux) / 100) * prorata
        return round(interet, 2)
    
    
    
    
    
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
    DEPOT_FIDELIS = "4"
    RETRAIT_FIDELIS = "5"
    libelle = models.CharField(max_length=50)  # Dépôt / Retrait
    etiquette = models.CharField(max_length=50)

    

class Pret(BaseModel):
    numero                 = models.CharField(max_length=50, null=True, blank=True, unique=True)
    client                 = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='prets')
    base                   = models.DecimalField(max_digits=12, decimal_places=2)
    taux                   = models.DecimalField(max_digits=5, decimal_places=2)
    taux_penalite          = models.DecimalField(max_digits=5, decimal_places=2, default=10, null=True, blank=True)
    modalite               = models.ForeignKey(ModaliteEcheance, on_delete=models.CASCADE)
    nombre_modalite        = models.PositiveIntegerField()
    amortissement          = models.ForeignKey(TypeAmortissement, on_delete=models.CASCADE, null=True, blank=True)
    interet                = models.DecimalField(max_digits=12, decimal_places=2, default=0, null=True, blank=True)
    montant                = models.DecimalField(max_digits=12, decimal_places=2, default=0, null=True, blank=True)
    status                 = models.ForeignKey(StatusPret, on_delete=models.CASCADE, null=True, blank=True,)
    employe                = models.ForeignKey('AuthentificationApp.Employe', on_delete=models.CASCADE, related_name='prets')
    confirmateur           = models.ForeignKey('AuthentificationApp.Employe', on_delete=models.CASCADE, related_name='confirm_prets', null=True, blank=True)
    derniere_date_penalite = models.DateField(null=True, blank=True)
    commentaire            = models.TextField(null=True, blank=True)
    
    
    def calcul_interets(self):
        r = self.taux / 100
        n = self.nombre_modalite
        if self.amortissement.etiquette == TypeAmortissement.ANNUITE:
            annuite = self.base * (r * (1 + r) ** n) / ((1 + r) ** n - 1)
            interets = []
            capital_restant = self.base
            for i in range(1, n + 1):
                interet = capital_restant * r
                amortissement = annuite - interet
                capital_restant -= amortissement
                interets.append(interet)
            return sum(interets)

        elif self.amortissement.etiquette == TypeAmortissement.CAPITAL:
            amortissement = self.base / n
            interets = []
            for i in range(1, n + 1):
                capital_restant = self.base - (i - 1) * amortissement
                interet = capital_restant * r
                interets.append(interet)
            return sum(interets)
        
        elif self.amortissement.etiquette == TypeAmortissement.BASE:
            return self.base * r
    
    
    
    def confirm_pret(self, employe):
        date_echeance = self.created_at.date()
        i = 0
        base = round(self.base / self.nombre_modalite, 2)
        
        if self.amortissement.etiquette == TypeAmortissement.BASE:
            reste = self.base
            while i < self.nombre_modalite:
                date_echeance += timedelta(days= self.modalite.duree())
                interet = round(base * self.taux / 100, 2)
                echeance = Echeance.objects.create(
                    pret            = self,
                    level           = i,
                    principal       = base,
                    interet         = interet ,
                    montant_a_payer = base + interet,
                    date_echeance   = date_echeance,
                    status          = StatusPret.objects.get(etiquette = StatusPret.EN_COURS),
                )
                reste -= base + interet
                i += 1
                
                
        elif self.amortissement.etiquette == TypeAmortissement.CAPITAL:
            reste = self.base
            while i < self.nombre_modalite:
                date_echeance += timedelta(days= self.modalite.duree())
                interet = round((self.base - (base * i)) * self.taux / 100, 2)
                echeance = Echeance.objects.create(
                    pret            = self,
                    level           = i,
                    principal       = base,
                    interet         = interet ,
                    montant_a_payer = base + interet,
                    date_echeance   = date_echeance,
                    status          = StatusPret.objects.get(etiquette = StatusPret.EN_COURS),
                )
                reste -= base + interet
                i += 1
                
                
        elif self.amortissement.etiquette == TypeAmortissement.ANNUITE:
            r = self.taux / 100
            n = self.nombre_modalite
            annuite = self.base * (r * (1 + r) ** n) / ((1 + r) ** n - 1)
            reste = self.base
            while i < self.nombre_modalite:
                date_echeance += timedelta(days= self.modalite.duree())
                interet = reste * r
                principal = round(annuite - interet, 2)
                echeance = Echeance.objects.create(
                    pret            = self,
                    level           = i,
                    principal       = principal,
                    interet         = interet ,
                    montant_a_payer = annuite,
                    date_echeance   = date_echeance,
                    status          = StatusPret.objects.get(etiquette = StatusPret.EN_COURS),
                )
                reste -= principal
                i += 1
                
        if reste > 0:
            echeance.interet += reste
            echeance.montant_a_payer += reste
            echeance.save()
            
        self.status       = StatusPret.objects.get(etiquette = StatusPret.EN_COURS)
        self.confirmateur = employe
        self.save()
            
 
    def total(self):    
        return self.montant + self.penalites_montant()
    
    
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
    principal       = models.DecimalField(max_digits=12, decimal_places=2)
    interet         = models.DecimalField(max_digits=12, decimal_places=2)
    montant_a_payer = models.DecimalField(max_digits=12, decimal_places=2)
    montant_paye    = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status          = models.ForeignKey(StatusPret, on_delete=models.CASCADE)
    
    def total(self):
        return self.montant_a_payer + self.penalites_montant()
    
    def montant_restant(self):
        return self.total() - self.montant_paye
    
    def penalites_montant(self):
        return self.penalites.aggregate(total=models.Sum('montant'))['total'] or 0
    
    
    def calculer_penalite(self):
        return self.montant_a_payer * self.pret.taux_penalite / 100
        # today = date.today()
        # jours_retard = (today - self.date_echeance).days
        # montant_penalite = (self.pret.taux_penalite * self.montant_restant())
        # return (montant_penalite * jours_retard) / self.pret.modalite.duree()
    
    def regler(self, montant, employe, mode, commentaire):
        if montant > self.montant_restant():
            raise ValueError("Le montant de remboursement est supérieur au montant restant à payer !")
        if montant <= 0:
            raise ValueError("Le montant de remboursement doit être supérieur à 0 !")
        self.montant_paye += montant
        if self.montant_paye >= self.montant_a_payer:
            self.status = StatusPret.objects.get(etiquette = StatusPret.TERMINE)
        self.save()

        transaction = Transaction.objects.create(
            echeance         = self,
            client           = self.pret.client,
            mode             = mode,
            type_transaction = TypeTransaction.objects.get(etiquette = TypeTransaction.REMBOURSEMENT),
            commentaire      = f"Remboursement échéance N°{self.level} du prêt N°{self.pret.numero} --- {commentaire}",
            montant          = montant,
            employe          = employe
        )

        if transaction:
            if self.pret.reste_a_payer() == 0:
                self.pret.status = StatusPret.objects.get(etiquette = StatusPret.TERMINE)
                self.pret.save()



class Garantie(BaseModel):
    temoin    = models.CharField(max_length=50, null=True, blank=True)
    contact   = models.CharField(max_length=50, null=True, blank=True)
    libelle   = models.CharField(max_length=50, null=True, blank=True)
    montant   = models.DecimalField(max_digits=12, decimal_places=2, default=0, null=True, blank=True)
    pret      = models.ForeignKey(Pret, on_delete=models.CASCADE, related_name='garanties')
    condition = models.TextField(null=True, blank=True)
    employe   = models.ForeignKey('AuthentificationApp.Employe', on_delete=models.CASCADE, related_name='garanties')
    image     = models.ImageField(upload_to='garanties/', null=True, blank=True)
        

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
    fidelis          = models.ForeignKey("FidelisApp.CompteFidelis", null=True, blank=True, on_delete=models.CASCADE, related_name='transactions')
    mode             = models.ForeignKey(ModePayement, null=True, blank=True, on_delete=models.CASCADE)
    type_transaction = models.ForeignKey(TypeTransaction, on_delete=models.CASCADE)
    montant          = models.DecimalField(max_digits=12, decimal_places=2)
    commentaire      = models.TextField(null=True, blank=True)
    employe          = models.ForeignKey('AuthentificationApp.Employe', on_delete=models.CASCADE, related_name='transactions')


   
   
   
   
   
   
   
   
@signals.pre_save(sender=CompteEpargne)
def sighandler(instance, **kwargs):
    if instance._state.adding:
        instance.status = StatusPret.objects.get(etiquette = StatusPret.EN_COURS)
        instance.numero = GenerateTools.epargneId(instance.employe.agence)


@signals.pre_save(sender=Transaction)
def sighandler(instance, **kwargs):
    if instance._state.adding:
        code = instance.employe.agence
        instance.numero = GenerateTools.transactionId(code)
 


@signals.post_save(sender=Transaction)
def sighandler(instance, created, **kwargs):
    if created:
        compte = instance.employe.agence.comptes.filter(principal=True).first()
        Operation.objects.create(
            libelle       = instance.type_transaction,
            compte_credit = compte if instance.type_transaction.etiquette in [TypeTransaction.DEPOT, TypeTransaction.DEPOT_FIDELIS, TypeTransaction.REMBOURSEMENT] else None,
            compte_debit  = compte if instance.type_transaction.etiquette in [TypeTransaction.RETRAIT, TypeTransaction.RETRAIT_FIDELIS] else None,
            montant       = instance.montant,
            employe       = instance.employe,
            transaction   = instance,
        )




@signals.pre_save(sender=Pret)
def sighandler(instance, **kwargs):
    if instance._state.adding:
        instance.numero = GenerateTools.pretId(instance.client.agence)
        instance.interet = instance.calcul_interets()
        instance.montant = instance.base + instance.interet
        instance.status = StatusPret.objects.get(etiquette = StatusPret.EN_ATTENTE)

    


@signals.post_save(sender=Interet)
def sighandler(instance, created, **kwargs):
    if created:
        instance.compte.solde_actuel = instance.compte.solde()
        instance.compte.derniere_date_interet = instance.created_at
        instance.compte.save()
    


@signals.post_save(sender=Penalite)
def sighandler(instance, created, **kwargs):
    if created:
        instance.echeance.status = StatusPret.objects.get(etiquette = StatusPret.RETARD)
        instance.echeance.derniere_date_penalite = instance.created_at
        instance.echeance.save()
    