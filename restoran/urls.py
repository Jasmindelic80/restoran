from django.contrib import admin
from django.urls import path, include
from rest_framework.authtoken import views as drf_views

urlpatterns = [
    path('admin/', admin.site.urls),

    # aplikacije
    path('korisnici/', include('korisnici.urls')),
    path('meni/', include('meni.urls')),
    path('narudzbe/', include('narudzba.urls')),   # <- množina, čisto
    path('stolovi/', include('stolovi.urls')),
    path('lager/', include('lager.urls')),

    # početna stranica = lista narudžbi
    path('', include('narudzba.urls')),

    # API
    path('api/', include('narudzba.api_urls')),
    path('api/auth/token/', drf_views.obtain_auth_token, name='api_token_auth'),
]
