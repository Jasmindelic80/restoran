from django.db import models

class Sto(models.Model):
    naziv = models.CharField(max_length=100)
    broj_mesta = models.IntegerField()

    def __str__(self):
        return f"{self.naziv} ({self.broj_mesta} mesta)"
