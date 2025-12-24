from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.db import transaction
from django.http import HttpResponse
from .excel_utils import build_excel_sectores
from django.db.models import Sum, Q

from .forms import (
    CrearSector, CrearUbicacion, CrearPiso, CrearLugar,
    CrearObjetoLugar, CrearTipoLugar, CrearCategoriaObjeto,
    CrearObjeto, CrearTipoObjeto, CrearHistorico,
    EditarSector, EditarUbicacion, EditarPiso, EditarLugar,
    EditarTipoLugar, EditarCategoria, EditarObjeto,
    EditarTipoObjeto, EditarObjetoLugar, EditarHistorico,
    BaseEstructuraForm, ObjetoLugarFilaFormSet,
)

from .models import (
    Sector, Ubicacion, Piso, Lugar, TipoLugar,
    CategoriaObjeto, Objeto, TipoObjeto,
    ObjetoLugar, HistoricoObjeto,
)

# -------------------
# AUTH
# -------------------   

@login_required
def descargar_excel_sectores(request):
    ubicaciones = (Ubicacion.objects.select_related("sector").order_by("sector__sector","ubicacion"))
    xlsx_bytes = build_excel_sectores(ubicaciones)

    response = HttpResponse(xlsx_bytes, content_type="application/vnd.openxmlformats-officedocument.""spreadsheetml.sheet")
    response["Content-Disposition"]= 'attachment; filename= "SECTORES.xlsx"'
    return response

@login_required
@transaction.atomic
def crear_estructura(request):
    if request.method == "POST":
        base_form = BaseEstructuraForm(request.POST)
        objetos_formset = ObjetoLugarFilaFormSet(request.POST, prefix="obj")

        if base_form.is_valid() and objetos_formset.is_valid():
            cd = base_form.cleaned_data

            sector_nombre = cd["sector"].strip()
            ubicacion_nombre = cd["ubicacion"].strip()
            piso_num = cd["piso"]
            nombre_lugar = cd["nombre_del_lugar"].strip()

            # Tipo de lugar: existente o nuevo
            tipo_lugar = cd.get("tipo_lugar_existente")
            if not tipo_lugar:
                tipo_lugar, _ = TipoLugar.objects.get_or_create(
                    tipo_de_lugar=cd["nuevo_tipo_lugar"].strip()
                )

            sector, _ = Sector.objects.get_or_create(sector=sector_nombre)
            ubicacion, _ = Ubicacion.objects.get_or_create(
                ubicacion=ubicacion_nombre,
                sector=sector,
            )
            piso, _ = Piso.objects.get_or_create(
                piso=piso_num,
                ubicacion=ubicacion,
            )

            lugar = Lugar.objects.create(
                nombre_del_lugar=nombre_lugar,
                piso=piso,
                lugar_tipo_lugar=tipo_lugar,
            )

            # ---- filas de objetos ----
            for f in objetos_formset:
                if not f.cleaned_data:
                    continue

                row = f.cleaned_data

                # Si está completamente vacía, la saltamos
                if not any(
                    row.get(k)
                    for k in [
                        "tipo_de_objeto", "cantidad", "estado", "detalle",
                        "nueva_categoria", "nuevo_objeto", "marca", "material",
                    ]
                ):
                    continue

                tipo_obj = row.get("tipo_de_objeto")
                cantidad = row.get("cantidad") or 1
                estado = row.get("estado") or "B"
                detalle = row.get("detalle") or ""

                nueva_categoria = (row.get("nueva_categoria") or "").strip()
                nuevo_objeto = (row.get("nuevo_objeto") or "").strip()
                marca = (row.get("marca") or "").strip()
                material = (row.get("material") or "").strip()

                # Si NO se seleccionó un tipo de objeto existente,
                # intentamos crear categoría / objeto / tipo_objeto
                if not tipo_obj:
                    if not nuevo_objeto:
                        # No hay tipo existente ni nombre nuevo -> ignoramos fila
                        continue

                    # Categoría
                    if nueva_categoria:
                        categoria, _ = CategoriaObjeto.objects.get_or_create(
                            nombre_de_la_categoria=nueva_categoria
                        )
                    else:
                        categoria, _ = CategoriaObjeto.objects.get_or_create(
                            nombre_de_la_categoria="Sin categoría"
                        )

                    # Objeto
                    objeto, _ = Objeto.objects.get_or_create(
                        nombre_del_objeto=nuevo_objeto,
                        categoria=categoria,
                    )

                    # Tipo de objeto
                    tipo_obj, _ = TipoObjeto.objects.get_or_create(
                        objeto=objeto,
                        marca=marca or "",
                        material=material or "",
                    )

                # Finalmente creamos el ObjetoLugar
                ObjetoLugar.objects.create(
                    lugar=lugar,
                    tipo_de_objeto=tipo_obj,
                    cantidad=cantidad,
                    estado=estado,
                    detalle=detalle,
                )

            return redirect("detalle_lugar", lugar_id=lugar.id)

    else:
        base_form = BaseEstructuraForm()
        objetos_formset = ObjetoLugarFilaFormSet(prefix="obj")

    return render(
        request,
        "crear_estructura.html",
        {"base_form": base_form, "objetos_formset": objetos_formset},
    )


