from django.urls import path
 
from . import views
 
urlpatterns = [
    path("equipo/<uuid:equipo_id>/", views.equipo_publico, name="equipo_publico"),
    path("equipo/<uuid:equipo_id>/qr.png", views.equipo_qr_imagen, name="equipo_qr_imagen"),
    path("equipo/<uuid:equipo_id>/etiqueta/", views.equipo_etiqueta, name="equipo_etiqueta"),
]
 