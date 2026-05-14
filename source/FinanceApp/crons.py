import logging
from datetime import date, datetime
from django.db import transaction
from .models import (
    CompteEpargne, Echeance, Interet, ModaliteEcheance, Penalite, StatusPret,
)

logger = logging.getLogger(__name__)


def generer_penalites():
    """
    Vérifie les échéances échues et impayées,
    et crée une pénalité par période de retard écoulée depuis la dernière.
    """
    logger.info("Génération des pénalités — %s", datetime.now())
    today = date.today()

    echeances = (
        Echeance.objects
        .filter(date_echeance__lt=today, deleted=False)
        .exclude(status__etiquette__in=[StatusPret.ANNULEE, StatusPret.TERMINE])
        .select_related("pret__modalite")
        .order_by("date_echeance")
    )

    with transaction.atomic():
        for echeance in echeances:
            if echeance.derniere_date_penalite:
                prochaine = echeance.derniere_date_penalite + echeance.pret.modalite.duree()
                if today < prochaine:
                    continue

            penalite = Penalite.objects.create(
                echeance    = echeance,
                montant     = echeance.calculer_penalite(),
                description = f"Pénalité échéance N°{echeance.level} du prêt {echeance.pret.numero}",
            )
            logger.info("Pénalité créée pour échéance %s du prêt %s", echeance.level, echeance.pret.numero)


def generer_interets_epargnes():
    """
    Calcule et crédite les intérêts pour chaque épargne active.
    """
    logger.info("Génération des intérêts épargne — %s", datetime.now())
    today = date.today()
    epargnes = CompteEpargne.objects.filter(
        deleted=False,
        status__etiquette=StatusPret.EN_COURS,
    ).select_related("modalite")

    for epargne in epargnes:
        if epargne.derniere_date_interet and epargne.derniere_date_interet >= today:
            continue

        periodicite = epargne.modalite.etiquette
        doit_crediter = False

        if periodicite == ModaliteEcheance.HEBDOMADAIRE and today.weekday() == 0:
            doit_crediter = True
        elif periodicite == ModaliteEcheance.MENSUEL and today.day == 1:
            doit_crediter = True
        elif periodicite == ModaliteEcheance.BIMENSUEL and today.day == 1 and today.month % 2 == 1:
            doit_crediter = True
        elif periodicite == ModaliteEcheance.TRIMESTRIEL and today.day == 1 and today.month in [1, 4, 7, 10]:
            doit_crediter = True
        elif periodicite == ModaliteEcheance.SEMESTRIEL and today.day == 1 and today.month in [1, 7]:
            doit_crediter = True
        elif periodicite == ModaliteEcheance.ANNUEL and today.day == 1 and today.month == 1:
            doit_crediter = True

        if doit_crediter:
            interet = epargne.calculer_interet_prorata(today)
            if interet > 0:
                with transaction.atomic():
                    Interet.objects.create(
                        compte      = epargne,
                        montant     = interet,
                        description = f"Intérêt {epargne.modalite} de {epargne.taux}%",
                    )
                    logger.info("Intérêt créé pour épargne %s", epargne.numero)
