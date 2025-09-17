
from FinanceApp.models import StatutPret, TypeTransaction


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
            
            
    except Exception as e:
        print("Erreur initialize ClientApp: ", e)