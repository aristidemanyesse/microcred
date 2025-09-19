from django.core.management.base import BaseCommand, CommandError
from faker import Faker
from AuthentificationApp.models import *
from MainApp.models import *
from FinanceApp.models import *

class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):
        
        faker = Faker()
        
        print("Création des clients...")
        for i in range(80):
            Client.objects.create(
                agence       = Agence.objects.filter().order_by('?').first(),
                type_client  = TypeClient.objects.filter().order_by('?').first(),
                date_naissance = faker.date_between(start_date="-70y", end_date="-18y"),
                nom          = faker.last_name(),
                prenoms      = faker.first_name(),
                profession    = faker.job(),
                genre        = Genre.objects.filter().order_by('?').first(),
                adresse      = faker.address(),
                telephone    = faker.phone_number(),
                email        = faker.email(),
                employe      = Employe.objects.filter().order_by('?').first()
            )
            
            
        for i in range(100):
            pret = Pret.objects.create(
                client          = Client.objects.filter().order_by('?').first(),
                modalite        = ModaliteEcheance.objects.filter().order_by('?').first(),
                base            = faker.random_int(min=100000, max=10000000),
                taux            = faker.random_int(min=1, max=10),
                nombre_modalite = faker.random_int(min=10, max=30),
                employe         = Employe.objects.filter().order_by('?').first(),
            )
            for echeance in pret.echeances.all().order_by('date_echeance')[:faker.random_int(min=1, max=7)]:
                montant = echeance.montant_a_payer if faker.boolean(chance_of_getting_true=70) else faker.random_int(min=100, max=round(echeance.montant_a_payer), step=100)
                echeance.regler(montant, employe=Employe.objects.filter().order_by('?').first())
                
                if faker.boolean(chance_of_getting_true=70):
                    Penalite.objects.create(
                        echeance = echeance,
                        montant  = faker.random_int(min=100, max=100000),
                        description = faker.text(max_nb_chars=50),
                    )
                
            

            compte =CompteEpargne.objects.create(
                client = Client.objects.filter().order_by('?').first(),
                employe = Employe.objects.filter().order_by('?').first(),
                taux = faker.random_int(min=1, max=10),
            )
            for i in range(5):
                compte.deposer(montant=faker.random_int(min=10000, max=100000), employe=Employe.objects.filter().order_by('?').first())
                if faker.boolean(chance_of_getting_true=50):
                    try:
                        compte.retirer(montant=faker.random_int(min=10000, max=100000), employe=Employe.objects.filter().order_by('?').first())
                    except ValueError:
                        pass
                    
                if faker.boolean(chance_of_getting_true=50):
                    Interet.objects.create(
                        compte      = compte,
                        montant     = (compte.solde() * faker.random_int(min=1, max=10)) / 100,
                        description = faker.text(max_nb_chars=50),
                    )   
            
            
        self.stdout.write(self.style.SUCCESS('Base de données initialisée avec succes !'))