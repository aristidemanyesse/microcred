from decimal import Decimal

from django.test import TestCase

from CoreApp.tests import RefDataMixin
from FidelisApp.models import CompteFidelis
from FinanceApp.models import StatusPret, Transaction, TypeTransaction


# ─── helper ─────────────────────────────────────────────────────────────────

def make_compte(customer, employe, base=10_000, nombre=3):
    return CompteFidelis.objects.create(
        client=customer,
        base=Decimal(str(base)),
        nombre=nombre,
        employe=employe,
    )


# ═══════════════════════════════════════════════════════════════════════════
# Tests 26-32 : CompteFidelis
# ═══════════════════════════════════════════════════════════════════════════

class FidelisTests(RefDataMixin, TestCase):

    def test_26_creation_genere_le_bon_nombre_de_cases(self):
        """Le signal pre_save ajoute 1 au nombre passé : nombre=3 → 4 cases"""
        compte = make_compte(self.customer, self.employe, nombre=3)
        # Le signal fait nombre += 1 → nombre stocké = 4 → 4 cases créées
        self.assertEqual(compte.nombre, 4)
        self.assertEqual(compte.cases.count(), 4)
        levels = list(compte.cases.values_list('level', flat=True).order_by('level'))
        self.assertEqual(levels, [1, 2, 3, 4])

    def test_27_deposer_clot_la_case_en_cours(self):
        """deposer() ferme la case EN_COURS la plus récente (ordering=-created_at)"""
        compte = make_compte(self.customer, self.employe, nombre=3)
        # Le signal crée 4 cases (niveau 1→4). L'ordering par défaut est -created_at,
        # donc cases.first() renvoie la case de niveau le plus élevé.
        case_la_plus_recente = compte.cases.first()  # niveau 4

        compte.deposer(self.employe, self.mode_espece, 'test')
        case_la_plus_recente.refresh_from_db()
        self.assertEqual(case_la_plus_recente.status.etiquette, StatusPret.TERMINE)

    def test_28_deposer_clot_compte_quand_toutes_cases_terminees(self):
        """nombre=3 → 4 cases (signal +1) → 4 dépôts clôturent le compte"""
        compte = make_compte(self.customer, self.employe, nombre=3)
        for _ in range(4):  # 4 cases créées car signal ajoute 1
            compte.deposer(self.employe, self.mode_espece, 'test')
        compte.refresh_from_db()
        self.assertEqual(compte.status.etiquette, StatusPret.TERMINE)
        self.assertIsNotNone(compte.cloture_at)

    def test_29_retirer_cree_transaction_et_marque_retire(self):
        """retirer() crée une transaction RETRAIT_FIDELIS et passe retire=True"""
        compte = make_compte(self.customer, self.employe, base=10_000, nombre=2)
        compte.deposer(self.employe, self.mode_espece, 'dépôt 1')
        compte.deposer(self.employe, self.mode_espece, 'dépôt 2')
        compte.retirer(self.employe, self.mode_espece, 'retrait final')
        compte.refresh_from_db()
        self.assertTrue(compte.retire)
        tx = Transaction.objects.filter(
            fidelis=compte,
            type_transaction__etiquette=TypeTransaction.RETRAIT_FIDELIS,
        ).first()
        self.assertIsNotNone(tx)

    def test_30_retirer_leve_erreur_si_deja_retire(self):
        """retirer() une 2ème fois lève ValueError"""
        compte = make_compte(self.customer, self.employe, base=10_000, nombre=2)
        compte.deposer(self.employe, self.mode_espece, 'd1')
        compte.deposer(self.employe, self.mode_espece, 'd2')
        compte.retirer(self.employe, self.mode_espece, 'retrait 1')
        with self.assertRaises(ValueError):
            compte.retirer(self.employe, self.mode_espece, 'retrait 2')

    def test_31_retirer_leve_erreur_si_solde_insuffisant(self):
        """retirer() sans dépôt lève ValueError (solde=0 < frais=base)"""
        compte = make_compte(self.customer, self.employe, base=10_000, nombre=3)
        with self.assertRaises(ValueError):
            compte.retirer(self.employe, self.mode_espece, 'retrait sans dépôt')

    def test_32_solde_calcul_correct(self):
        """solde() = total_payes - total_retire"""
        compte = make_compte(self.customer, self.employe, base=10_000, nombre=3)
        compte.deposer(self.employe, self.mode_espece, 'd1')
        compte.deposer(self.employe, self.mode_espece, 'd2')
        # 2 cases payées × 10 000 = 20 000 ; aucun retrait
        self.assertEqual(compte.solde(), Decimal('20000'))
