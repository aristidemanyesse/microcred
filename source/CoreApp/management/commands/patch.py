from django.core.management.base import BaseCommand
from faker import Faker
from FinanceApp.models import CompteEpargne, Echeance, Interet, StatusPret, Transaction
from AuthentificationApp.models import Employe

class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):
        try:
            faker = Faker()
            for employe in Employe.objects.all():
                print(employe)
        except Exception as e:
            print("Erreur patch: ", e)