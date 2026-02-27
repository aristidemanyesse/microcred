from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.db.models import Sum
from TresorApp.models import CompteAgence, Operation, TypeActivity
from FinanceApp.models import CompteEpargne, Echeance, ModePayement, Pret, StatusPret, Transaction, TypeTransaction
from FidelisApp.models import CompteFidelis
from django.db import transaction


class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):
        try:
            
            with transaction.atomic():
                for pret in Pret.objects.filter(deleted=False, status__etiquette__in=[StatusPret.EN_COURS, StatusPret.TERMINE]).order_by("created_at"):
                    if not Transaction.objects.filter(pret=pret, type_transaction__etiquette=TypeTransaction.OCTROIE_PRET).exists():
                        print(pret.numero)
                        trx = Transaction.objects.create(
                            client = pret.client,
                            mode = ModePayement.objects.get(etiquette=ModePayement.ESPECE),
                            type_transaction = TypeTransaction.objects.get(etiquette=TypeTransaction.OCTROIE_PRET),
                            montant = pret.base,
                            employe = pret.employe,
                            pret = pret,
                            commentaire = f"Décaissement pour le prêt N°{pret.numero}"
                        )
                        if trx:
                            trx.created_at = pret.created_at
                            trx.update_at = pret.created_at
                            trx.save(update_fields=["created_at", "update_at"])
                            
                            ope = Operation.objects.filter(transaction=trx).first()
                            if ope:
                                ope.pret = pret
                                ope.transaction = trx if trx else None
                                ope.created_at = pret.created_at
                                ope.update_at = pret.created_at
                                ope.save(update_fields=["pret", "transaction", "created_at", "update_at"])
            
            
                for trx in Transaction.objects.filter(type_transaction__etiquette=TypeTransaction.OCTROIE_PRET):
                    if not Operation.objects.filter(transaction=trx).exists():
                        print(f"Transaction sans opération: {trx.id} - {trx.commentaire}")
                        ope = Operation.objects.create(
                            libelle = trx.commentaire or f"Opération pour {trx.type_transaction.libelle}",
                            montant = trx.montant,
                            compte_credit = trx.employe.agence.comptes.filter(activity__etiquette=TypeActivity.PRET).first(),
                            pret = trx.pret,
                            transaction = trx,
                            employe = trx.employe
                        )
                        if ope:
                            ope.created_at = trx.created_at
                            ope.update_at = trx.created_at
                            ope.save(update_fields=["created_at", "update_at"])
                            
                            
                            
                for echeance in Echeance.objects.filter(deleted=False).order_by("created_at"):
                    if echeance.montant_restant() >  0:
                        echeance.status = StatusPret.objects.get(etiquette = StatusPret.EN_COURS)
                        echeance.save(update_fields=["status"])
                        
                for echeance in Echeance.objects.filter(deleted=False).order_by("created_at"):
                    echeance.principal_paye = 0
                    echeance.interet_paye = 0
                    echeance.penalites_payees = 0
                    echeance.save(update_fields=["principal_paye", "interet_paye", "penalites_payees"])
                    

                    

                    print(f"Traitement de l'échéance {echeance.id} du prêt {echeance.pret.numero}")
                    for trx in echeance.transactions.filter(deleted=False).order_by("created_at"):
                        
                        penalites_total = echeance.penalites_montant(date=trx.created_at)
                        penalites_restantes = max(penalites_total - echeance.penalites_payees, 0)

                        interet_restant = max(echeance.interet - (echeance.interet_paye or 0), 0)
                        principal_restant = max(echeance.principal - (echeance.principal_paye or 0), 0)
            
                        reste = trx.montant 
                        
                        trx.penalite_part = min(reste, penalites_restantes)
                        reste -= trx.penalite_part
                        echeance.penalites_payees += trx.penalite_part
                        
                        trx.interet_part = min(reste, interet_restant)
                        reste -= trx.interet_part
                        echeance.interet_paye += trx.interet_part
                        
                        trx.principal_part = min(reste, principal_restant)
                        reste -= trx.principal_part
                        echeance.principal_paye += trx.principal_part
                        
                        # Par sécurité : on ne devrait pas avoir de reste > 0, vu le check restant_total
                        # mais si arrondi, on force sur l'intérêt (ou sur principal) selon ta politique.
                        if reste > 0:
                            # on pousse le résiduel sur l'intérêt (option)
                            trx.interet_part += reste
                            echeance.interet_paye += reste
                            reste = 0
                        
                        trx.save(update_fields=["penalite_part", "interet_part", "principal_part"])
                        echeance.save(update_fields=["penalites_payees", "interet_paye", "principal_paye"])
                        
                
                
                
                
                
                
                
                
                
                
                
                
                                
            # 
            # for echeance in Echeance.objects.filter(deleted=False):
                # t_remb = TypeTransaction.objects.get(etiquette=TypeTransaction.REMBOURSEMENT)
                # penalites_deja_payees = (
                    # Transaction.objects
                    # .filter(echeance=echeance, type_transaction=t_remb, deleted=False)
                    # .aggregate(s=Sum("penalite_part"))["s"] or 0
                # )
                # echeance.penalites_payees = penalites_deja_payees
                # echeance.save()
            
            # print(prets.count())
            # for pret in prets:
            #     print(f"{pret}\t{pret.echeances.filter().count()}\t{pret.base}\t{pret.taux}\t{pret.interet}\t{pret.montant_rembourse()}\t{pret.created_at.date()}\t{pret.client}")
                # for echeance in pret.echeances.filter():
                #     print(echeance.montant_paye)
                
        except Exception as e:
            print("Erreur patch: ", e)