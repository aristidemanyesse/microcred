from django.urls import path
from . import views

app_name = 'MainApp'

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('clients/', views.clients_view, name='clients'),
    path('client/<uuid:pk>/', views.client_view, name='client'),
    
    path('rapports/', views.rapports_view, name='rapports'),
]
