import logging
from datetime import date
from django.db import transaction
from django.utils import timezone
from .models import CompteEpargne, Echeance, Interet, Penalite, Epargne, StatusPret

logger = logging.getLogger(__name__)


def generer_penalites():
    """
    Vérifie les échéances échues et impayées,
    et crée une pénalité pour chacune.
    """
    today = date.today()

    # on cible les échéances échues et non réglées
    echeances = Echeance.objects.filter(
        date_echeance__lt=today,
        status = StatusPret.objects.get(etiquette = StatusPret.EN_COURS)
    )

    with transaction.atomic():
        for echeance in echeances:
            penalite, created = Penalite.objects.get_or_create(
                echeance=echeance,
                defaults={
                    "montant": echeance.calculer_penalite(),
                }
            )
            if created:
                logger.info(f"Pénalité générée pour échéance {echeance.level} de {echeance.pret.numero}")




def generer_interets_epargnes():
    """
    Calcule et crédite les intérêts pour chaque épargne active.
    """
    today = date.today()

    # suppose qu’on a un champ taux_interet (ex: 5%)
    epargnes = CompteEpargne.objects.filter(active=True)

    with transaction.atomic():
        for epargne in epargnes:
            interet = epargne.calculer_interet()
            if interet > 0:
                # ici tu peux soit créer une transaction de type INTERET
                Interet.objects.create(
                    compte      = epargne,
                    montant     = interet,
                    description = f"Intérêt de {epargne.taux}% sur l'épargne N°{epargne.numero}",
                )
