from django.db import models
from meni.models import Stavka  # moraš imati app 'meni' i model 'Stavka'

class Narudzba(models.Model):
    datum = models.DateTimeField(auto_now_add=True)
    stavke = models.ManyToManyField(Stavka, related_name='narudzbe')

    def __str__(self):
        return f"Narudžba #{self.id} - {self.datum.strftime('%d.%m.%Y %H:%M')}"
