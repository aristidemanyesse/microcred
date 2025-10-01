from django import forms
from FinanceApp.models import Garantie, Pret, CompteEpargne


class PretForm(forms.ModelForm):
    class Meta:
        model = Pret
        fields = "__all__"
        
        
class CompteEpargneForm(forms.ModelForm):
    class Meta:
        model = CompteEpargne
        fields = "__all__"



class GarantieForm(forms.ModelForm):
    class Meta:
        model = Garantie        
        fields = "__all__"
