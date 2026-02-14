from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Narudzba
from lager.models import Recept

@receiver(post_save, sender=Narudzba)
def skini_lager(sender, instance, created, **kwargs):
    if instance.status == 'zavrsena':
        for stavka_narudzbe in instance.stavke.all():
            recepti = Recept.objects.filter(stavka=stavka_narudzbe.stavka)

            for recept in recepti:
                sirovina = recept.sirovina
                potrosnja = recept.kolicina * stavka_narudzbe.kolicina

                sirovina.kolicina -= potrosnja
                sirovina.save()
