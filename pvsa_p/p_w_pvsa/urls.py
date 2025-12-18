from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

from . import views

urlpatterns= [

    path("signin/", views.signin, name="signin"),
    path("logout/", views.signout, name="logout"),
    path("signup/", views.signup, name="signup"),


    path("admin/", admin.site.urls),
    path("", views.home, name="home"),

    ## SECTORES 
    path("sectores/", views.lista_sectores, name="lista_sectores"),
    path("sectores/<int:sector_id>/", views.detalle_sector, name="detalle_sector"),
    path("sectores/<int:sector_id>/borrar/", views.borrar_sector, name="borrar_sector"),
    path("sector/crear/", views.crear_sector, name="crear_sector"),
    path("sectores/<int:sector_id>/editar/", views.editar_sector, name="editar_sector"),

    ## UBICACIONES
    path("ubicaciones/", views.lista_ubicaciones, name="lista_ubicaciones"),
    path("ubicaciones/<int:ubicacion_id>/", views.detalle_ubicacion, name="detalle_ubicacion"),
    path("ubicaciones/<int:ubicacion_id>/borrar", views.borrar_ubicacion, name="borrar_ubicacion"),
    path("ubicacion/crear/", views.crear_ubicacion, name="crear_ubicacion"),
    path("ubicaciones/<int:ubicacion_id>/editar/", views.editar_ubicacion, name="editar_ubicacion"),

    ## PISOS
    path("pisos/<int:piso_id>/", views.detalle_piso, name="detalle_piso"),
    path("pisos/<int:piso_id>/borrar", views.borrar_piso, name="borrar_piso"),
    path("piso/crear/", views.crear_piso, name="crear_piso"),
    path("pisos/", views.crear_piso, name="listar_piso"),
    path("pisos/<int:piso_id>/editar/", views.EditarPiso, name="editar_piso"),

    ## LUGAR
    path("lugar/<int:lugar_id>/", views.detalle_lugar, name="detalle_lugar"),
    path("lugar/<int:lugar_id>/borrar", views.borrar_lugar, name="borrar_lugar"),
    path("lugar/<int:lugar_id>/editar", views.editar_lugar, name="editar_lugar"),
    path("lugar/crear/", views.crear_lugar, name="crear_lugar"),
    path("lugares/", views.crear_lugar, name="listar_lugar"),

    ## OBJETO DEL LUGAR
    path("lugar/<int:lugar_id>/objeto/crear/", views.crear_objeto_lugar, name="crear_objeto_lugar"),
    path("lugar/<int:lugar_id>/objeto/crear/", views.crear_objeto_lugar, name="detalle_objeto_lugar"),
    path("lugar/objetos/", views.crear_objeto_lugar, name="listar_objeto_lugar"),
    path("lugar/<int:lugar_id>/objeto/editar/", views.editar_objeto_lugar, name="editar_objeto_lugar"),
    path("lugar/<int:lugar_id>/objeto/borrar/", views.borrar_objeto_lugar, name="borrar_objeto_lugar"),



    ## TIPO DEL LUGAR
    path("tipo-lugar/crear/", views.crear_tipo_lugar, name="crear_tipo_lugar"),
    path("", views.crear_tipo_lugar, name="detalle_tipo_lugar"),
    path("tipo-lugar/", views.crear_tipo_lugar, name="listar_tipo_lugar"),
    path("tipo-lugar/<int:tipo_lugar_id>/editar/", views.editar_tipo_lugar, name="editar_tipo_lugar"),
    path("tipo-lugar/<int:tipo_lugar_id>/borrar/", views.borrar_tipo_lugar, name="borrar_tipo_lugar"),


    ## CATEGORIA
    path("categoria/crear/", views.crear_categoria_objeto, name="crear_categoria_objeto"),
    path("categoria/crear/", views.crear_categoria_objeto, name="detalle_categoria_objeto"),
    path("categorias/", views.crear_categoria_objeto, name="listar_categoria_objeto"),
    path("categoria/<int:categoria_id>/editar/", views.editar_categoria, name="editar_categoria"),
    path("categoria/<int:categoria_id>/borrar/", views.borrar_categoria, name="borrar_categoria"),


    ## OBJETO
    path("objeto/crear/", views.crear_objeto, name="crear_objeto"),
    path("objeto/crear/", views.crear_objeto, name="detalle_objeto"),
    path("objetos/", views.crear_objeto, name="listar_objeto"),
    path("objeto/<int:objeto_id>/editar/", views.editar_objeto, name="editar_objeto"),
    path("objeto/<int:objeto_id>/borrar/", views.borrar_objeto, name="borrar_objeto"),



    ## TIPO DE OBJETO
    path("tipo-objeto/crear/", views.crear_tipo_objeto, name="crear_tipo_objeto"),
    path("tipo-objeto/crear/", views.crear_tipo_objeto, name="detalle_tipo_objeto"),
    path("tipo-objetos/", views.crear_tipo_objeto, name="listar_tipo_objeto"),
    path("tipo-objeto/<int:tipo_objetos_id>/editar/", views.editar_tipo_objeto, name="editar_tipo_objeto"),
    path("tipo-objeto/<int:tipo_objetos_id>/borrar/", views.borrar_tipo_objeto, name="borrar_tipo_objeto"),





    ## HISTORICO
    path("historicos/", views.borrar_lugar, name="listar_historico"),
    path("historico/<int:historico_id>/editar/", views.editar_historico, name="editar_historico"),
    path("historico/<int:historico_id>/borrar/", views.borrar_historico, name="borrar_historico"),


    
]