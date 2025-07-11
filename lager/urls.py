from django.urls import path
from . import views

urlpatterns = [
    path('', views.stanje_robe, name='stanje_robe'),
    path('edit/<int:pk>/', views.edit_sirovina, name='edit_sirovina'),
]
