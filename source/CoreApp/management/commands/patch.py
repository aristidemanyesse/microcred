from django.core.management.base import BaseCommand
from faker import Faker
from FinanceApp.models import CompteEpargne, Echeance, Interet, StatusPret, Transaction
from AuthentificationApp.models import Employe

class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):
        try:
            faker = Faker()
            for epargne in CompteEpargne.objects.all():
                Interet.objects.create(
                    compte        = epargne,
                    montant       = faker.random_int(min=100, max=100000),
                    description   = "Montant de l'échéance",
                )
        except Exception as e:
            print("Erreur patch: ", e)