from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

from . import views

urlpatterns= [

    path("login/", auth_views.LoginView.as_view(template_name= "p_w_pvsa/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("signup", views.signup, name="signup"),




    path("admin/", admin.site.urls),
    path("", views.home, name="home"),

    path("sectores/", views.lista_sectores, name="lista_sectores"),
    path("sectores/<int:sector_id>/", views.detalle_sector, name="detalle_sector"),
    
    path("ubicaciones/<int:ubicacion_id>/", views.detalle_ubicacion, name="detalle_ubicacion"),

    path("pisos/<int:piso_id>/", views.detalle_piso, name="detalle_piso"),

    path("lugar/<int:lugar_id/", views.detalle_lugar, name="detalle_lugar"),

]