def signup(request):
    if request.method == "GET":
        return render(request, "signup.html", {"form": UserCreationForm})
    if request.POST["password1"] != request.POST["password2"]:
        return render(
            request,
            "signup.html",
            {"form": UserCreationForm, "error": "Las contraseñas no coinciden"},
        )

    try:
        user = User.objects.create_user(
            username=request.POST["username"],
            password=request.POST["password1"],
        )
        user.save()
        login(request, user)
        return redirect("home")
    except Exception:
        return render(
            request,
            "signup.html",
            {"form": UserCreationForm, "error": "Usuario ya existe"},
        )


def signin(request):
    if request.method == "GET":
        return render(request, "signin.html", {"form": AuthenticationForm})

    user = authenticate(
        request,
        username=request.POST["username"],
        password=request.POST["password"],
    )
    if user is None:
        return render(
            request,
            "signin.html",
            {
                "form": AuthenticationForm,
                "error": "Nombre o contraseña incorrectos",
            },
        )

    login(request, user)
    return redirect("home")


@login_required
def signout(request):
    logout(request)
    return redirect("signin")


@login_required
def home(request):
    return render(request, "home.html")


# -------------------
# UTIL: DELETE CONFIRM
# -------------------

def _confirm_delete(request, obj, cancel_url_name, cancel_kwargs, success_url_name):
    if request.method == "POST":
        obj.delete()
        return redirect(success_url_name)

    cancel_url = reverse(cancel_url_name, kwargs=cancel_kwargs)
    return render(request, "confirm_delete.html", {"obj": obj, "cancel_url": cancel_url})


# -------------------
# SECTOR
# -------------------

@login_required
def lista_sectores(request):
    sectores = Sector.objects.all().order_by("sector")
    return render(request, "sector/sectores.html", {"sectores": sectores})


@login_required
def detalle_sector(request, sector_id):
    sector = get_object_or_404(Sector, pk=sector_id)
    ubicaciones = Ubicacion.objects.filter(sector=sector).order_by("ubicacion")
    return render(
        request,
        "sector/detalle_sector.html",
        {"sector": sector, "ubicaciones": ubicaciones},
    )


@login_required
def crear_sector(request):
    if request.method == "GET":
        return render(request, "sector/crear_sector.html", {"form": CrearSector()})
    form = CrearSector(request.POST)
    if form.is_valid():
        form.save()
        return redirect("lista_sectores")
    return render(request, "sector/crear_sector.html", {"form": form})


@login_required
def editar_sector(request, sector_id):
    sector = get_object_or_404(Sector, pk=sector_id)
    if request.method == "GET":
        return render(
            request,
            "sector/editar_sector.html",
            {"form": EditarSector(instance=sector), "sector": sector},
        )

    form = EditarSector(request.POST, instance=sector)
    if form.is_valid():
        form.save()
        return redirect("detalle_sector", sector_id=sector.id)
    return render(
        request,
        "sector/editar_sector.html",
        {"form": form, "sector": sector},
    )


