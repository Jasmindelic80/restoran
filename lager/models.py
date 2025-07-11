from django.db import models
from meni.models import Stavka



class Sirovina(models.Model):
    naziv = models.CharField(max_length=100)
    jedinica_mjere = models.CharField(max_length=20)
    kolicina = models.FloatField()

    def __str__(self):
        return f"{self.naziv} ({self.kolicina} {self.jedinica_mjere})"

class Recept(models.Model):
    stavka = models.ForeignKey(Stavka, on_delete=models.CASCADE)
    sirovina = models.ForeignKey(Sirovina, on_delete=models.CASCADE)
    kolicina = models.FloatField(help_text="Količina sirovine po jednoj jedinici stavke")

    def __str__(self):
        return f"{self.stavka.naziv} - {self.kolicina} {self.sirovina.jedinica_mjere} {self.sirovina.naziv}"

