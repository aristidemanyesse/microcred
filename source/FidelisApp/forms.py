from django import forms
from .models import *


class CompteFidelisForm(forms.ModelForm):
    class Meta:
        model = CompteFidelis
        fields = "__all__"