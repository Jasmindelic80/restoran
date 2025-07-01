from django import forms
from .models import Sto

class StoForm(forms.ModelForm):
    class Meta:
        model = Sto
        fields = ['naziv', 'broj_mesta']
