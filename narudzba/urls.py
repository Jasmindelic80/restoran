from django.urls import path
from . import views
from .views import sank_view

urlpatterns = [
    path('', views.narudzba_list, name='narudzba_list'),
    path('<int:pk>/', views.narudzba_detail, name='narudzba_detail'),
    path('nova/', views.narudzba_create, name='narudzba_create'),
    path('<int:pk>/izmeni/', views.narudzba_update, name='narudzba_update'),
    path('<int:pk>/obrisi/', views.narudzba_delete, name='narudzba_delete'),
    path('sank/', sank_view, name='sank'),
    path('narudzba/<int:pk>/izdaj_racun/', views.izdaj_racun, name='izdaj_racun'),
]


