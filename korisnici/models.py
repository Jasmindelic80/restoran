
from django.db import models
from django.contrib.auth.models import User

class Profil(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    telefon = models.CharField(max_length=20, blank=True)
    adresa = models.TextField(blank=True)

    def __str__(self):
        return f'Profil korisnika: {self.user.username}'
