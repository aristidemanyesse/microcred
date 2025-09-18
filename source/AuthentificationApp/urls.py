from django.urls import path

from . import views, views_ajax

app_name = 'AuthentificationApp'

urlpatterns = [
    path('', views.login_view, name='login'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('locked/', views.logout_view, name='logout'),
    
    path('login/ajax/', views_ajax.login_ajax, name='login_ajax'),
    path('first_user/ajax/', views_ajax.first_user, name='first_user'),
    
    
    path('users/', views.users_view, name='users'),
]
