from django.contrib import admin

from FinanceApp.models import *

# Register your models here.

@admin.register(TypeTransaction)
class TypeTransactionAdmin(admin.ModelAdmin):
    list_display = ('libelle', 'etiquette')
    search_fields = ('libelle',)
    
@admin.register(StatutPret)
class StatutPretAdmin(admin.ModelAdmin):
    list_display = ('libelle', 'etiquette')
    search_fields = ('libelle',)
    

@admin.register(Penalite)
class PenaliteAdmin(admin.ModelAdmin):
    list_display = ('echeance', 'montant', 'date_application', 'description')
    search_fields = ('echeance__id', 'description')
    

@admin.register(CompteEpargne)
class CompteEpargneAdmin(admin.ModelAdmin):
    list_display = ('client', 'solde', 'date_creation')
    search_fields = ('client__id', 'client__nom', 'client__prenoms')
    

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('compte', 'type_transaction', 'montant', 'date_transaction', 'commentaire')
    search_fields = ('compte__id', 'type_transaction__libelle', 'commentaire')
    
    
@admin.register(Pret)
class PretAdmin(admin.ModelAdmin):  
    list_display = ('client', 'montant', 'taux_interet', 'date_debut', 'duree_mois', 'montant_rembourse', 'statut')
    search_fields = ('client__id', 'client__nom', 'client__prenoms')
    list_filter = ('statut',)
    
@admin.register(Echeance)
class EcheanceAdmin(admin.ModelAdmin):
    list_display = ('pret', 'date_echeance', 'montant_a_payer', 'montant_paye', 'statut')
    search_fields = ('pret__id', 'pret__client__id', 'pret__client__nom', 'pret__client__prenoms')
    list_filter = ('statut',)
    

