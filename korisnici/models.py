from django.db import models
from django.contrib.auth.models import User

class Profil(models.Model):
    ULOGE = [
        ('sef', 'Šef'),
        ('konobar', 'Konobar'),
        ('sank', 'Šank'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    telefon = models.CharField(max_length=20, blank=True)
    adresa = models.TextField(blank=True)
    uloga = models.CharField(max_length=20, choices=ULOGE)

    def __str__(self):
        return f'{self.user.username} ({self.get_uloga_display()})'

    @property
    def prikaz_uloge(self):
        return self.get_uloga_display()

class Narudzba(models.Model):
    STATUSI = [
        ('kreirana', 'Kreirana'),
        ('na_sanku', 'Na šanku'),
        ('zavrsena', 'Završena'),
    ]

    konobar = models.ForeignKey(User, on_delete=models.CASCADE, related_name='narudzbe_konobar')
    sto_broj = models.PositiveIntegerField()
    napomena = models.TextField(blank=True)
    datum = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUSI, default='kreirana')

    def __str__(self):
        return f"Narudžba #{self.id} - sto {self.sto_broj}"

    @property
    def prikaz_statusa(self):
        return dict(self.STATUSI).get(self.status, self.status)
