from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse

from CoreApp.tests import RefDataMixin
from FinanceApp.models import (
    CompteEpargne, Echeance, Interet, Penalite,
    Pret, Transaction, StatusPret,
)
from FinanceApp.crons import generer_penalites, generer_interets_epargnes
from TresorApp.models import Operation


# ─── helpers ────────────────────────────────────────────────────────────────

def make_pret(customer, employe, modalite, amortissement,
              base=100_000, taux=10, nombre=4):
    return Pret.objects.create(
        client=customer, base=base, taux=taux, taux_penalite=10,
        modalite=modalite, nombre_modalite=nombre,
        amortissement=amortissement, employe=employe,
    )


def make_pret_decaisse(customer, employe, modalite, amortissement,
                       base=100_000, taux=10, nombre=4):
    pret = make_pret(customer, employe, modalite, amortissement,
                     base=base, taux=taux, nombre=nombre)
    pret.decaissement(employe)
    return pret


# ═══════════════════════════════════════════════════════════════════════════
# Tests 1-2 : Pret.calcul_interets()
# ═══════════════════════════════════════════════════════════════════════════

class PretAmortissementTests(RefDataMixin, TestCase):

    def test_01_calcul_interets_base(self):
        """BASE : intérêt = base × taux%  et  montant = base + intérêt"""
        pret = make_pret(self.customer, self.employe,
                         self.mod_mensuel, self.amort_base,
                         base=100_000, taux=10, nombre=4)
        self.assertEqual(pret.interet, Decimal('10000.00'))
        self.assertEqual(pret.montant, Decimal('110000.00'))

    def test_02_calcul_interets_annuite(self):
        """ANNUITÉ : intérêt > 0, montant = base + intérêt, total ≈ 12 × annuité"""
        pret = make_pret(self.customer, self.employe,
                         self.mod_mensuel, self.amort_annuite,
                         base=100_000, taux=24, nombre=12)
        self.assertGreater(pret.interet, 0)
        self.assertEqual(pret.montant, pret.base + pret.interet)
        # taux périodique = 24%/12 = 2% → annuité théorique ≈ 9 455,96
        # 12 × 9 455,96 ≈ 113 471
        self.assertAlmostEqual(float(pret.montant), 113_471, delta=15)


# ═══════════════════════════════════════════════════════════════════════════
# Tests 3-7 : Pret.decaissement()
# ═══════════════════════════════════════════════════════════════════════════

class PretDecaissementTests(RefDataMixin, TestCase):

    def test_03_decaissement_base_nombre_echeances(self):
        """BASE : crée exactement nombre_modalite échéances"""
        pret = make_pret_decaisse(self.customer, self.employe,
                                  self.mod_mensuel, self.amort_base, nombre=4)
        self.assertEqual(pret.echeances.count(), 4)

    def test_04_decaissement_base_montants_par_echeance(self):
        """BASE : principal, intérêt et montant_a_payer corrects sur chaque échéance"""
        pret = make_pret_decaisse(self.customer, self.employe,
                                  self.mod_mensuel, self.amort_base,
                                  base=100_000, taux=10, nombre=4)
        for ech in pret.echeances.all():
            self.assertEqual(ech.principal,       Decimal('25000.00'))
            self.assertEqual(ech.interet,          Decimal('2500.00'))
            self.assertEqual(ech.montant_a_payer,  Decimal('27500.00'))

    def test_05_decaissement_annuite_echeances_constantes(self):
        """ANNUITÉ : 12 échéances créées avec annuité constante (±1 F d'arrondi)"""
        pret = make_pret_decaisse(self.customer, self.employe,
                                  self.mod_mensuel, self.amort_annuite,
                                  base=100_000, taux=24, nombre=12)
        echeances = list(pret.echeances.order_by('level'))
        self.assertEqual(len(echeances), 12)
        montants = [float(e.montant_a_payer) for e in echeances]
        self.assertAlmostEqual(max(montants), min(montants), delta=1)

    def test_06_decaissement_cree_transaction_octroie_pret(self):
        """Le décaissement crée une transaction OCTROIE_PRET avec montant = base"""
        pret = make_pret_decaisse(self.customer, self.employe,
                                  self.mod_mensuel, self.amort_base)
        tx = Transaction.objects.filter(
            pret=pret,
            type_transaction__etiquette=self.tt_octroie.etiquette,
        ).first()
        self.assertIsNotNone(tx)
        self.assertEqual(tx.montant, pret.base)

    def test_07_decaissement_guard_deja_decaisse(self):
        """Un 2ème appel à decaissement() lève ValueError"""
        pret = make_pret_decaisse(self.customer, self.employe,
                                  self.mod_mensuel, self.amort_base)
        with self.assertRaises(ValueError):
            pret.decaissement(self.employe)


