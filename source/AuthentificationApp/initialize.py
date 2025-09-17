from .models import Employe, Role
from django.contrib.auth.models import User


def initialize():
    try:
        # Create a defaults roles
        print("Création des roles ...")
        if not Role.objects.filter().exists():
            Role.objects.create(libelle='Administrateur')
            Role.objects.create(libelle='Superviseur')
            Role.objects.create(libelle='Gestionnaire de compte')
            
            
        # Create a superuser to access the Admin site.
        print("Enregistrement du super Administrateur de la base de données ...")
        if Employe.objects.filter(is_superuser = True).count() == 0:
            Employe.objects.create_superuser(
                first_name = 'Administrateur',
                last_name  = 'Assanah',
                username   = 'administration',
                email      = 'administration@assanah.com',
                password   = '12345678',
                is_superuser  = True,
                is_active  = True,
            )
            
            
        print("Enregistrement de l'administrateur du site ...")
        if not Employe.objects.filter().exists():
            emp = Employe.objects.create(
                first_name = 'Aristide',
                last_name  = 'Manyesse',
                contact = '0612345678',
                address = '12 rue de la gare',
                role    = Role.objects.get(libelle='Superviseur')
            )
            
            
    except Exception as e:
        print("Erreur initialize AuthentificationApp: ", e)