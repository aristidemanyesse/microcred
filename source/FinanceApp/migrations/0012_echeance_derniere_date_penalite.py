from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('FinanceApp', '0011_transaction_pret'),
    ]

    operations = [
        migrations.AddField(
            model_name='echeance',
            name='derniere_date_penalite',
            field=models.DateField(blank=True, null=True),
        ),
    ]
