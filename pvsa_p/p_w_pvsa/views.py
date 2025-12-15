from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.forms import UserCreationForm

from .models import Sector, Ubicacion, Piso, Lugar, TipoLugar, TipoObjeto, CategoriaObjeto, ObjetoLugar, Objeto, HistoricoObjeto

def home(request):
    return render(request, "p_w_pvsa/home.html")

def lista_sectores(request):
    sectores = Sector.objects.all().order_by("sector")
    context={
        "sectores": sectores,
    }
    return render(request, "sectores.html", context)

def detalle_sector(request, sector_id):
    sector = get_object_or_404(Sector, pk=sector_id)
    ubicaciones = Ubicacion.objects.filter(sector=sector).order_by("Ubicacion")
    context={
        "sector": sector,
        "ubicaciones": ubicaciones,
    }
    return render(request, "detalle_sector.html", context)

def detalle_ubicacion(request, ubicacion_id):
    ubicacion = get_object_or_404(Ubicacion, pk=ubicacion_id)
    pisos = Piso.objects.filter(ubicacion=ubicacion).order_by("Pisos")
    context= {
        "ubicacion": ubicacion,
        "pisos": pisos,
    }
    return render(request, "detalle_ubicacion.html", context)

def detalle_piso(request, piso_id):
    piso = get_object_or_404(Piso, pk=piso_id)
    lugares = Lugar.objects.filter(piso=piso).order_by("Lugares")
    context={
        "piso":piso,
        "lugares": lugares,
    }
    return render(request, "detalle_piso.html", context)

def detalle_lugar(request, lugar_id):
    lugar = get_object_or_404(Lugar, pk=lugar_id)
    objetos = ObjetoLugar.objects.filter(lugar=lugar).order_by("objetos")
    context={
        "lugar":lugar,
        "objetos": objetos,
    }
    return render(request, "detalle_lugar.html", context)


def signup(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("login")
    else:
        form = UserCreationForm()
    return render(request, "accounts/signup.html", {"form": form})