# ═══════════════════════════════════════════════════════════════════════════
# Tests 8-14 : Pret.reste_a_payer / progress / penalites / Echeance.regler
# ═══════════════════════════════════════════════════════════════════════════

class RemboursementTests(RefDataMixin, TestCase):

    def setUp(self):
        # Prêt BASE : 100 000 F, 10%, 4 mois → 4 échéances de 27 500 F
        self.pret = make_pret_decaisse(
            self.customer, self.employe,
            self.mod_mensuel, self.amort_base,
            base=100_000, taux=10, nombre=4,
        )

    def _ech(self, level=1):
        return self.pret.echeances.order_by('level')[level - 1]

    def test_08_reste_a_payer_apres_paiement_partiel(self):
        """reste_a_payer() diminue correctement après un remboursement"""
        self._ech(1).regler(Decimal('27500'), self.employe, self.mode_espece, 'test')
        # 110 000 - 27 500 = 82 500
        self.assertEqual(self.pret.reste_a_payer(), Decimal('82500.00'))

    def test_09_progress_apres_un_paiement(self):
        """progress() = 25 % après avoir réglé 1 échéance sur 4"""
        self._ech(1).regler(Decimal('27500'), self.employe, self.mode_espece, 'test')
        self.assertEqual(self.pret.progress(), 25)

    def test_10_penalites_montant_cumule(self):
        """penalites_montant() additionne les pénalités de toutes les échéances"""
        ech = self._ech(1)
        Penalite.objects.create(echeance=ech, montant=Decimal('1000'))
        Penalite.objects.create(echeance=ech, montant=Decimal('500'))
        self.assertEqual(self.pret.penalites_montant(), Decimal('1500'))

    def test_11_regler_paiement_total_clot_echeance(self):
        """Un paiement complet passe l'échéance en TERMINE"""
        ech = self._ech(1)
        ech.regler(Decimal('27500'), self.employe, self.mode_espece, 'test')
        ech.refresh_from_db()
        self.assertEqual(ech.status.etiquette, StatusPret.TERMINE)
        self.assertEqual(ech.montant_paye, Decimal('27500'))

    def test_12_regler_ventilation_penalite_interet_principal(self):
        """Ventilation : pénalités d'abord, puis intérêts, puis principal"""
        ech = self._ech(1)
        Penalite.objects.create(echeance=ech, montant=Decimal('2750'))
        # Payer pénalité (2 750) + intérêt (2 500) uniquement
        ech.regler(Decimal('5250'), self.employe, self.mode_espece, 'test')
        ech.refresh_from_db()
        self.assertEqual(ech.penalites_payees, Decimal('2750'))
        self.assertEqual(ech.interet_paye,     Decimal('2500'))
        self.assertEqual(ech.principal_paye,   Decimal('0'))

    def test_13_regler_paiement_final_clot_pret(self):
        """Solder la dernière échéance passe le prêt en TERMINE"""
        # Prêt à 1 seule échéance pour simplifier
        pret = make_pret_decaisse(
            self.customer, self.employe,
            self.mod_mensuel, self.amort_base,
            base=100_000, taux=10, nombre=1,
        )
        ech = pret.echeances.first()
        ech.regler(ech.montant_a_payer, self.employe, self.mode_espece, 'solde total')
        pret.refresh_from_db()
        self.assertEqual(pret.status.etiquette, StatusPret.TERMINE)

    def test_14_regler_leve_erreur_si_montant_superieur(self):
        """regler() lève ValueError si montant > restant dû"""
        ech = self._ech(1)  # montant_restant = 27 500
        with self.assertRaises(ValueError):
            ech.regler(Decimal('50000'), self.employe, self.mode_espece, 'test')


