from rest_framework import serializers
from .models import Narudzba

class NarudzbaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Narudzba
        fields = '__all__'