@login_required
def borrar_sector(request, sector_id):
    sector = get_object_or_404(Sector, pk=sector_id)
    return _confirm_delete(
        request, sector, "detalle_sector", {"sector_id": sector.id}, "lista_sectores"
    )


# -------------------
# UBICACION
# -------------------

@login_required
def lista_ubicaciones(request):
    ubicaciones = Ubicacion.objects.select_related("sector").all().order_by("ubicacion")
    return render(request, "ubicacion/ubicaciones.html", {"ubicaciones": ubicaciones})


@login_required
def detalle_ubicacion(request, ubicacion_id):
    ubicacion = get_object_or_404(Ubicacion, pk=ubicacion_id)
    pisos = Piso.objects.filter(ubicacion=ubicacion).order_by("piso")
    return render(
        request,
        "ubicacion/detalle_ubicacion.html",
        {"ubicacion": ubicacion, "pisos": pisos},
    )


@login_required
def crear_ubicacion(request):
    if request.method == "GET":
        return render(request, "ubicacion/crear_ubicacion.html", {"form": CrearUbicacion()})
    form = CrearUbicacion(request.POST)
    if form.is_valid():
        ubicacion = form.save()
        return redirect("detalle_sector", sector_id=ubicacion.sector_id)
    return render(request, "ubicacion/crear_ubicacion.html", {"form": form})


@login_required
def editar_ubicacion(request, ubicacion_id):
    ubicacion = get_object_or_404(Ubicacion, pk=ubicacion_id)
    if request.method == "GET":
        return render(
            request,
            "ubicacion/editar_ubicacion.html",
            {"form": EditarUbicacion(instance=ubicacion), "ubicacion": ubicacion},
        )

    form = EditarUbicacion(request.POST, instance=ubicacion)
    if form.is_valid():
        form.save()
        return redirect("detalle_ubicacion", ubicacion_id=ubicacion.id)
    return render(
        request,
        "ubicacion/editar_ubicacion.html",
        {"form": form, "ubicacion": ubicacion},
    )


@login_required
def borrar_ubicacion(request, ubicacion_id):
    ubicacion = get_object_or_404(Ubicacion, pk=ubicacion_id)
    return _confirm_delete(
        request,
        ubicacion,
        "detalle_ubicacion",
        {"ubicacion_id": ubicacion.id},
        "lista_ubicaciones",
    )


# -------------------
# PISO
# -------------------

@login_required
def lista_pisos(request):
    pisos = (
        Piso.objects.select_related("ubicacion", "ubicacion__sector")
        .all()
        .order_by("ubicacion__ubicacion", "piso")
    )
    return render(request, "piso/pisos.html", {"pisos": pisos})


@login_required
def detalle_piso(request, piso_id):
    piso = get_object_or_404(Piso, pk=piso_id)
    lugares = Lugar.objects.filter(piso=piso).order_by("nombre_del_lugar")
    return render(
        request,
        "piso/detalle_piso.html",
        {"piso": piso, "lugares": lugares},
    )


@login_required
def crear_piso(request):
    if request.method == "GET":
        return render(request, "piso/crear_piso.html", {"form": CrearPiso()})
    form = CrearPiso(request.POST)
    if form.is_valid():
        piso = form.save()
        return redirect("detalle_ubicacion", ubicacion_id=piso.ubicacion_id)
    return render(request, "piso/crear_piso.html", {"form": form})


@login_required
def editar_piso(request, piso_id):
    piso = get_object_or_404(Piso, pk=piso_id)
    cancel_url = reverse("detalle_piso", kwargs={"piso_id": piso.id})

    if request.method == "GET":
        return render(
            request,
            "editar_generico.html",
            {
                "titulo": "Editar piso",
                "form": EditarPiso(instance=piso),
                "cancel_url": cancel_url,
            },
        )

    form = EditarPiso(request.POST, instance=piso)
    if form.is_valid():
        form.save()
        return redirect("detalle_piso", piso_id=piso.id)

    return render(
        request,
        "editar_generico.html",
        {
            "titulo": "Editar piso",
            "form": form,
            "cancel_url": cancel_url,
        },
    )


@login_required
def borrar_piso(request, piso_id):
    piso = get_object_or_404(Piso, pk=piso_id)
    return _confirm_delete(
        request, piso, "detalle_piso", {"piso_id": piso.id}, "lista_pisos"
    )


