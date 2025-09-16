from django.urls import path
from . import views

app_name = 'AuthentificationApp'

urlpatterns = [
    path('', views.login_view, name='login'),
    path('login/', views.login_view, name='login'),
    
    
    path('users/', views.users_view, name='users'),
]
