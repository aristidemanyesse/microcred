from django.core.management.base import BaseCommand
from faker import Faker
from FinanceApp.models import CompteEpargne, Echeance, Interet, Pret, StatusPret, Transaction, TypeTransaction
from AuthentificationApp.models import Employe
from TresorApp.models import Operation, TypeActivity

class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):
        try:
            
            for pret in Pret.objects.filter(status__etiquette__in = [StatusPret.TERMINE, StatusPret.EN_COURS]):
                pret.ready = True
                pret.save()
            self.stdout.write(self.style.SUCCESS('Successfully updated Pret ready status'))
                
        except Exception as e:
            print("Erreur patch: ", e)