# -------------------
# LUGAR
# -------------------

@login_required
def lista_lugares(request):
    lugares = (
        Lugar.objects.select_related(
            "piso", "piso__ubicacion", "piso__ubicacion__sector", "lugar_tipo_lugar"
        )
        .all()
        .order_by("nombre_del_lugar")
    )
    return render(request, "lugar/lugares.html", {"lugares": lugares})


@login_required
def detalle_lugar(request, lugar_id):
    lugar = get_object_or_404(Lugar, pk=lugar_id)
    objetos = (
        ObjetoLugar.objects.select_related("tipo_de_objeto", "tipo_de_objeto__objeto")
        .filter(lugar=lugar)
        .order_by("-fecha")
    )
    return render(
        request,
        "lugar/detalle_lugar.html",
        {"lugar": lugar, "objetos": objetos},
    )


@login_required
def crear_lugar(request):
    if request.method == "GET":
        return render(request, "lugar/crear_lugar.html", {"form": CrearLugar()})
    form = CrearLugar(request.POST)
    if form.is_valid():
        lugar = form.save()
        return redirect("detalle_piso", piso_id=lugar.piso_id)
    return render(request, "lugar/crear_lugar.html", {"form": form})


@login_required
def editar_lugar(request, lugar_id):
    lugar = get_object_or_404(Lugar, pk=lugar_id)
    cancel_url = reverse("detalle_lugar", kwargs={"lugar_id": lugar.id})

    if request.method == "GET":
        return render(
            request,
            "editar_generico.html",
            {
                "titulo": "Editar lugar",
                "form": EditarLugar(instance=lugar),
                "cancel_url": cancel_url,
            },
        )

    form = EditarLugar(request.POST, instance=lugar)
    if form.is_valid():
        form.save()
        return redirect("detalle_lugar", lugar_id=lugar.id)

    return render(
        request,
        "editar_generico.html",
        {
            "titulo": "Editar lugar",
            "form": form,
            "cancel_url": cancel_url,
        },
    )


@login_required
def borrar_lugar(request, lugar_id):
    lugar = get_object_or_404(Lugar, pk=lugar_id)
    return _confirm_delete(
        request, lugar, "detalle_lugar", {"lugar_id": lugar.id}, "lista_lugares"
    )


# -------------------
# OBJETO DEL LUGAR
# -------------------

@login_required
def lista_objetos_lugar(request):
    objetos = (
        ObjetoLugar.objects
        .select_related("lugar", "tipo_de_objeto", "tipo_de_objeto__objeto")
        .all()
        .order_by("-fecha")
    )
    return render(request, "objeto_lugar/objetos_lugar.html", {"objetos": objetos})


@login_required
def detalle_objeto_lugar(request, objeto_lugar_id):
    obj = get_object_or_404(ObjetoLugar, pk=objeto_lugar_id)
    historicos = (
        HistoricoObjeto.objects
        .filter(objeto_del_lugar=obj)
        .order_by("-fecha_anterior")
    )
    return render(
        request,
        "objeto_lugar/detalle_objeto_lugar.html",
        {"objeto_lugar": obj, "historicos": historicos},
    )


@login_required
def crear_objeto_lugar(request, lugar_id):
    lugar = get_object_or_404(Lugar, pk=lugar_id)

    if request.method == "GET":
        return render(
            request,
            "objeto_lugar/crear_objeto_lugar.html",
            {"form": CrearObjetoLugar(), "lugar": lugar},
        )

    form = CrearObjetoLugar(request.POST)
    if form.is_valid():
        obj = form.save(commit=False)
        obj.lugar = lugar
        obj.save()
        return redirect("detalle_lugar", lugar_id=lugar.id)

    return render(
        request,
        "objeto_lugar/crear_objeto_lugar.html",
        {"form": form, "lugar": lugar},
    )


