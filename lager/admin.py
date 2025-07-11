from django.contrib import admin
from .models import Sirovina, Recept
from meni.models import Stavka


@admin.register(Sirovina)
class SirovinaAdmin(admin.ModelAdmin):
    list_display = ['naziv', 'kolicina', 'jedinica_mjere']
    search_fields = ['naziv']


@admin.register(Recept)
class ReceptAdmin(admin.ModelAdmin):
    list_display = ['stavka', 'sirovina', 'kolicina']
    list_filter = ['stavka']
    autocomplete_fields = ['stavka', 'sirovina']
    search_fields = ['stavka__naziv', 'sirovina__naziv']
