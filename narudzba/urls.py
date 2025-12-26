from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import NarudzbaViewSet, StavkaNarudzbeViewSet, StavkaViewSet
from django.urls import path, include
from . import views  # ovo je ključno


router = DefaultRouter()
router.register("narudzbe", NarudzbaViewSet)
router.register("stavke_narudzbe", StavkaNarudzbeViewSet)
router.register("stavke", StavkaViewSet)

urlpatterns = [
    # standardne Django views
    path('', views.narudzba_list, name='narudzba_list'),
    path('<int:pk>/', views.narudzba_detail, name='narudzba_detail'),
    path('nova/', views.narudzba_create, name='narudzba_create'),
    path('<int:pk>/izmeni/', views.narudzba_update, name='narudzba_update'),
    path('<int:pk>/obrisi/', views.narudzba_delete, name='narudzba_delete'),
    path('sank/', views.sank_view, name='sank'),
    path('narudzba/<int:pk>/izdaj_racun/', views.izdaj_racun, name='izdaj_racun'),
    path('api/narudzba/<int:pk>/izdaj_racun/', views.izdaj_racun, name='izdaj_racun'),


    # DRF API routes
    path("api/", include(router.urls)),
]



