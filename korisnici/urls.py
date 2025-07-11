from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('profil/', views.profil_view, name='profil'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('stanje-robe/', views.stanje_robe, name='stanje_robe'),
    path('izvjestaj/', views.izvjestaj, name='izvjestaj'),
    path('izvjestaj/stanje-robe/', views.izvjestaj_stanje_roba, name='izvjestaj_stanje_roba'),
    path('izvjestaj_stanje/', views.izvjestaj_stanje_roba, name='izvjestaj_stanje_roba'),
    path('narudzba/<int:narudzba_id>/potvrdi/', views.potvrdi_narudzbu, name='potvrdi_narudzbu'),
]
