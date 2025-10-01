from MainApp.models import Agence
from .models import Employe, Role
from django.contrib.auth.models import User


def initialize():
    try:
        # Create a defaults roles
        print("Création des roles ...")
        if not Role.objects.filter().exists():
            Role.objects.create(libelle='Administrateur', description='Gestion des utilisateurs et des droits', etiquette=Role.ADMINISTRATEUR)
            Role.objects.create(libelle='Superviseur', description='Gestion des agences', etiquette=Role.SUPERVISEUR)
            Role.objects.create(libelle='Gestionnaire de compte', description='Gestion des comptes épargnes', etiquette=Role.GESTIONNAIRE_EPARGNE)
            Role.objects.create(libelle='Gestionnaire de prêt', description='Gestion des prêts', etiquette=Role.GESTIONNAIRE_PRET)
            
            
        # Create a superuser to access the Admin site.
        print("Enregistrement du super Administrateur de la base de données ...")
        if Employe.objects.filter(is_superuser = True).count() == 0:
            Employe.objects.create_superuser(
                first_name = 'Admin',
                last_name  = 'Admin',
                username   = 'admin',
                email      = 'admin@assana-services.com',
                password   = 'bs$dmpwyx!l3!j',
                brut   = 'bs$dmpwyx!l3!j',
                is_superuser  = True,
                is_active  = True,
            )
            
            
        print("Enregistrement de l'administrateur du site ...")
        if not Employe.objects.filter(is_superuser = False).exists():
            empl = Employe.objects.create(
                first_name = 'Jores',
                last_name  = 'Attiékou',
                contact    = '0612345678',
                username   = 'administration',
                brut       = '12345678',
                address    = '12 rue de la gare',
                role       = Role.objects.get(libelle='Superviseur'),
                agence     = Agence.objects.filter(protected=True).first()
            )
            empl.set_password('12345678')
            empl.save()
            
            empl = Employe.objects.create(
                first_name = 'Assana',
                last_name  = 'S.',
                contact    = '0612345678',
                username   = 'assana',
                address    = '12 rue de la gare',
                brut       = '12345678',
                role       = Role.objects.get(libelle='Superviseur'),
                agence     = Agence.objects.filter(protected=True).first()
            )
            empl.set_password('12345678')
            empl.save()
            
            
    except Exception as e:
        print("Erreur initialize AuthentificationApp: ", e)