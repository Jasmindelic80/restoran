from django.contrib import admin
from django.urls import path, include

from rest_framework.authtoken import views as drf_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('korisnici/', include('korisnici.urls')),
    path('meni/', include('meni.urls')),
    path('narudzba/', include('narudzba.urls')),
    path('stolovi/', include('stolovi.urls')),
    path('lager/', include('lager.urls')),
    path('', include('narudzba.urls')),

    # Ispravno definiranje token endpointa:
    path('api/auth/token/', drf_views.obtain_auth_token, name='api_token_auth'),
]