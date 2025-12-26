from rest_framework import serializers
from .models import Narudzba, StavkaNarudzbe
from meni.models import Stavka


class StavkaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stavka
        fields = ["id", "naziv", "cijena"]


class StavkaNarudzbeSerializer(serializers.ModelSerializer):
    stavka_naziv = serializers.CharField(source="stavka.naziv", read_only=True)
    stavka_cijena = serializers.DecimalField(
        source="stavka.cijena",
        max_digits=10,
        decimal_places=2,
        read_only=True
    )

    class Meta:
        model = StavkaNarudzbe
        fields = [
            "id",
            "narudzba",
            "stavka",
            "stavka_naziv",
            "stavka_cijena",
            "kolicina",
        ]


class NarudzbaSerializer(serializers.ModelSerializer):
    stavke = StavkaNarudzbeSerializer(many=True, read_only=True)
    status = serializers.CharField(required=False)  # ✅ omogućava PATCH sa samo status

    class Meta:
        model = Narudzba
        fields = ['id', 'konobar', 'sto_broj', 'datum', 'status', 'stavke']
