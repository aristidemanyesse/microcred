from django.core.management.base import BaseCommand
from faker import Faker
from FinanceApp.models import Echeance, StatusPret, Transaction
from AuthentificationApp.models import Employe
from datetime import date
class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):
        try:
            Echeance.objects.filter(date_echeance__lte=date.today(), status__etiquette = StatusPret.EN_COURS).update(status=StatusPret.objects.get(etiquette = StatusPret.RETARD))
        except Exception as e:
            print("Erreur patch: ", e)