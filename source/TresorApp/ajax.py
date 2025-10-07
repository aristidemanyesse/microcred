from django.db.models import Sum, DecimalField, Case, When, Value, IntegerField
from datetime import datetime, date, timedelta
from FinanceApp.models import  Transaction, TypeTransaction
from annoying.decorators import render_to
from datetime import datetime
from django.db.models.functions import TruncMonth, TruncDay
from dateutil.relativedelta import relativedelta
from django.http import JsonResponse



def stats_finance(request, start=None, end=None):
    start = request.session.get("start")
    end = request.session.get("end")
    
    if start and end:
        start = datetime.strptime(start, "%Y-%m-%d").date()
        end = datetime.strptime(end, "%Y-%m-%d").date()
    
    # Déterminer le type de découpage
    days_diff = (end - start).days

    if days_diff <= 31:
        # Découpage quotidien
        trunc_unit = TruncDay("created_at")
        date_format = "%Y-%m-%d"
        label_format = "%d %b %Y"
        nb_parts = days_diff + 1
        delta = timedelta(days=1)
    else:
        # Découpage mensuel
        trunc_unit = TruncMonth("created_at")
        date_format = "%Y-%m"
        label_format = "%b %Y"
        nb_parts = (end.year - start.year) * 12 + (end.month - start.month) + 1
        delta = relativedelta(months=1)
        

    # Récupération groupée
    qs = (Transaction.objects
        .filter(created_at__date__gte=start, created_at__date__lte=end)
        .annotate(period=trunc_unit)
        .values("period")
        .annotate(
            depots=Sum(
                Case(
                    When(type_transaction__etiquette=TypeTransaction.DEPOT, then="montant"),
                    default=0,
                    output_field=DecimalField(),
                )
            ),
            retraits=Sum(
                Case(
                    When(type_transaction__etiquette=TypeTransaction.RETRAIT, then="montant"),
                    default=0,
                    output_field=DecimalField(),
                )
            ),
            remboursements=Sum(
                Case(
                    When(type_transaction__etiquette=TypeTransaction.REMBOURSEMENT, then="montant"),
                    default=0,
                    output_field=DecimalField(),
                )
            ),
            depot_fidelis=Sum(
                Case(
                    When(type_transaction__etiquette=TypeTransaction.DEPOT_FIDELIS, then="montant"),
                    default=0,
                    output_field=DecimalField(),
                )
            ),
            retrait_fidelis=Sum(
                Case(
                    When(type_transaction__etiquette=TypeTransaction.RETRAIT_FIDELIS, then="montant"),
                    default=0,
                    output_field=DecimalField(),
                )
            ),
        )
        .order_by("period")
    )

    # Indexer les résultats par mois pour lookup rapide
    results_map = {row["period"].strftime(date_format): row for row in qs}

    # Calcul du nombre de mois dans l'intervalle
    nb_months = (end.year - start.year) * 12 + (end.month - start.month) + 1

    # Générer les mois de la période
    results = []
    current_date = start
    for _ in range(nb_parts):
        key = current_date.strftime(date_format)
        label = current_date.strftime(label_format)
        row = results_map.get(key)

        results.append({
            "mois": label,
            "depots": float(row["depots"] if row else 0),
            "retraits": float(row["retraits"] if row else 0),
            "remboursements": float(row["remboursements"] if row else 0),
            "depot_fidelis": float(row["depot_fidelis"] if row else 0),
            "retrait_fidelis": float(row["retrait_fidelis"] if row else 0),
        })
        current_date += delta
        

    return JsonResponse(results, safe=False)
