from django.urls import path
from . import views

app_name = 'TresorApp'

urlpatterns = [
    path('compte/<uuid:pk>/', views.compte_view, name='compte'),
    path('compte/<uuid:pk>/releve/', views.releve_view, name='releve_compte'),
    path('rapports/<str:start>/<str:end>/', views.rapports_view, name='rapports_date'),
    path('rapports/', views.rapports_view, name='rapports'),
]
