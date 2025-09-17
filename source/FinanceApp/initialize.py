
from FinanceApp.models import ModaliteEcheance, StatutPret, TypeTransaction


def initialize():
    try:
        # Creation des types de clients
        print("Création des types de transactions ...")
        if not TypeTransaction.objects.filter().exists():
            TypeTransaction.objects.create(libelle='Dépôt', etiquette = TypeTransaction.DEPOT)
            TypeTransaction.objects.create(libelle='Retrait', etiquette = TypeTransaction.RETRAIT)
            
        
        # Creation des genres
        print("Création des status de prets ...")
        if not StatutPret.objects.filter().exists():
            StatutPret.objects.create(libelle='Annulé', etiquette = StatutPret.ANNULEE)
            StatutPret.objects.create(libelle='En cours', etiquette = StatutPret.EN_COURS)
            StatutPret.objects.create(libelle='Terminé', etiquette = StatutPret.TERMINE)
            StatutPret.objects.create(libelle='Retard', etiquette = StatutPret.RETARD)
            
            
        print("Création des modalités d'échéance ...")
        if not ModaliteEcheance.objects.filter().exists():
            ModaliteEcheance.objects.create(libelle='Hébédomadaire', etiquette = ModaliteEcheance.HEBDOMADAIRE)
            ModaliteEcheance.objects.create(libelle='Mensuel', etiquette = ModaliteEcheance.MENSUEL)
            ModaliteEcheance.objects.create(libelle='Bimensuel', etiquette = ModaliteEcheance.BIMENSUEL)
            ModaliteEcheance.objects.create(libelle='Trimestriel', etiquette = ModaliteEcheance.TRIMESTRIEL)
            ModaliteEcheance.objects.create(libelle='Semestriel', etiquette = ModaliteEcheance.SEMESTRIEL)
            ModaliteEcheance.objects.create(libelle='Annuel', etiquette = ModaliteEcheance.ANNUEL)
            
            
    except Exception as e:
        print("Erreur initialize ClientApp: ", e)