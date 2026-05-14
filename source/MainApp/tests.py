from decimal import Decimal

from django.test import TestCase

from CoreApp.tests import RefDataMixin
from FinanceApp.models import CompteEpargne, Penalite, Pret


# ─── helper ─────────────────────────────────────────────────────────────────

def make_pret_decaisse(customer, employe, modalite, amortissement):
    pret = Pret.objects.create(
        client=customer, base=Decimal('100000'), taux=10, taux_penalite=10,
        modalite=modalite, nombre_modalite=4,
        amortissement=amortissement, employe=employe,
    )
    pret.decaissement(employe)
    return pret


# ═══════════════════════════════════════════════════════════════════════════
# Tests 38-40 : méthodes d'agrégat sur Client
# ═══════════════════════════════════════════════════════════════════════════

class ClientAggregatsTests(RefDataMixin, TestCase):

    def test_38_total_epargne_somme_des_soldes(self):
        """total_epargne() additionne le solde de tous les comptes épargne"""
        ep1 = CompteEpargne.objects.create(
            client=self.customer, taux=Decimal('5'),
            modalite=self.mod_mensuel, employe=self.employe,
        )
        ep2 = CompteEpargne.objects.create(
            client=self.customer, taux=Decimal('5'),
            modalite=self.mod_mensuel, employe=self.employe,
        )
        ep1.deposer(Decimal('30000'), self.employe, self.mode_espece)
        ep2.deposer(Decimal('20000'), self.employe, self.mode_espece)
        self.assertEqual(self.customer.total_epargne(), Decimal('50000'))

    def test_39_total_prets_en_cours_reste_a_payer(self):
        """total_prets_en_cours() = montant − remboursé pour les prêts EN_COURS"""
        pret = make_pret_decaisse(
            self.customer, self.employe, self.mod_mensuel, self.amort_base,
        )
        expected = pret.montant - pret.montant_rembourse()
        self.assertEqual(self.customer.total_prets_en_cours(), expected)

    def test_40_total_penalites_cumule_toutes_penalites(self):
        """total_penalites() additionne toutes les pénalités non supprimées"""
        pret = make_pret_decaisse(
            self.customer, self.employe, self.mod_mensuel, self.amort_base,
        )
        ech = pret.echeances.first()
        Penalite.objects.create(echeance=ech, montant=Decimal('500'))
        Penalite.objects.create(echeance=ech, montant=Decimal('300'))
        self.assertEqual(self.customer.total_penalites(), Decimal('800'))
