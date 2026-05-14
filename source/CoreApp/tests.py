from django.test import TestCase

from MainApp.models import Agence, Client, Genre, TypeClient
from AuthentificationApp.models import Employe, Role
from FinanceApp.models import (
    ModePayement, ModaliteEcheance, StatusPret,
    TypeAmortissement, TypeTransaction,
)
from TresorApp.models import TypeActivity


class RefDataMixin:
    """
    Crée toutes les données de référence nécessaires aux tests.
    À utiliser EN PREMIER dans la MRO : class MyTest(RefDataMixin, TestCase)

    Utilise cls.customer (pas cls.client) pour éviter le conflit avec
    self.client (client HTTP de Django TestCase).
    """

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        # 1. TypeActivity en premier : le signal post_save d'Agence en a besoin
        cls.activity_pret    = TypeActivity.objects.create(libelle='Prêt',    etiquette=TypeActivity.PRET)
        cls.activity_epargne = TypeActivity.objects.create(libelle='Épargne', etiquette=TypeActivity.EPARGNE)
        cls.activity_fidelis = TypeActivity.objects.create(libelle='Fidélis', etiquette=TypeActivity.FIDELIS)

        # 2. StatusPret
        cls.st_annulee  = StatusPret.objects.create(libelle='Annulé',     etiquette=StatusPret.ANNULEE,    classe='danger')
        cls.st_attente  = StatusPret.objects.create(libelle='En attente', etiquette=StatusPret.EN_ATTENTE, classe='light')
        cls.st_valide   = StatusPret.objects.create(libelle='Validé',     etiquette=StatusPret.VALIDE,     classe='secondary')
        cls.st_en_cours = StatusPret.objects.create(libelle='En cours',   etiquette=StatusPret.EN_COURS,   classe='primary')
        cls.st_termine  = StatusPret.objects.create(libelle='Terminé',    etiquette=StatusPret.TERMINE,    classe='success')
        cls.st_retard   = StatusPret.objects.create(libelle='Retard',     etiquette=StatusPret.RETARD,     classe='warning')

        # 3. TypeTransaction
        cls.tt_depot           = TypeTransaction.objects.create(libelle='Dépôt épargne',  etiquette=TypeTransaction.DEPOT)
        cls.tt_retrait         = TypeTransaction.objects.create(libelle='Retrait épargne', etiquette=TypeTransaction.RETRAIT)
        cls.tt_remb            = TypeTransaction.objects.create(libelle='Remboursement',   etiquette=TypeTransaction.REMBOURSEMENT)
        cls.tt_octroie         = TypeTransaction.objects.create(libelle='Octroi de prêt',  etiquette=TypeTransaction.OCTROIE_PRET)
        cls.tt_depot_fidelis   = TypeTransaction.objects.create(libelle='Dépôt Fidélis',   etiquette=TypeTransaction.DEPOT_FIDELIS)
        cls.tt_retrait_fidelis = TypeTransaction.objects.create(libelle='Retrait Fidélis', etiquette=TypeTransaction.RETRAIT_FIDELIS)

        # 4. ModaliteEcheance
        cls.mod_hebdo       = ModaliteEcheance.objects.create(libelle='Hebdomadaire', libelle2='semaine',   etiquette=ModaliteEcheance.HEBDOMADAIRE)
        cls.mod_mensuel     = ModaliteEcheance.objects.create(libelle='Mensuel',      libelle2='mois',      etiquette=ModaliteEcheance.MENSUEL)
        cls.mod_bimensuel   = ModaliteEcheance.objects.create(libelle='Bimensuel',    libelle2='bimestre',  etiquette=ModaliteEcheance.BIMENSUEL)
        cls.mod_trimestriel = ModaliteEcheance.objects.create(libelle='Trimestriel',  libelle2='trimestre', etiquette=ModaliteEcheance.TRIMESTRIEL)
        cls.mod_semestriel  = ModaliteEcheance.objects.create(libelle='Semestriel',   libelle2='semestre',  etiquette=ModaliteEcheance.SEMESTRIEL)
        cls.mod_annuel      = ModaliteEcheance.objects.create(libelle='Annuel',       libelle2='an',        etiquette=ModaliteEcheance.ANNUEL)

        # 5. ModePayement
        cls.mode_espece   = ModePayement.objects.create(libelle='Espèces',  etiquette=ModePayement.ESPECE)
        cls.mode_mobile   = ModePayement.objects.create(libelle='Mobile',   etiquette=ModePayement.MOBILE)
        cls.mode_cheque   = ModePayement.objects.create(libelle='Chèque',   etiquette=ModePayement.CHEQUE)
        cls.mode_virement = ModePayement.objects.create(libelle='Virement', etiquette=ModePayement.VIREMENT)

        # 6. TypeAmortissement
        cls.amort_base    = TypeAmortissement.objects.create(libelle='Capital+intérêts constants', etiquette=TypeAmortissement.BASE)
        cls.amort_annuite = TypeAmortissement.objects.create(libelle='Annuité constante',          etiquette=TypeAmortissement.ANNUITE)

        # 7. Rôles
        cls.role_admin   = Role.objects.create(libelle='Administrateur', etiquette=Role.ADMINISTRATEUR,       description='')
        cls.role_sup     = Role.objects.create(libelle='Superviseur',    etiquette=Role.SUPERVISEUR,          description='')
        cls.role_epargne = Role.objects.create(libelle='Gest. Épargne', etiquette=Role.GESTIONNAIRE_EPARGNE,  description='')
        cls.role_pret    = Role.objects.create(libelle='Gest. Prêt',    etiquette=Role.GESTIONNAIRE_PRET,     description='')

        # 8. Agence — le signal post_save crée 3 CompteAgence (PRET / FIDELIS / EPARGNE)
        cls.agence = Agence.objects.create(
            libelle='Agence Test', adresse='Test', ville='Test', code='TST',
        )

        # 9. Employés (le signal pre_save initialise is_active, is_new et le mot de passe)
        cls.employe = Employe.objects.create(
            username='agent_test', first_name='Agent', last_name='Test',
            brut='motdepasse1', agence=cls.agence, role=cls.role_admin,
        )
        cls.employe_epargne = Employe.objects.create(
            username='agent_epargne', first_name='Epargne', last_name='Test',
            brut='motdepasse1', agence=cls.agence, role=cls.role_epargne,
        )
        cls.employe_pret = Employe.objects.create(
            username='agent_pret', first_name='Pret', last_name='Test',
            brut='motdepasse1', agence=cls.agence, role=cls.role_pret,
        )

        # 10. TypeClient & Genre
        cls.type_client = TypeClient.objects.create(libelle='Particulier', etiquette=TypeClient.PARTICULIER)
        cls.genre       = Genre.objects.create(libelle='Homme',            etiquette=Genre.HOMME)

        # 11. Client (le signal pre_save assigne agence et génère le numéro)
        cls.customer = Client.objects.create(
            type_client=cls.type_client,
            nom='Dupont', prenoms='Jean', genre=cls.genre,
            profession='Commerçant', adresse='Abidjan', telephone='0101010101',
            employe=cls.employe,
        )
