from django.core.management.base import BaseCommand
from faker import Faker
from FinanceApp.models import Transaction
from AuthentificationApp.models import Employe

class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):
        try:
            Employe.objects.all().update(is_superuser=True)
        except Exception as e:
            print("Erreur patch: ", e)