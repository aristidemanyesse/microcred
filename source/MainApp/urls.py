from django.urls import path
from . import views



urlpatterns = [
    path('', views.login_view, name='login'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('clients/', views.clients_view, name='clients'),
    path('client/', views.client_view, name='client'),
    path('credits/', views.credits_view, name='credits'),
    path('credit/', views.credit_view, name='credit'),
    path('epargne/', views.epargne_view, name='epargne'),
    path('rapports/', views.rapports_view, name='rapports'),
]
