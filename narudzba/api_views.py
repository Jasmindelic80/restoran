from rest_framework import viewsets, permissions
from .models import Narudzba, StavkaNarudzbe
from meni.models import Stavka
from .serializers import (
    NarudzbaSerializer,
    StavkaNarudzbeSerializer,
    StavkaSerializer,
)
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

class StavkaNarudzbeViewSet(viewsets.ModelViewSet):
    serializer_class = StavkaNarudzbeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        narudzba_id = self.request.query_params.get('narudzba')
        if narudzba_id:
            return StavkaNarudzbe.objects.filter(narudzba_id=narudzba_id)
        return StavkaNarudzbe.objects.none()  # ne vraća ništa ako nema parametra


class NarudzbaViewSet(viewsets.ModelViewSet):
    queryset = Narudzba.objects.all()
    serializer_class = NarudzbaSerializer
    permission_classes = [permissions.IsAuthenticated]



class StavkaNarudzbeViewSet(viewsets.ModelViewSet):
    queryset = StavkaNarudzbe.objects.all()
    serializer_class = StavkaNarudzbeSerializer
    permission_classes = [permissions.IsAuthenticated]


class StavkaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Stavka.objects.all()
    serializer_class = StavkaSerializer
    permission_classes = [permissions.IsAuthenticated]