@login_required
def editar_objeto_lugar(request, objeto_lugar_id):
    objeto_lugar = get_object_or_404(ObjetoLugar, pk=objeto_lugar_id)
    cancel_url = reverse(
        "detalle_objeto_lugar",
        kwargs={"objeto_lugar_id": objeto_lugar.id},
    )

    if request.method == "GET":
        return render(
            request,
            "editar_generico.html",
            {
                "titulo": "Editar objeto del lugar",
                "form": EditarObjetoLugar(instance=objeto_lugar),
                "cancel_url": cancel_url,
            },
        )

    form = EditarObjetoLugar(request.POST, instance=objeto_lugar)
    if form.is_valid():
        form.save()
        return redirect("detalle_objeto_lugar", objeto_lugar_id=objeto_lugar.id)

    return render(
        request,
        "editar_generico.html",
        {
            "titulo": "Editar objeto del lugar",
            "form": form,
            "cancel_url": cancel_url,
        },
    )


@login_required
def borrar_objeto_lugar(request, objeto_lugar_id):
    obj = get_object_or_404(ObjetoLugar, pk=objeto_lugar_id)
    return _confirm_delete(
        request,
        obj,
        "detalle_lugar",
        {"lugar_id": obj.lugar_id},
        "lista_objetos_lugar",
    )

# -------------------
# TIPO LUGAR
# -------------------

@login_required
def lista_tipos_lugar(request):
    tipos = TipoLugar.objects.all().order_by("tipo_de_lugar")
    return render(request, "tipo_lugar/tipos_lugar.html", {"tipos": tipos})


@login_required
def detalle_tipo_lugar(request, tipo_lugar_id):
    tipo = get_object_or_404(TipoLugar, pk=tipo_lugar_id)
    lugares = Lugar.objects.filter(lugar_tipo_lugar=tipo).order_by("nombre_del_lugar")
    return render(
        request,
        "tipo_lugar/detalle_tipo_lugar.html",
        {"tipo": tipo, "lugares": lugares},
    )


@login_required
def crear_tipo_lugar(request):
    if request.method == "GET":
        return render(request, "tipo_lugar/crear_tipo_lugar.html", {"form": CrearTipoLugar()})
    form = CrearTipoLugar(request.POST)
    if form.is_valid():
        form.save()
        return redirect("lista_tipos_lugar")
    return render(request, "tipo_lugar/crear_tipo_lugar.html", {"form": form})


@login_required
def editar_tipo_lugar(request, tipo_lugar_id):
    tipo = get_object_or_404(TipoLugar, pk=tipo_lugar_id)
    cancel_url = reverse("detalle_tipo_lugar", kwargs={"tipo_lugar_id": tipo.id})

    if request.method == "GET":
        return render(
            request,
            "editar_generico.html",
            {
                "titulo": "Editar tipo de lugar",
                "form": EditarTipoLugar(instance=tipo),
                "cancel_url": cancel_url,
            },
        )

    form = EditarTipoLugar(request.POST, instance=tipo)
    if form.is_valid():
        form.save()
        return redirect("detalle_tipo_lugar", tipo_lugar_id=tipo.id)

    return render(
        request,
        "editar_generico.html",
        {
            "titulo": "Editar tipo de lugar",
            "form": form,
            "cancel_url": cancel_url,
        },
    )


@login_required
def borrar_tipo_lugar(request, tipo_lugar_id):
    tipo = get_object_or_404(TipoLugar, pk=tipo_lugar_id)
    return _confirm_delete(
        request,
        tipo,
        "detalle_tipo_lugar",
        {"tipo_lugar_id": tipo.id},
        "lista_tipos_lugar",
    )


# -------------------
# CATEGORIA / OBJETO / TIPO OBJETO
# -------------------

@login_required
def lista_categorias(request):
    categorias = CategoriaObjeto.objects.all().order_by("nombre_de_categoria")
    return render(request, "categoria/categorias.html", {"categorias": categorias})


@login_required
def detalle_categoria(request, categoria_id):
    categoria = get_object_or_404(CategoriaObjeto, pk=categoria_id)
    objetos = Objeto.objects.filter(objeto_categoria_id=categoria_id).order_by("nombre_del_objeto")
    return render(
        request,
        "categoria/detalle_categoria.html",
        {"categoria": categoria, "objetos": objetos},
    )


