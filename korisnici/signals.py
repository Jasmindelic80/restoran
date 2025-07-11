from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Profil

@receiver(post_save, sender=User)
def kreiraj_profil(sender, instance, created, **kwargs):
    if created:
        Profil.objects.create(user=instance, uloga='konobar')
