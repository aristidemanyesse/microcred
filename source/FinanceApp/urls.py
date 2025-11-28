from django.urls import path
from . import views, ajax

app_name = 'FinanceApp'

urlpatterns = [
    path('prets/', views.prets_view, name='prets'),
    path('prets/simulateur/', views.prets_simulateur_view, name='simulateur_pret'),
    path('prets/archivage/', views.archivage_prets, name='archivage_prets'),
    path('demandes/', views.demandes_view, name='demandes'),
    path('pret/<uuid:pk>/', views.pret_view, name='pret'),
    path('pret/<uuid:pk>/releve/', views.releve_pret, name='releve_pret'),
    
    path('echeances/', views.echeances_view, name='echeances'),
    path('transactions/invoice/<uuid:pk>/', views.invoice, name='invoice'),
 
    path('epargnes/', views.epargnes_view, name='epargnes'),
    path('epargnes/simulateur/', views.epargnes_simulateur_view, name='simulateur_epargne'),
    path('epargnes/archivage/', views.archivage_epargnes, name='archivage_epargnes'),
    path('epargne/<uuid:pk>/', views.epargne_view, name='epargne'),
    path('epargne/<uuid:pk>/releve/', views.releve_epargne, name='releve_epargne'),
    
    path('remboursement/', ajax.new_remboursement, name='new_remboursement'),
    path('confirm_pret/', ajax.confirm_pret, name='confirm_pret'),
    path('decline_pret/', ajax.decline_pret, name='decline_pret'),
    path('decaissement/', ajax.decaissement, name='decaissement'),
    path('new_depot/', ajax.new_depot, name='new_depot'),
    path('new_retrait/', ajax.new_retrait, name='new_retrait'),
    
    path('api/stats-finance/', ajax.stats_finance, name='stats_finance'),
]
