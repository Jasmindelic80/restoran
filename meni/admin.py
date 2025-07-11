from django.contrib import admin
from .models import Stavka


@admin.register(Stavka)
class StavkaAdmin(admin.ModelAdmin):
    search_fields = ('naziv', 'kategorija', 'cijena')
    list_filter = ('kategorija',)