@login_required
def crear_categoria_objeto(request):
    if request.method == "GET":
        return render(
            request,
            "categoria/crear_categoria_objeto.html",
            {"form": CrearCategoriaObjeto()},
        )
    form = CrearCategoriaObjeto(request.POST)
    if form.is_valid():
        form.save()
        return redirect("lista_categorias")
    return render(request, "categoria/crear_categoria_objeto.html", {"form": form})


@login_required
def editar_categoria(request, categoria_id):
    categoria = get_object_or_404(CategoriaObjeto, pk=categoria_id)
    cancel_url = reverse("detalle_categoria", kwargs={"categoria_id": categoria.id})

    if request.method == "GET":
        return render(
            request,
            "editar_generico.html",
            {
                "titulo": "Editar categoría",
                "form": EditarCategoria(instance=categoria),
                "cancel_url": cancel_url,
            },
        )

    form = EditarCategoria(request.POST, instance=categoria)
    if form.is_valid():
        form.save()
        return redirect("detalle_categoria", categoria_id=categoria.id)

    return render(
        request,
        "editar_generico.html",
        {
            "titulo": "Editar categoría",
            "form": form,
            "cancel_url": cancel_url,
        },
    )


@login_required
def borrar_categoria(request, categoria_id):
    categoria = get_object_or_404(CategoriaObjeto, pk=categoria_id)
    return _confirm_delete(
        request,
        categoria,
        "detalle_categoria",
        {"categoria_id": categoria.id},
        "lista_categorias",
    )


@login_required
def lista_objetos(request):
    objetos = Objeto.objects.select_related("objeto_categoria").all().order_by(
        "nombre_del_objeto"
    )
    return render(request, "objeto/objetos.html", {"objetos": objetos})


@login_required
def detalle_objeto(request, objeto_id):
    objeto = get_object_or_404(Objeto, pk=objeto_id)
    tipos = TipoObjeto.objects.filter(objeto=objeto).order_by("marca", "material")
    return render(
        request,
        "objeto/detalle_objeto.html",
        {"objeto": objeto, "tipos": tipos},
    )


@login_required
def crear_objeto(request):
    if request.method == "GET":
        return render(request, "objeto/crear_objeto.html", {"form": CrearObjeto()})
    form = CrearObjeto(request.POST)
    if form.is_valid():
        form.save()
        return redirect("lista_objetos")
    return render(request, "objeto/crear_objeto.html", {"form": form})


@login_required
def editar_objeto(request, objeto_id):
    objeto = get_object_or_404(Objeto, pk=objeto_id)
    cancel_url = reverse("detalle_objeto", kwargs={"objeto_id": objeto.id})

    if request.method == "GET":
        return render(
            request,
            "editar_generico.html",
            {
                "titulo": "Editar objeto",
                "form": EditarObjeto(instance=objeto),
                "cancel_url": cancel_url,
            },
        )

    form = EditarObjeto(request.POST, instance=objeto)
    if form.is_valid():
        form.save()
        return redirect("detalle_objeto", objeto_id=objeto.id)

    return render(
        request,
        "editar_generico.html",
        {
            "titulo": "Editar objeto",
            "form": form,
            "cancel_url": cancel_url,
        },
    )


@login_required
def borrar_objeto(request, objeto_id):
    objeto = get_object_or_404(Objeto, pk=objeto_id)
    return _confirm_delete(
        request,
        objeto,
        "detalle_objeto",
        {"objeto_id": objeto.id},
        "lista_objetos",
    )


@login_required
def lista_tipos_objeto(request):
    tipos = (
        TipoObjeto.objects.select_related("objeto", "objeto__objeto_categoria")
        .all()
        .order_by("objeto__nombre_del_objeto", "marca")
    )
    return render(request, "tipo_objeto/tipos_objeto.html", {"tipos": tipos})


@login_required
def detalle_tipo_objeto(request, tipo_objeto_id):
    tipo = get_object_or_404(TipoObjeto, pk=tipo_objeto_id)
    usados = (
        ObjetoLugar.objects.filter(tipo_de_objeto=tipo)
        .select_related("lugar")
        .order_by("-fecha")
    )
    return render(
        request,
        "tipo_objeto/detalle_tipo_objeto.html",
        {"tipo": tipo, "usados": usados},
    )


