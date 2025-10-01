from django.urls import path
from . import views

app_name = 'TresorApp'

urlpatterns = [
    path('rapports/', views.rapports_view, name='rapports'),
]
