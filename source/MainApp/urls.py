from django.urls import path
from . import views

app_name = 'MainApp'

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('clients/', views.clients_view, name='clients'),
    path('client/', views.client_view, name='client'),
    
    path('prets/', views.prets_view, name='prets'),
    path('demandes/', views.demandes_view, name='demandes'),
    path('pret/', views.pret_view, name='pret'),
    path('echeances/', views.echeances_view, name='echeances'),
    path('penalites/', views.penalites_view, name='penalites'),
    
    path('epargnes/', views.epargnes_view, name='epargnes'),
    path('epargne/', views.epargne_view, name='epargne'),
    
    path('rapports/', views.rapports_view, name='rapports'),
]
