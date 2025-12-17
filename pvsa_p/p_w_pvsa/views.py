from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from .forms import CrearSector

from .models import Sector, Ubicacion, Piso, Lugar, TipoLugar, TipoObjeto, CategoriaObjeto, ObjetoLugar, Objeto, HistoricoObjeto

@login_required
def lista_sectores(request):
    sectores = Sector.objects.all().order_by("sector")
    return render(request, "sectores.html", {
        "sectores": sectores
    })
@login_required
def detalle_sector(request, sector_id):
    sector = get_object_or_404(Sector, pk=sector_id)
    ubicaciones = Ubicacion.objects.filter(sector=sector).order_by("ubicacion")
    return render(request, "detalle_sector.html", {
        "sector": sector,
        "ubicaciones": ubicaciones,
    })
@login_required
def lista_ubicaciones(request):
    ubicaciones = Ubicacion.objects.all().order_by("ubicacion")
    return render(request, "ubicaciones.html",{
        "ubicaciones": ubicaciones
    } )
@login_required
def detalle_ubicacion(request, ubicacion_id):
    ubicacion = get_object_or_404(Ubicacion, pk=ubicacion_id)
    pisos = Piso.objects.filter(ubicacion=ubicacion).order_by("piso")
    return render(request, "detalle_ubicacion.html", {
        "ubicacion": ubicacion,
        "pisos": pisos,
    })
@login_required
def detalle_piso(request, piso_id):
    piso = get_object_or_404(Piso, pk=piso_id)
    lugares = Lugar.objects.filter(piso=piso).order_by("nombre_del_lugar")
    return render(request, "detalle_piso.html", {
        "piso": piso,
        "lugares": lugares,
    })


@login_required
def detalle_lugar(request, lugar_id):
    lugar = get_object_or_404(Lugar, pk=lugar_id)
    objetos = ObjetoLugar.objects.filter(lugar=lugar).order_by("fecha")
    context={
        "lugar":lugar,
        "objetos": objetos,
    }
    return render(request, "detalle_lugar.html", context)



def home(request):
    return render(request, "home.html")

def signup(request):

    if request.method =="GET":
        return render(request, "signup.html", {
        "form": UserCreationForm
    })
    else:
        if request.POST['password1'] == request.POST['password2']:
            try:
                user = User.objects.create_user(username=request.POST['username'], password=request.POST['password1'])
                user.save()
                login(request, user)
                return redirect("home")
            except:
                return render(request, "signup.html", {
                    "form": UserCreationForm,
                    "error": "Usuario ya existe",})
        return render(request, "signup.html", {
                    "form": UserCreationForm,
                    "error": "Las contraseñas no coinciden",})
    

@login_required
def signout (request):
    logout(request)
    return redirect('home')


def signin(request):
    if request.method == "GET":
        return render(request, "signin.html", {
        'form': AuthenticationForm
    })
    else:
        user = authenticate(request,  username=request.POST['username'], password=request.POST['password'])
        if user is None:
            return render(request, "signin.html", {
            'form': AuthenticationForm,
            "error": "nombre o contraseña son incorrectas"})
        else:
            login(request, user)
            return redirect('detalle_lugar')


@login_required
def crear_sector(request):
    if request.method == "GET":
        return render(request, "crear_sector.html", {
        "form": CrearSector
    })
    else:
        try:
            form = CrearSector(request.POST)
            form.save()
            return redirect("home")
        except ValueError:
            return redirect("home", {
                "error": "se ingreso algo mal"
            })