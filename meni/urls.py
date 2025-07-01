from django.urls import path
from . import views

urlpatterns = [
    path('', views.meni_list, name='meni_list'),
    path('stavka/dodaj/', views.stavka_create, name='stavka_create'),
    path('stavka/<int:pk>/', views.stavka_detail, name='stavka_detail'),
    path('stavka/<int:pk>/izmijeni/', views.stavka_update, name='stavka_update'),  # ← OVO
    path('stavka/<int:pk>/obrisi/', views.stavka_delete, name='stavka_delete'),
]
