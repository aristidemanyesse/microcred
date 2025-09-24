from django.urls import path
from . import views, ajax

app_name = 'FinanceApp'

urlpatterns = [
    path('prets/', views.prets_view, name='prets'),
    path('demandes/', views.demandes_view, name='demandes'),
    path('pret/<uuid:pk>/', views.pret_view, name='pret'),
    path('echeances/', views.echeances_view, name='echeances'),
 
    path('epargnes/', views.epargnes_view, name='epargnes'),
    path('epargne/<uuid:pk>/', views.epargne_view, name='epargne'),
    
    path('remboursement/', ajax.new_remboursement, name='new_remboursement'),
    path('confirm_pret/', ajax.confirm_pret, name='confirm_pret'),
    path('new_depot/', ajax.new_depot, name='new_depot'),
    path('new_retrait/', ajax.new_retrait, name='new_retrait'),
]
