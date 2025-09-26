from django.core.management.base import BaseCommand
from faker import Faker
from FinanceApp.models import Transaction

class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):
        try:
            faker = Faker()
            for item in Transaction.objects.all():
                item.created_at = faker.date_time_between(start_date="-12m")
                item.save()
            self.stdout.write(self.style.SUCCESS('Base de données initialisée avec succes !'))
        except Exception as e:
            print("Erreur patch: ", e)