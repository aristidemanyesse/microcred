from datetime import datetime, timedelta
from django.core.management.base import BaseCommand

from TresorApp.models import CompteAgence, Operation


class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):
        try:
            
            for x in CompteAgence.objects.filter(libelle = "Compte Epargne"):
                # x.created_at = datetime(2025, 10, 1, 0, 0, 0)
                # x.save()
                print(x.base)
                opes = Operation.objects.filter(compte_credit = x).order_by("created_at")[:1]
                for ope in opes:
                    print(ope.credit_amount_before())
                
        except Exception as e:
            print("Erreur patch: ", e)