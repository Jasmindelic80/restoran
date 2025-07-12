from django import forms
from meni.models import Stavka
from .models import Narudzba, StavkaNarudzbe

class NarudzbaForm(forms.ModelForm):
    class Meta:
        model = Narudzba
        fields = ['sto_broj']
        widgets = {
            'sto_broj': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),

        }

class StavkaNarudzbeForm(forms.ModelForm):
    class Meta:
        model = StavkaNarudzbe
        fields = ['stavka', 'kolicina']
        widgets = {
            'stavka': forms.Select(attrs={'class': 'form-control'}),
            'kolicina': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        }


StavkaNarudzbeFormSet = forms.inlineformset_factory(
    Narudzba,
    StavkaNarudzbe,
    form=StavkaNarudzbeForm,
    extra=3,
    can_delete=True
)
