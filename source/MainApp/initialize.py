
from MainApp.models import Agence, Genre, TypeClient


def initialize():
    try:
        # Creation des types de clients
        print("Création des types de clients ...")
        if not TypeClient.objects.filter().exists():
            TypeClient.objects.create(libelle='Particulier', etiquette = TypeClient.PARTICULIER)
            TypeClient.objects.create(libelle='Entreprise', etiquette = TypeClient.ENTREPRISE)
            
        
        # Creation des genres
        print("Création des genres ...")
        if not Genre.objects.filter().exists():
            Genre.objects.create(libelle='Homme', etiquette = Genre.HOMME)
            Genre.objects.create(libelle='Femme', etiquette = Genre.FEMME)
            
            
        # Creation des agences
        print("Création des agences ...")
        if not Agence.objects.filter().exists():
            Agence.objects.create(libelle='Agence principale', adresse='Koumassi, rue des sables', ville='Abidjan', code='AP001')
            

    except Exception as e:
        print("Erreur initialize ClientApp: ", e)