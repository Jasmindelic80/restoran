from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import NarudzbaViewSet, StavkaNarudzbeViewSet, StavkaViewSet

router = DefaultRouter()
router.register("narudzbe", NarudzbaViewSet)
router.register("stavke_narudzbe", StavkaNarudzbeViewSet)
router.register("stavke", StavkaViewSet)

urlpatterns = [
    # UI
    path('', views.narudzba_list, name='narudzba_list'),
    path('nova/', views.narudzba_create, name='narudzba_create'),
    path('sank/', views.sank_view, name='sank'),

    path('<int:pk>/izdaj_racun/', views.izdaj_racun, name='izdaj_racun'),

    path('<int:pk>/', views.narudzba_detail, name='narudzba_detail'),
    path('<int:pk>/izmeni/', views.narudzba_update, name='narudzba_update'),
    path('<int:pk>/obrisi/', views.narudzba_delete, name='narudzba_delete'),
    path('izvjestaj/graf/', views.promet_graf, name='promet_graf'),

    # API
    path('api/', include(router.urls)),
]
