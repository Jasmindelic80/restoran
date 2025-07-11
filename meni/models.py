from django.db import models

class Stavka(models.Model):
    naziv = models.CharField(max_length=100)

    opis = models.TextField(blank=True, null=True)
    cijena = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return self.naziv

class Stavka(models.Model):
    KATEGORIJE = [

        ('toplo', 'Topli napici'),
        ('sokovi', 'Sokovi'),
        ('pivo', 'Pivo'),
        ('zestoka', 'Zestoka pica'),
        ('vino', 'Vino'),
        ('kokteli', 'Kokteli'),
    ]

    naziv = models.CharField(max_length=100)
    opis = models.TextField(blank=True, null=True)
    cijena = models.DecimalField(max_digits=8, decimal_places=2)
    kategorija = models.CharField(max_length=20, choices=KATEGORIJE, default='ostalo')

    def __str__(self):
        return self.naziv
