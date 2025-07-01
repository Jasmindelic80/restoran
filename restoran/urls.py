from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('korisnici/', include('korisnici.urls')),
    path('meni/', include('meni.urls')),
    path('narudzba/', include('narudzba.urls')),
    path('stolovi/', include('stolovi.urls')),
]
