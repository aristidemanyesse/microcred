from datetime import date, datetime
from django.db import transaction
from .models import *

def generer_penalites():
    """
    Vérifie les échéances échues et impayées,
    et crée une pénalité pour chacune.
    """
    print("Création des pénalités ...", datetime.now())
    today = date.today()

    # on cible les échéances échues et non réglées
    echeances = Echeance.objects.filter(date_echeance__lt=today).exclude(status__etiquette__in = [StatusPret.ANNULEE, StatusPret.TERMINE]).order_by("date_echeance")
    with transaction.atomic():
        for echeance in echeances:
            prochaine_penalite = echeance.derniere_date_penalite + echeance.pret.modalite.duree()
            if echeance.derniere_date_penalite and today < prochaine_penalite:
                continue

            penalite, created = Penalite.objects.get_or_create(
                echeance=echeance,
                defaults={
                    "montant": echeance.calculer_penalite(),
                }
            )
            if created:
                print(f"Pénalité générée pour échéance {echeance.level} de {echeance.pret.numero}")




def generer_interets_epargnes():
    """
    Calcule et crédite les intérêts pour chaque épargne active.
    """
    print("Création des intérêts ...", datetime.now())
    today = date.today()
    epargnes = CompteEpargne.objects.filter(active=True)

    for epargne in epargnes:
        
        if epargne.derniere_date_interet and epargne.derniere_date_interet >= today:
            continue 
        
        periodicite = epargne.modalite.etiquette
        doit_crediter = False

        # ---- Conditions de déclenchement ----
        if periodicite == ModaliteEcheance.HEBDOMADAIRE and today.weekday() == 0:  # Lundi
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

        # ---- Calcul des intérêts ----
        if doit_crediter:
            interet = epargne.calculer_interet_prorata(today)
            if interet > 0:
                with transaction.atomic():
                    Interet.objects.create(
                        compte      = epargne,
                        montant     = interet,
                        description = f"Intérêt {epargne.modalite} de {epargne.taux}%",
                    )
                    print(f"Intérêt créé pour épargne {epargne.numero}")
