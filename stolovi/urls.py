from django.urls import path
from . import views

urlpatterns = [
    path('', views.stolovi_list, name='stolovi_list'),
    path('<int:pk>/', views.sto_detail, name='sto_detail'),
    path('novi/', views.sto_create, name='sto_create'),
    path('<int:pk>/izmeni/', views.sto_update, name='sto_update'),
    path('<int:pk>/obrisi/', views.sto_delete, name='sto_delete'),
]