# ═══════════════════════════════════════════════════════════════════════════
# Tests 15-16 : AJAX new_remboursement
# ═══════════════════════════════════════════════════════════════════════════

class AjaxRemboursementTests(RefDataMixin, TestCase):

    def setUp(self):
        self.pret = make_pret_decaisse(
            self.customer, self.employe,
            self.mod_mensuel, self.amort_base,
            base=100_000, taux=10, nombre=4,
        )
        self.client.force_login(self.employe)
        self.url = reverse('FinanceApp:new_remboursement')

    def test_15_ajax_remboursement_multi_echeances(self):
        """Payer 2 × 27 500 en un POST solde les 2 premières échéances"""
        resp = self.client.post(self.url, {
            'id':          str(self.pret.pk),
            'mode':        str(self.mode_espece.pk),
            'montant':     '55000',
            'commentaire': 'test multi',
        })
        data = resp.json()
        self.assertTrue(data['status'], data.get('message'))
        echeances = list(
            self.pret.echeances.order_by('level').select_related('status')
        )
        self.assertEqual(echeances[0].status.etiquette, StatusPret.TERMINE)
        self.assertEqual(echeances[1].status.etiquette, StatusPret.TERMINE)
        self.assertEqual(echeances[2].status.etiquette, StatusPret.EN_COURS)

    def test_16_ajax_remboursement_refuse_si_montant_superieur(self):
        """Montant > reste à payer → réponse status=False"""
        resp = self.client.post(self.url, {
            'id':          str(self.pret.pk),
            'mode':        str(self.mode_espece.pk),
            'montant':     '999999',
            'commentaire': 'test',
        })
        self.assertFalse(resp.json()['status'])


# ═══════════════════════════════════════════════════════════════════════════
# Tests 17-19 : CompteEpargne dépôt / retrait
# ═══════════════════════════════════════════════════════════════════════════

class CompteEpargneTests(RefDataMixin, TestCase):

    def _ep(self, taux='5.00'):
        return CompteEpargne.objects.create(
            client=self.customer, taux=Decimal(taux),
            modalite=self.mod_mensuel, employe=self.employe,
        )

    def test_17_deposer_met_a_jour_solde(self):
        """deposer() crédite le solde_actuel et le solde calculé"""
        ep = self._ep()
        ep.deposer(Decimal('50000'), self.employe, self.mode_espece)
        ep.refresh_from_db()
        self.assertEqual(ep.solde_actuel, Decimal('50000'))
        self.assertEqual(ep.solde(), Decimal('50000'))

    def test_18_retirer_met_a_jour_solde(self):
        """retirer() débite le solde correctement"""
        ep = self._ep()
        ep.deposer(Decimal('50000'), self.employe, self.mode_espece)
        ep.retirer(Decimal('20000'), self.employe, self.mode_espece)
        ep.refresh_from_db()
        self.assertEqual(ep.solde_actuel, Decimal('30000'))

    def test_19_retirer_leve_erreur_si_solde_insuffisant(self):
        """retirer() lève ValueError quand solde < montant"""
        ep = self._ep()
        ep.deposer(Decimal('10000'), self.employe, self.mode_espece)
        with self.assertRaises(ValueError):
            ep.retirer(Decimal('20000'), self.employe, self.mode_espece)


# ═══════════════════════════════════════════════════════════════════════════
# Tests 20-21 : calculer_interet_prorata()
# ═══════════════════════════════════════════════════════════════════════════

