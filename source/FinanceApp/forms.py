from django import forms
from FinanceApp.models import Pret, CompteEpargne


class PretForm(forms.ModelForm):
    class Meta:
        model = Pret
        fields = "__all__"
        
        
class CompteEpargneForm(forms.ModelForm):
    class Meta:
        model = CompteEpargne
        fields = "__all__"
        