@login_required
def crear_tipo_objeto(request):
    if request.method == "GET":
        return render(request, "tipo_objeto/crear_tipo_objeto.html", {"form": CrearTipoObjeto()})
    form = CrearTipoObjeto(request.POST)
    if form.is_valid():
        form.save()
        return redirect("lista_tipos_objeto")
    return render(request, "tipo_objeto/crear_tipo_objeto.html", {"form": form})


@login_required
def editar_tipo_objeto(request, tipo_objeto_id):
    tipo = get_object_or_404(TipoObjeto, pk=tipo_objeto_id)
    cancel_url = reverse("detalle_tipo_objeto", kwargs={"tipo_objeto_id": tipo.id})

    if request.method == "GET":
        return render(
            request,
            "editar_generico.html",
            {
                "titulo": "Editar tipo de objeto",
                "form": EditarTipoObjeto(instance=tipo),
                "cancel_url": cancel_url,
            },
        )

    form = EditarTipoObjeto(request.POST, instance=tipo)
    if form.is_valid():
        form.save()
        return redirect("detalle_tipo_objeto", tipo_objeto_id=tipo.id)

    return render(
        request,
        "editar_generico.html",
        {
            "titulo": "Editar tipo de objeto",
            "form": form,
            "cancel_url": cancel_url,
        },
    )


@login_required
def borrar_tipo_objeto(request, tipo_objeto_id):
    tipo = get_object_or_404(TipoObjeto, pk=tipo_objeto_id)
    return _confirm_delete(
        request,
        tipo,
        "detalle_tipo_objeto",
        {"tipo_objeto_id": tipo.id},
        "lista_tipos_objeto",
    )


# -------------------
# HISTORICO
# -------------------

@login_required
def lista_historicos(request):
    historicos = (
        HistoricoObjeto.objects.select_related(
            "objeto_del_lugar",
            "objeto_del_lugar__lugar",
            "objeto_del_lugar__tipo_de_objeto",
            "objeto_del_lugar__tipo_de_objeto__objeto",
        )
        .all()
        .order_by("-fecha_anterior")
    )
    return render(request, "historico/historicos.html", {"historicos": historicos})


@login_required
def detalle_historico(request, historico_id):
    historico = get_object_or_404(HistoricoObjeto, pk=historico_id)
    return render(request, "historico/detalle_historico.html", {"historico": historico})


@login_required
def crear_historico(request, objeto_lugar_id):
    objeto_lugar = get_object_or_404(ObjetoLugar, pk=objeto_lugar_id)

    if request.method == "GET":
        form = CrearHistorico(
            initial={
                "cantidad_anterior": objeto_lugar.cantidad,
                "estado_anterior": objeto_lugar.estado,
                "detalle_anterior": objeto_lugar.detalle,
                "fecha_anterior": objeto_lugar.fecha,
                "objeto_del_lugar": objeto_lugar.id,
            }
        )
        return render(
            request,
            "historico/crear_historico.html",
            {"form": form, "objeto_lugar": objeto_lugar},
        )

    form = CrearHistorico(request.POST)
    if form.is_valid():
        h = form.save(commit=False)
        h.objeto_del_lugar = objeto_lugar
        h.save()
        return redirect("detalle_objeto_lugar", objeto_lugar_id=objeto_lugar.id)

    return render(
        request,
        "historico/crear_historico.html",
        {"form": form, "objeto_lugar": objeto_lugar},
    )


@login_required
def editar_historico(request, historico_id):
    historico = get_object_or_404(HistoricoObjeto, pk=historico_id)
    cancel_url = reverse("detalle_historico", kwargs={"historico_id": historico.id})

    if request.method == "GET":
        return render(
            request,
            "editar_generico.html",
            {
                "titulo": "Editar histórico",
                "form": EditarHistorico(instance=historico),
                "cancel_url": cancel_url,
            },
        )

    form = EditarHistorico(request.POST, instance=historico)
    if form.is_valid():
        form.save()
        return redirect("detalle_historico", historico_id=historico.id)

    return render(
        request,
        "editar_generico.html",
        {
            "titulo": "Editar histórico",
            "form": form,
            "cancel_url": cancel_url,
        },
    )


