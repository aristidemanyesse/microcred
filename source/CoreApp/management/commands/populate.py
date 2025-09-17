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
                genre        = Genre.objects.filter().order_by('?').first(),
                adresse      = faker.address(),
                telephone    = faker.phone_number(),
                email        = faker.email(),
            )
            
            
        for i in range(100):
            pret = Pret.objects.create(
                client          = Client.objects.filter().order_by('?').first(),
                modalite        = ModaliteEcheance.objects.filter().order_by('?').first(),
                base            = faker.random_int(min=100000, max=10000000),
                taux            = faker.random_int(min=1, max=10),
                nombre_modalite = faker.random_int(min=10, max=30),
            )
            for echeance in pret.echeance_set.all().order_by('date_echeance'):
                echeance.montant_paye = echeance.montant_a_payer if faker.boolean(chance_of_getting_true=70) else faker.random_int(min=100, max=round(echeance.montant_a_payer), step=100)
                echeance.save()
                
                if faker.boolean(chance_of_getting_true=70):
                    Penalite.objects.create(
                        echeance = echeance,
                        montant  = faker.random_int(min=100, max=100000),
                        description = faker.text(max_nb_chars=50),
                    )
                
            

            compte =CompteEpargne.objects.create(
                client        = Client.objects.filter().order_by('?').first(),
                date_creation = faker.date_between(start_date="-5y", end_date="now"),
            )
            for i in range(5):
                Transaction.objects.create(
                    compte           = compte,
                    type_transaction = TypeTransaction.objects.filter().order_by('?').first(),
                    montant          = faker.random_int(min=10000, max=100000),
                    date_transaction = faker.date_between(start_date="-5y", end_date="now"),
                    commentaire      = faker.text(max_nb_chars=50),
                )
                
                if faker.boolean(chance_of_getting_true=50):
                    Interet.objects.create(
                        compte      = compte,
                        montant     = (compte.solde() * faker.random_int(min=1, max=10)) / 100,
                        description = faker.text(max_nb_chars=50),
                    )   
            
            
        return
        
        # Create a defaults roles
        print("Création des utilisateurs ...")
        for i in range(5):
            emp = Employe.objects.create(
                contact = faker.basic_phone_number(),
                address = faker.address(),
                role    = Role.objects.filter().order_by('?').first(),
            )

         
        print("Création des clients...")
        for i in range(5):
            Client.objects.create(
                contact       = faker.basic_phone_number(),
                address       = faker.address(),
                type_client   = TypeClient.objects.filter().order_by('?').first(),
                date_creation = faker.date_time_between(start_date="-5m", end_date="now"),
            )

         
        print("Création des emballage...")
        for i in range(100):
            Emballage.objects.create(
                type   = TypeEmballage.objects.filter().order_by('?').first(),
            )
        
        print("Création des livreurs...")
        for i in range(10):
            Livreur.objects.create(
                contact   = faker.email(),
                address   = faker.address(),
                vehicule  = TypeVehicule.objects.filter().order_by('?').first(),
                active    = True,
                date_creation     = faker.date_time_between(start_date="-5m", end_date="now"),
            )
            
        print("Creation des points relais...")
        for i in range(30):
            pr = PointRelais.objects.create(
                libelle              = faker.company(),
                commune           = Commune.objects.filter().order_by('?').first(),
                address           = faker.address(),
                description       = faker.text(),
                email             = faker.email(),
                contact           = faker.basic_phone_number(),
                contact2          = faker.basic_phone_number(),
                available_ferie   = faker.boolean(),
                logo              = faker.image_url(),
                background        = faker.image_url(),
                type              = TypePointRelais.objects.filter().order_by('?').first(),
                date_creation     = faker.date_time_between(start_date="-5m", end_date="now"),
            )
            pr.services.set(TypeService.objects.filter()[:faker.random_int(min=1, max=3)])
            
        
        print("Cross Communes ...")
        for cross in CrossCommune.objects.all():
            cross.zone = Zone.objects.filter().order_by('?').first()
            cross.save()
        
        print("Type colis ...")
        for type in TypeColis.objects.all():
            type.vehicule = TypeVehicule.objects.filter().order_by('?').first()
            type.save()
            
            
        print("Creation des colis...")
        for i in range(100):
            colis = Colis.objects.create(
                sender                = Client.objects.filter().order_by('?').first(),
                receiver              = Client.objects.filter().order_by('?').first(),
                receiver_name         = faker.first_name(),
                receiver_phone        = faker.basic_phone_number(),
                point_relais_sender   = PointRelais.objects.filter().order_by('?').first(),
                point_relais_receiver = PointRelais.objects.filter().order_by('?').first(),
                type_colis            = TypeColis.objects.filter().order_by('?').first(),
                type_emballage        = TypeEmballage.objects.filter().order_by('?').first(),
                type_destinataire     = TypeDestinataire.objects.filter().order_by('?').first(),
                status                = StatusColis.objects.filter().order_by('?').first(),
                date_creation         = faker.date_time_between(start_date="-5m", end_date="now"),
            )
            if colis.status.level >= StatusColis.objects.get(level=StatusColis.RETRAIT).level:
                RetraitColis.objects.create(
                    colis = colis,
                    client = colis.receiver,
                    success_date = faker.date_between(start_date="-1y", end_date="-1w"),
                    date_creation     = faker.date_time_between(start_date="-5m", end_date="now"),
                )
            if colis.status.level >= StatusColis.objects.get(level=StatusColis.LIVRAISON).level:
                LivraisonColis.objects.create(
                    colis           = colis,
                    livreur         = Livreur.objects.filter().order_by('?').first(),
                    status          = StatusLivraison.objects.filter().order_by('?').first(),
                    success_date    = faker.date_between(start_date="-1y", end_date="-1w"),
                    date_creation     = faker.date_time_between(start_date="-5m", end_date="now"),
                )
            if colis.status.level >= StatusColis.objects.get(level=StatusColis.RECUPERATION).level:
                RecuperationColis.objects.create(
                    colis         = colis,
                    livreur       = Livreur.objects.filter().order_by('?').first(),
                    success_date    = faker.date_between(start_date="-1y", end_date="-1w"),
                    date_creation     = faker.date_time_between(start_date="-5m", end_date="now"),
                )
            if colis.status.level >= StatusColis.objects.get(level=StatusColis.DEPOSE).level:
                DepotColis.objects.create(
                    colis           = colis,
                    point_relais    = PointRelais.objects.filter().order_by('?').first(),
                    success_date      = faker.date_between(start_date="-1y", end_date="-1w"),
                    date_creation     = faker.date_time_between(start_date="-5m", end_date="now"),
                )
                
                
            # Payement.objects.create(
            #     amount        = colis.total,
            #     code          = colis.code,
            #     message       = faker.text(max_nb_chars=50),
            #     status        = True,
            #     date_creation     = faker.date_time_between(start_date="-5m", end_date="now"),
            # )
        self.stdout.write(self.style.SUCCESS('Base de données initialisée avec succes !'))