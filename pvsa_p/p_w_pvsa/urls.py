from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

from . import views

urlpatterns= [

    path("signin/", views.signin, name="signin"),
    path("logout/", views.signout, name="logout"),
    path("signup/", views.signup, name="signup"),


    path("sector/crear", views.crear_sector, name="crear_sector"),

    path("admin/", admin.site.urls),
    path("", views.home, name="home"),

    path("sectores/", views.lista_sectores, name="lista_sectores"),
    path("sectores/<int:sector_id>/", views.detalle_sector, name="detalle_sector"),

    path("ubicaciones/", views.lista_ubicaciones, name="lista_ubicaciones"),
    path("ubicaciones/<int:ubicacion_id>/", views.detalle_ubicacion, name="detalle_ubicacion"),

    path("pisos/<int:piso_id>/", views.detalle_piso, name="detalle_piso"),

   ## path("lugar/<int:lugar_id/", views.detalle_lugar, name="detalle_lugar"),

    path("detalle_lugar/", views.detalle_lugar, name="detalle_lugar"),

]