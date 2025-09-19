
from django.shortcuts import redirect
from django.urls import path
from django.urls.conf import include

from . import views, ajax
# from . import ajax 

app_name = "CoreApp"
urlpatterns = [
    # path('dashboard/', views.dashboard, name="dashboard"),  
    # path('admin/dashboard/', views.dashboard_admin, name="dashboard_admin"),  
    # path('admin/finance/', views.finance, name="finance"),  
    # path('admin/finance/<str:start>/<str:end>/', views.finance, name="finance"),
    # path('admin/parametrage/', views.parametrage, name="parametrage_prix"),  
    # path('admin/parametrage/autres/', views.parametrage_autres, name="parametrage_autres"),  
    # path('admin/utilisateurs/', views.utilisateurs, name="utilisateurs"),
    
    path('core/ajax/save/', ajax.save, name="save"),
    path('core/ajax/mise_a_jour/', ajax.mise_a_jour, name="mise_a_jour"),
    path('core/ajax/supprimer/', ajax.supprimer, name="supprimer"),
    path('core/ajax/change_active/', ajax.change_active, name="change_active"),
    path('core/ajax/filter_date/', ajax.filter_date, name="filter_date"),
    path('core/ajax/session/', ajax.session, name="session"),
    path('core/ajax/delete_session/', ajax.delete_session, name="delete_session"),
    path('core/ajax/change_language/', ajax.change_language, name="change_language"),

]
