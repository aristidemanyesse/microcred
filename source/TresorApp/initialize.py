
from TresorApp.models import TypeActivity


def initialize():
    try:
        # Creation des types d'activités
        print("Création des types d'activités ...")
        if not TypeActivity.objects.filter().exists():
            TypeActivity.objects.create(libelle='Prêt', etiquette = TypeActivity.PRET)
            TypeActivity.objects.create(libelle='Fidélis', etiquette = TypeActivity.FIDELIS)
            TypeActivity.objects.create(libelle='Épargne', etiquette = TypeActivity.EPARGNE)


    except Exception as e:
        print("Erreur initialize ClientApp: ", e)