from django.contrib import admin
from .models import Narudzba, StavkaNarudzbe


@admin.register(Narudzba)
class NarudzbaAdmin(admin.ModelAdmin):
    list_display = ("id", "sto_broj", "status", "datum")


@admin.register(StavkaNarudzbe)
class StavkaNarudzbeAdmin(admin.ModelAdmin):
    list_display = ("id", "narudzba", "stavka", "kolicina")
