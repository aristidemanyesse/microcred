from django import forms
from AuthentificationApp.models import Employe


class EmployeForm(forms.ModelForm):
    class Meta:
        model = Employe
        fields = "__all__"
        