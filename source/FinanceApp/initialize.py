
from FinanceApp.models import *


def initialize():
    try:
        # Creation des types de clients
        print("Création des types de transactions ...")
        if not TypeTransaction.objects.filter().exists():
            TypeTransaction.objects.create(libelle='Dépôt sur compte épargne', etiquette = TypeTransaction.DEPOT)
            TypeTransaction.objects.create(libelle='Retrait sur compte épargne', etiquette = TypeTransaction.RETRAIT)
            TypeTransaction.objects.create(libelle='Remboursement de prêt', etiquette = TypeTransaction.REMBOURSEMENT)
            TypeTransaction.objects.create(libelle='Dépôt sur compte Fidélis', etiquette = TypeTransaction.DEPOT_FIDELIS)
            TypeTransaction.objects.create(libelle='Retrait sur compte Fidélis', etiquette = TypeTransaction.RETRAIT_FIDELIS)
            
            
        
        # Creation des genres
        print("Création des status de prets ...")
        if not StatusPret.objects.filter().exists():
            StatusPret.objects.create(libelle='Annulé', etiquette = StatusPret.ANNULEE, classe="danger")
            StatusPret.objects.create(libelle='En attente', etiquette = StatusPret.EN_ATTENTE, classe="light")
            StatusPret.objects.create(libelle='En cours', etiquette = StatusPret.EN_COURS, classe="primary")
            StatusPret.objects.create(libelle='Terminé', etiquette = StatusPret.TERMINE, classe="success")
            StatusPret.objects.create(libelle='Retard', etiquette = StatusPret.RETARD, classe="warning")
            
            
        print("Création des modalités d'échéance ...")
        if not ModaliteEcheance.objects.filter().exists():
            ModaliteEcheance.objects.create(libelle='Hébédomadaire', libelle2="semaine", etiquette = ModaliteEcheance.HEBDOMADAIRE)
            ModaliteEcheance.objects.create(libelle='Mensuel', libelle2="mois", etiquette = ModaliteEcheance.MENSUEL)
            ModaliteEcheance.objects.create(libelle='Bimensuel', libelle2="bimestre", etiquette = ModaliteEcheance.BIMENSUEL)
            ModaliteEcheance.objects.create(libelle='Trimestriel', libelle2="trimestre", etiquette = ModaliteEcheance.TRIMESTRIEL)
            ModaliteEcheance.objects.create(libelle='Semestriel', libelle2="semestre", etiquette = ModaliteEcheance.SEMESTRIEL)
            ModaliteEcheance.objects.create(libelle='Annuel', libelle2="année", etiquette = ModaliteEcheance.ANNUEL)
            
            
        print("Création des modes de payement ...")
        if not ModePayement.objects.filter().exists():
            ModePayement.objects.create(libelle='En espèces', etiquette = ModePayement.ESPECE)
            ModePayement.objects.create(libelle='Par mobile Money', etiquette = ModePayement.MOBILE)
            ModePayement.objects.create(libelle='Par chèque', etiquette = ModePayement.CHEQUE)
            ModePayement.objects.create(libelle='Par virement bancaire', etiquette = ModePayement.VIREMENT)  
            
            
        print("Création des types d'amortissement ...")
        if not TypeAmortissement.objects.filter().exists():
            TypeAmortissement.objects.create(libelle='Capital et interet constants', etiquette = TypeAmortissement.BASE)
            TypeAmortissement.objects.create(libelle='Annuité constante', etiquette = TypeAmortissement.ANNUITE)
            
            
    except Exception as e:
        print("Erreur initialize FinanceApp: ", e)