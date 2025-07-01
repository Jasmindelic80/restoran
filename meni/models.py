from django.db import models

class Stavka(models.Model):
    naziv = models.CharField(max_length=100)
    opis = models.TextField(blank=True, null=True)
    cijena = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return self.naziv