class InteretProrataTests(RefDataMixin, TestCase):

    def _ep_avec_depot(self, taux=12, montant=100_000, created=None):
        ep = CompteEpargne.objects.create(
            client=self.customer, taux=Decimal(str(taux)),
            modalite=self.mod_mensuel, employe=self.employe,
        )
        if created:
            ep.created_at = created  # contrôle la date de création pour le prorata
        ep.deposer(Decimal(str(montant)), self.employe, self.mode_espece)
        return ep

    def test_20_prorata_mensuel_mois_plein(self):
        """Compte ouvert avant la période → prorata = 1 → intérêt = solde × taux%"""
        ep = self._ep_avec_depot(
            taux=12, montant=100_000,
            created=datetime(2025, 1, 1, tzinfo=timezone.utc),
        )
        # today = 31 jan → jours_ecoules = 31, jours_periode = 31 → prorata = 1
        interet = ep.calculer_interet_prorata(today=date(2025, 1, 31))
        expected = round(100_000 * 0.12 * 1.0, 2)
        self.assertAlmostEqual(interet, expected, places=1)

    def test_21_prorata_compte_ouvert_mi_periode(self):
        """Compte ouvert le 15 → prorata < 1 → intérêt proportionnel"""
        ep = self._ep_avec_depot(
            taux=12, montant=100_000,
            created=datetime(2025, 1, 15, tzinfo=timezone.utc),
        )
        # today = 31 jan : jours_ecoules = 17, jours_periode = 31
        interet = ep.calculer_interet_prorata(today=date(2025, 1, 31))
        interet_plein = 100_000 * 0.12
        self.assertLess(interet, interet_plein)
        expected = round(interet_plein * 17 / 31, 2)
        self.assertAlmostEqual(interet, expected, places=1)


# ═══════════════════════════════════════════════════════════════════════════
# Tests 22-23 : cron generer_penalites
# ═══════════════════════════════════════════════════════════════════════════

class CronPenalitesTests(RefDataMixin, TestCase):

    def _pret_avec_echeance_en_retard(self):
        pret = make_pret_decaisse(
            self.customer, self.employe,
            self.mod_mensuel, self.amort_base,
            base=100_000, taux=10, nombre=4,
        )
        ech = pret.echeances.order_by('level').first()
        ech.date_echeance = date.today() - timedelta(days=35)
        ech.save(update_fields=['date_echeance'])
        return pret, ech

    def test_22_generer_penalites_cree_penalite_si_retard(self):
        """Le cron crée une pénalité pour une échéance échue et impayée"""
        pret, ech = self._pret_avec_echeance_en_retard()
        generer_penalites()
        self.assertGreater(ech.penalites.filter(deleted=False).count(), 0)

    def test_23_generer_penalites_ignore_echeances_futures(self):
        """Le cron ne crée aucune pénalité si toutes les échéances sont à venir"""
        make_pret_decaisse(
            self.customer, self.employe,
            self.mod_mensuel, self.amort_base,
            base=100_000, taux=10, nombre=4,
        )
        before = Penalite.objects.count()
        generer_penalites()
        self.assertEqual(Penalite.objects.count(), before)


# ═══════════════════════════════════════════════════════════════════════════
# Test 24 : cron generer_interets_epargnes
# ═══════════════════════════════════════════════════════════════════════════

class CronInteretsTests(RefDataMixin, TestCase):

    def test_24_generer_interets_le_premier_du_mois(self):
        """Le cron crédite un intérêt mensuel uniquement le 1er du mois"""
        ep = CompteEpargne.objects.create(
            client=self.customer, taux=Decimal('5.00'),
            modalite=self.mod_mensuel, employe=self.employe,
        )
        ep.deposer(Decimal('100000'), self.employe, self.mode_espece)

        # Simuler un 1er du mois
        with patch('FinanceApp.crons.date') as mock_date:
            mock_date.today.return_value = date(2026, 6, 1)
            generer_interets_epargnes()

        self.assertEqual(Interet.objects.filter(compte=ep).count(), 1)


# ═══════════════════════════════════════════════════════════════════════════
# Test 25 : signal post_save_transaction → Operation trésorerie
# ═══════════════════════════════════════════════════════════════════════════

class SignalTransactionTests(RefDataMixin, TestCase):

    def test_25_depot_epargne_cree_operation_treso(self):
        """Un dépôt épargne crée une Operation créditée sur le CompteAgence EPARGNE"""
        ep = CompteEpargne.objects.create(
            client=self.customer, taux=Decimal('5.00'),
            modalite=self.mod_mensuel, employe=self.employe,
        )
        before = Operation.objects.count()
        ep.deposer(Decimal('50000'), self.employe, self.mode_espece)
        self.assertEqual(Operation.objects.count(), before + 1)
        op = Operation.objects.order_by('-created_at').first()
        self.assertIsNotNone(op.compte_credit)
        self.assertIsNone(op.compte_debit)
