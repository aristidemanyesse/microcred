from django.test import TestCase
from django.urls import reverse

from CoreApp.tests import RefDataMixin
from AuthentificationApp.models import Employe


# ═══════════════════════════════════════════════════════════════════════════
# Tests 33-35 : login_ajax
# ═══════════════════════════════════════════════════════════════════════════

class LoginAjaxTests(RefDataMixin, TestCase):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        # Employé avec is_new=False (connexion normale possible)
        cls.emp = Employe.objects.create(
            username='emp_login', first_name='Login', last_name='Test',
            brut='passtest1', agence=cls.agence, role=cls.role_admin,
        )
        cls.emp.is_new = False
        cls.emp.set_password('passtest1')
        cls.emp.save()

    def setUp(self):
        self.url = reverse('AuthentificationApp:login_ajax')

    def test_33_login_ajax_succes(self):
        """Connexion réussie avec identifiants corrects → status=True"""
        resp = self.client.post(self.url, {
            'username': 'emp_login',
            'password': 'passtest1',
        })
        self.assertTrue(resp.json()['status'])

    def test_34_login_ajax_identifiants_invalides(self):
        """Mot de passe incorrect → status=False"""
        resp = self.client.post(self.url, {
            'username': 'emp_login',
            'password': 'mauvais_mdp',
        })
        self.assertFalse(resp.json()['status'])

    def test_35_login_ajax_employe_inactif(self):
        """Employé inactif → status=False même avec bon mot de passe"""
        Employe.objects.filter(pk=self.emp.pk).update(is_active=False)
        resp = self.client.post(self.url, {
            'username': 'emp_login',
            'password': 'passtest1',
        })
        self.assertFalse(resp.json()['status'])


# ═══════════════════════════════════════════════════════════════════════════
# Test 36 : first_user — initialisation du mot de passe
# ═══════════════════════════════════════════════════════════════════════════

class FirstUserTests(RefDataMixin, TestCase):

    def setUp(self):
        self.url = reverse('AuthentificationApp:first_user')
        # Employé "new" (premier login)
        self.emp = Employe.objects.create(
            username='emp_new', first_name='New', last_name='User',
            brut='initpass1', agence=self.agence, role=self.role_admin,
        )
        # Simuler ce que login_ajax stocke en session
        session = self.client.session
        session['user_id'] = str(self.emp.id)
        session.save()

    def test_36_first_user_vide_brut_et_desactive_is_new(self):
        """first_user initialise le compte, vide brut et passe is_new=False"""
        resp = self.client.post(self.url, {
            'username':       'nouveau_login',
            'password1':      'nouveau_mdp1',
            'password2':      'nouveau_mdp1',
            'phrase_secrete': 'Ma question secrète ?',
            'reponse_secrete': 'ma réponse',
        })
        data = resp.json()
        self.assertTrue(data['status'], data.get('message'))
        self.emp.refresh_from_db()
        self.assertEqual(self.emp.brut, '')
        self.assertFalse(self.emp.is_new)


# ═══════════════════════════════════════════════════════════════════════════
# Test 37 : refresh_password — contrôle des droits
# ═══════════════════════════════════════════════════════════════════════════

class RefreshPasswordTests(RefDataMixin, TestCase):

    def setUp(self):
        self.url = reverse('CoreApp:refresh_password')
        # Créer la cible du reset
        self.cible = Employe.objects.create(
            username='agent_cible', first_name='Cible', last_name='Test',
            brut='pass12345', agence=self.agence, role=self.role_pret,
        )

    def test_37_gestionnaire_ne_peut_pas_reinitialiser_mdp(self):
        """Un gestionnaire (is_employe=True) reçoit status=False"""
        self.client.force_login(self.employe_pret)
        resp = self.client.post(self.url, {
            'id': str(self.cible.id),
        })
        self.assertFalse(resp.json()['status'])
