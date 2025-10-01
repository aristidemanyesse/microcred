

from django import forms
from TresorApp.models import CompteAgence, Operation

class CompteAgenceForm(forms.ModelForm):
    class Meta:
        model = CompteAgence
        fields = "__all__"
        
        
class OperationForm(forms.ModelForm):
    class Meta:
        model = Operation
        fields = "__all__"