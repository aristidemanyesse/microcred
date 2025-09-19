
from FinanceApp.models import ModaliteEcheance, ModePayement, StatusPret, TypeTransaction


def initialize():
    try:
        # Creation des types de clients
        print("Création des types de transactions ...")
        if not TypeTransaction.objects.filter().exists():
            TypeTransaction.objects.create(libelle='Dépôt', etiquette = TypeTransaction.DEPOT)
            TypeTransaction.objects.create(libelle='Retrait', etiquette = TypeTransaction.RETRAIT)
            TypeTransaction.objects.create(libelle='Remboursement de prêt', etiquette = TypeTransaction.REMBOURSEMENT)
            
        
        # Creation des genres
        print("Création des status de prets ...")
        if not StatusPret.objects.filter().exists():
            StatusPret.objects.create(libelle='Annulé', etiquette = StatusPret.ANNULEE, classe="danger")
            StatusPret.objects.create(libelle='En attente', etiquette = StatusPret.EN_ATTENTE, classe="default")
            StatusPret.objects.create(libelle='En cours', etiquette = StatusPret.EN_COURS, classe="primary")
            StatusPret.objects.create(libelle='Terminé', etiquette = StatusPret.TERMINE, classe="success")
            StatusPret.objects.create(libelle='Retard', etiquette = StatusPret.RETARD, classe="warning")
            
            
        print("Création des modalités d'échéance ...")
        if not ModaliteEcheance.objects.filter().exists():
            ModaliteEcheance.objects.create(libelle='Hébédomadaire', etiquette = ModaliteEcheance.HEBDOMADAIRE)
            ModaliteEcheance.objects.create(libelle='Mensuel', etiquette = ModaliteEcheance.MENSUEL)
            ModaliteEcheance.objects.create(libelle='Bimensuel', etiquette = ModaliteEcheance.BIMENSUEL)
            ModaliteEcheance.objects.create(libelle='Trimestriel', etiquette = ModaliteEcheance.TRIMESTRIEL)
            ModaliteEcheance.objects.create(libelle='Semestriel', etiquette = ModaliteEcheance.SEMESTRIEL)
            ModaliteEcheance.objects.create(libelle='Annuel', etiquette = ModaliteEcheance.ANNUEL)
            
            
        print("Création des modes de payement ...")
        if not ModePayement.objects.filter().exists():
            ModePayement.objects.create(libelle='Espèces', etiquette = ModePayement.ESPECE)
            ModePayement.objects.create(libelle='Mobile Money', etiquette = ModePayement.MOBILE)
            ModePayement.objects.create(libelle='Chèque', etiquette = ModePayement.CHEQUE)
            ModePayement.objects.create(libelle='Virement', etiquette = ModePayement.VIREMENT)  
            
            
    except Exception as e:
        print("Erreur initialize ClientApp: ", e)