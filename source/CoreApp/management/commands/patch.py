from django.core.management.base import BaseCommand
from faker import Faker
from FinanceApp.models import CompteEpargne, Echeance, Interet, Pret, StatusPret, Transaction, TypeTransaction
from AuthentificationApp.models import Employe
from TresorApp.models import Operation, TypeActivity

class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):
        try:
            TypeTransaction.objects.get_or_create(libelle='Octroi de prêt', etiquette = TypeTransaction.OCTROIE_PRET)
            
            
            for pret in Pret.objects.filter(status__etiquette__in = [StatusPret.TERMINE, StatusPret.EN_COURS]):
                compte = pret.employe.agence.comptes.filter(activity__etiquette = TypeActivity.PRET).first()                
                Operation.objects.create(
                    libelle       = "Décaissement pour le prêt N°" + str(pret.numero),
                    compte_credit = None,
                    compte_debit  = compte,
                    montant       = pret.base,
                    employe       = pret.employe,
                )
                
        
            for operation in Operation.objects.filter(transaction__isnull=False):
                instance = operation.transaction
                if instance.type_transaction.etiquette in [TypeTransaction.DEPOT_FIDELIS, TypeTransaction.RETRAIT_FIDELIS]:
                    compte = instance.employe.agence.comptes.filter(activity__etiquette = TypeActivity.FIDELIS).first()
                    debit = instance.type_transaction.etiquette == TypeTransaction.RETRAIT_FIDELIS
                    
                elif instance.type_transaction.etiquette in [TypeTransaction.DEPOT, TypeTransaction.RETRAIT]:
                    compte = instance.employe.agence.comptes.filter(activity__etiquette = TypeActivity.EPARGNE).first()
                    debit = instance.type_transaction.etiquette == TypeTransaction.RETRAIT
                    
                elif instance.type_transaction.etiquette in [TypeTransaction.REMBOURSEMENT, TypeTransaction.OCTROIE_PRET]:
                    compte = instance.employe.agence.comptes.filter(activity__etiquette = TypeActivity.PRET).first()
                    debit = instance.type_transaction.etiquette == TypeTransaction.OCTROIE_PRET
                
                operation.compte_credit = compte if not debit else None
                operation.compte_debit  = compte if debit else None
                operation.save()
                print("Patch operation id {} done.".format(operation.id))
                
        except Exception as e:
            print("Erreur patch: ", e)