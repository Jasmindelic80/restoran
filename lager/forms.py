from django import forms
from .models import Sirovina

class SirovinaForm(forms.ModelForm):
    class Meta:
        model = Sirovina
        fields = ['naziv', 'kolicina', "jedinica_mjere"]
