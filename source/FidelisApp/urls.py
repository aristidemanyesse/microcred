from django.urls import path
from . import views, ajax

app_name = 'FidelisApp'

urlpatterns = [
    path('comptes/', views.comptes, name='comptes'),
    path('archivage/', views.archivage, name='archivage'),
    path('compte/<uuid:pk>/', views.compte_view, name='compte'),
    path('compte/<uuid:pk>/releve/', views.releve_view, name='releve_fidelis'),
    
    path('new_depot/', ajax.new_depot, name='new_depot'),
    path('new_retrait/', ajax.new_retrait, name='new_retrait'),
]
