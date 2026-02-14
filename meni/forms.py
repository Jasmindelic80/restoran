from django import forms
from .models import Stavka

class StavkaForm(forms.ModelForm):
    class Meta:
        model = Stavka
        fields = ['naziv', 'opis', 'cijena', "kategorija"]
