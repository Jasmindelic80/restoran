from django.db import models
from django.contrib.auth.models import User
from meni.models import Stavka


class Narudzba(models.Model):
    konobar = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    sto_broj = models.PositiveIntegerField()
    datum = models.DateTimeField(auto_now_add=True)

    STATUS_CHOICES = [
        ('u_pripremi', 'U pripremi'),
        ('spremna', 'Spremna za posluženje'),
        ('zavrsena', 'Završena'),
        ('placena', 'Plaćena'),
        ('ZATVORENA', 'Zatvorena'),
    ]

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='u_pripremi'
    )

    class Meta:
        ordering = ['-datum']

    def __str__(self):
        return f"Narudžba #{self.id} | Sto {self.sto_broj} | {self.get_status_display()}"


class StavkaNarudzbe(models.Model):
    narudzba = models.ForeignKey(
        Narudzba,
        related_name='stavke',
        on_delete=models.CASCADE
    )

    stavka = models.ForeignKey(
        Stavka,
        on_delete=models.CASCADE
    )

    kolicina = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.kolicina} x {self.stavka.naziv} (Narudžba #{self.narudzba.id})"
