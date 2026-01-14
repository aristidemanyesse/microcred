from django.contrib import admin

from FinanceApp.models import *

# Register your models here.

@admin.register(TypeTransaction)
class TypeTransactionAdmin(admin.ModelAdmin):
    list_display = ('libelle', 'etiquette')
    search_fields = ('libelle',)
    
@admin.register(StatusPret)
class StatusPretAdmin(admin.ModelAdmin):
    list_display = ('libelle', 'etiquette')
    search_fields = ('libelle',)
    

@admin.register(Penalite)
class PenaliteAdmin(admin.ModelAdmin):
    list_display = ('echeance', 'montant', 'description')
    search_fields = ('echeance__id', 'description')
    

@admin.register(CompteEpargne)
class CompteEpargneAdmin(admin.ModelAdmin):
    list_display = ('client', 'solde',)
    search_fields = ('client__id', 'client__nom', 'client__prenoms')


@admin.register(Interet)
class InteretAdmin(admin.ModelAdmin):
    list_display = ('compte', 'montant', 'description')
    search_fields = ('compte__id', 'description')

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('compte', 'type_transaction', 'montant', 'commentaire', 'created_at')
    search_fields = ('compte__id', 'type_transaction__libelle', 'commentaire')
    
@admin.register(ModaliteEcheance)
class ModaliteEcheanceAdmin(admin.ModelAdmin):  
    list_display = ('libelle', 'etiquette')
    search_fields = ('libelle',)
    
@admin.register(Pret)
class PretAdmin(admin.ModelAdmin):  
    list_display = ('numero', 'client', 'base', 'taux', 'montant', 'modalite', 'nombre_modalite', 'status', 'created_at')
    search_fields = ('client__id', 'client__nom', 'client__prenoms')
    list_filter = ('status', 'created_at')

@admin.register(Echeance)
class EcheanceAdmin(admin.ModelAdmin):
    list_display = ('pret', 'date_echeance', 'montant_a_payer', 'montant_paye', 'status')
    search_fields = ('pret__id', 'pret__client__id', 'pret__client__nom', 'pret__client__prenoms')
    list_filter = ('status',)

@admin.register(Garantie)
class GarantieAdmin(admin.ModelAdmin):
    list_display = ('pret', 'montant', 'temoin', 'contact', 'libelle') 
    

@admin.register(TypeAmortissement)
class TypeAmortissementAdmin(admin.ModelAdmin):
    list_display = ('libelle', 'etiquette')