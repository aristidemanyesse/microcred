from django.db import models
from django.contrib.auth.models import AbstractUser
from CoreApp.models import BaseModel

# Create your models here.

class Role(BaseModel):
    libelle = models.CharField(max_length=50)  # Agent, Superviseur agence, Admin


class Employe(AbstractUser, BaseModel):
    agence  = models.ForeignKey('MainApp.Agence', on_delete=models.CASCADE, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    contact = models.CharField(max_length = 255, null = True, blank=True)
    role    = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True)
    brut    = models.CharField(max_length=50, unique=True, null=True, blank=True)
    is_new  = models.BooleanField(default=True)

    
    def __str__(self):
        return self.get_full_name()
    
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def is_agent(self):
        return self.role.nom.lower() == 'agent'

    def is_superviseur_agence(self):
        return self.role.nom.lower() == 'superviseur agence'

    def is_admin(self):
        return self.role.nom.lower() == 'admin'