@login_required
def borrar_historico(request, historico_id):
    historico = get_object_or_404(HistoricoObjeto, pk=historico_id)
    return _confirm_delete(
        request,
        historico,
        "detalle_historico",
        {"historico_id": historico.id},
        "lista_historicos",
    )


# -------------------
# RESUMEN
# -------------------

def _add_percentages(rows):
    for r in rows:
        total = r.get("total") or 0
        b = r.get("buenas") or 0
        p = r.get("pendientes") or 0
        m = r.get("malas") or 0

        if total ==0:
            r["pct_buenas"] = r["pct_pendientes"] = r["pct_malas"] = 0
        else:
            r["pct_buenas"] = round(b * 100 / total, 1)
            r["pct_pendientes"] = round(p * 100 / total, 1)
            r["pct_malas"] = round(m * 100 / total, 1)
    return rows

def resumen_general(request):

    qs_sector = (ObjetoLugar.objects.values("lugar__piso__ubicacion__sector__id","lugar__piso__ubicacion__sector__sector")
                 .annotate(total=Sum("cantidad"),buenas=Sum("cantidad",filter=Q(estado="B")), pendientes=Sum("cantidad", filter=Q(estado = "P")),
                           malas=Sum("cantidad", filter=Q(estado = "M")),).order_by("lugar__piso__ubicacion__sector__sector"))
    resumen_sector = list(qs_sector)
    _add_percentages(resumen_sector)

    qs_ubic = (ObjetoLugar.objects.values("lugar__piso__ubicacion__id","lugar__piso__ubicacion__ubicacion","lugar__piso__ubicacion__sector__sector")
                 .annotate(total=Sum("cantidad"),buenas=Sum("cantidad",filter=Q(estado="B")), pendientes=Sum("cantidad", filter=Q(estado = "P")),
                           malas=Sum("cantidad", filter=Q(estado = "M")),).order_by("lugar__piso__ubicacion__sector__sector","lugar__piso__ubicacion__ubicacion"))
    resumen_ubic = list(qs_ubic)
    _add_percentages(resumen_ubic)

    qs_obj = (ObjetoLugar.objects.values("tipo_de_objeto__objeto__id","tipo_de_objeto__objeto__nombre_del_objeto",)
                 .annotate(total=Sum("cantidad"),buenas=Sum("cantidad",filter=Q(estado="B")), pendientes=Sum("cantidad", filter=Q(estado = "P")),
                           malas=Sum("cantidad", filter=Q(estado = "M")),).order_by("tipo_de_objeto__objeto__nombre_del_objeto"))
    resumen_obj = list(qs_obj)
    _add_percentages(resumen_obj)

    malos_qs = (ObjetoLugar.objects.filter(estado="M").select_related("lugar__piso__ubicacion__sector", "lugar__piso__ubicacion", "lugar__piso","lugar","tipo_de_objeto__objeto")
                .order_by("tipo_de_objeto__objeto__nombre_del_objeto", "lugar__piso__ubicacion__sector__sector", "lugar__piso__ubicacion__ubicacion", "lugar__piso__piso", "lugar__nombre_del_lugar",))
    malos_por_objeto = {}
    for ol in malos_qs:
        oid = ol.tipo_de_objeto.objeto_id
        malos_por_objeto.setdefault(oid,[]).append(ol)

    resumen_objetos=[]
    for r in resumen_obj:
        oid = r["tipo_de_objeto__objeto__id"]
        resumen_objetos.append(
            {
                "id": oid,
                "nombre":r["tipo_de_objeto__objeto__nombre_del_objeto"],
                "total": r["total"] or 0,
                "buenas":r["buenas"] or 0,
                "pendientes": r["pendientes"] or 0,
                "malas": r["malas"] or 0,
                "pct_buenas": r["pct_buenas"],
                "pct_pendientes":r["pct_pendientes"],
                "pct_malas":r["pct_malas"],
                "malos": malos_por_objeto.get(oid, []),

            }
        )
        contexto = {
            "resumen_sector": resumen_sector,
            "resumen_ubic":resumen_ubic,
            "resumen_objetos":resumen_objetos,
        }
    return render(request, "resumen/resumen_general.html", contexto)