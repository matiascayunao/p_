from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from .forms import CrearSector, CrearUbicacion, CrearPiso, CrearLugar, CrearObjetoLugar, CrearTipoLugar, CrearCategoriaObjeto, CrearObjeto, CrearTipoObjeto, CrearHistorico
from .forms import EditarSector, EditarUbicacion, EditarPiso, EditarTipoLugar, EditarLugar, EditarCategoria, EditarTipoObjeto, EditarObjeto, EditarObjetoLugar, EditarHistorico
from .models import Sector, Ubicacion, Piso, Lugar, TipoLugar, TipoObjeto, CategoriaObjeto, ObjetoLugar, Objeto, HistoricoObjeto

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
            return redirect('home')
        
@login_required
def signout (request):
    logout(request)
    return redirect('home')
        

@login_required
def home(request):
    return render(request, "home.html")
    


## Sectores
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
def crear_sector(request):
    if request.method == "GET":
        return render(request, "crear_sector.html", {
        "form": CrearSector()
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
        
@login_required  
def borrar_sector(request, sector_id):
    sector = get_object_or_404(Sector, pk=sector_id)
    if request.method == 'POST':
        sector.delete()
        return redirect("home")
    
@login_required
def editar_sector(request, sector_id):
    sector = get_object_or_404(Sector, pk=sector_id)
    if request.method =="GET":
        form = EditarSector(instance=sector)
        return render(request, "editar_sector.html",{
            "form": form,
            "sector": sector
        })
    form = EditarSector(request.POST, instance=sector)
    if form.is_valid():
            form.save()
            return redirect("sectores")
    return render(request, "editar_sector.html", {
        "form": form,
        "sector": sector
    })
## Ubicaciones

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
def crear_ubicacion(request):
    if request.method == "GET":
        return render(request, "crear_ubicacion.html", {
            "form": CrearUbicacion()
        })

    form = CrearUbicacion(request.POST)
    if form.is_valid():
        ubicacion = form.save()
        return redirect("home", sector_id=ubicacion.sector.id)

    return render(request, "crear_ubicacion.html", {
        "form": form
    })

@login_required  
def borrar_ubicacion(request, ubicacion_id):
    ubicacion = get_object_or_404(Ubicacion, pk=ubicacion_id)
    if request.method == 'POST':
        ubicacion.delete()
        return redirect("home")
    
@login_required
def editar_ubicacion(request, ubicacion_id):
    ubicacion = get_object_or_404(Ubicacion, pk=ubicacion_id)
    if request.method =="GET":
        form = EditarUbicacion(instance=ubicacion)
        return render(request, "editar_ubicacion.html",{
            "form": form,
            "ubicacion": ubicacion
        })
    form = EditarUbicacion(request.POST, instance=ubicacion)
    if form.is_valid():
            form.save()
            return redirect("lista_ubicaciones")
    return render(request, "editar_ubicacion.html", {
        "form": form,
        "ubicacion": ubicacion
    })

## Piso
@login_required
def detalle_piso(request, piso_id):
    piso = get_object_or_404(Piso, pk=piso_id)
    lugares = Lugar.objects.filter(piso=piso).order_by("nombre_del_lugar")
    return render(request, "detalle_piso.html", {
        "piso": piso,
        "lugares": lugares,
    })

@login_required
def crear_piso(request):
    if request.method == "GET":
        return render(request, "crear_piso.html", {
            "form": CrearPiso()
        })

    form = CrearPiso(request.POST)
    if form.is_valid():
        piso = form.save()
        return redirect("home", ubicacion_id=piso.ubicacion.id)

    return render(request, "crear_piso.html", {
        "form": form
    })
@login_required  
def borrar_piso(request, piso_id):
    piso = get_object_or_404(Piso, pk=piso_id)
    if request.method == 'POST':
        piso.delete()
        return redirect("home")
    

@login_required
def editar_piso(request, piso_id):
    piso = get_object_or_404(Piso, pk=piso_id)
    if request.method =="GET":
        form = EditarPiso(instance=piso)
        return render(request, "editar_piso.html",{
            "form": form,
            "piso": piso
        })
    form = EditarPiso(request.POST, instance=piso)
    if form.is_valid():
            form.save()
            return redirect("pisos")
    return render(request, "editar_piso.html", {
        "form": form,
        "piso": piso
    })
##Lugar


@login_required
def detalle_lugar(request, lugar_id):
    lugar = get_object_or_404(Lugar, pk=lugar_id)
    objetos = ObjetoLugar.objects.filter(lugar=lugar).order_by("fecha")
    context={
        "lugar":lugar,
        "objetos": objetos,
    }
    return render(request, "detalle_lugar.html", context)



@login_required
def crear_lugar(request):
    if request.method == "GET":
        return render(request, "crear_lugar.html", {
            "form": CrearLugar()
        })

    form = CrearLugar(request.POST)
    if form.is_valid():
        lugar = form.save()
        return redirect("home", piso_id=lugar.piso.id)

    return render(request, "crear_lugar.html", {
        "form": form
    })

@login_required  
def borrar_lugar(request, lugar_id):
    lugar = get_object_or_404(Lugar, pk=lugar_id)
    if request.method == 'POST':
        lugar.delete()
        return redirect("home")
    
@login_required
def editar_lugar(request, lugar_id):
    lugar = get_object_or_404(Lugar, pk=lugar_id)
    if request.method =="GET":
        form = EditarLugar(instance=lugar)
        return render(request, "editar_lugar.html",{
            "form": form,
            "lugar": lugar
        })
    form = EditarLugar(request.POST, instance=lugar)
    if form.is_valid():
            form.save()
            return redirect("lugares")
    return render(request, "editar_lugar.html", {
        "form": form,
        "lugar": lugar
    })



### Objeto del lugar
@login_required
def crear_objeto_lugar(request, lugar_id):
    lugar = get_object_or_404(Lugar, pk=lugar_id)

    if request.method == "GET":
        return render(request, "crear_objeto_lugar.html", {
            "form": CrearObjetoLugar(),
            "lugar": lugar
        })

    form = CrearObjetoLugar(request.POST)
    if form.is_valid():
        obj = form.save(commit=False)
        obj.lugar = lugar
        obj.save()
        return redirect("home", lugar_id=lugar.id)

    return render(request, "crear_objeto_lugar.html", {
        "form": form,
        "lugar": lugar
    })

@login_required
def editar_objeto_lugar(request, objeto_lugar_id):
    objeto_lugar = get_object_or_404(ObjetoLugar, pk=objeto_lugar_id)
    if request.method =="GET":
        form = EditarObjetoLugar(instance=objeto_lugar)
        return render(request, "editar_objeto_lugar.html",{
            "form": form,
            "objeto_lugar": objeto_lugar
        })
    form = EditarObjetoLugar(request.POST, instance=objeto_lugar)
    if form.is_valid():
            form.save()
            return redirect("objetos_del_lugar")
    return render(request, "editar_objeto_lugar.html", {
        "form": form,
        "objeto_lugar": objeto_lugar
    })

@login_required  
def borrar_objeto_lugar(request, objeto_lugar_id):
    objeto_lugar = get_object_or_404(ObjetoLugar, pk=objeto_lugar_id)
    if request.method == 'POST':
        objeto_lugar.delete()
        return redirect("home")

## Tipo de Lugar

@login_required
def crear_tipo_lugar(request):
    if request.method == "GET":
        return render(request, "crear_tipo_lugar.html", {"form": CrearTipoLugar()})

    form = CrearTipoLugar(request.POST)
    if form.is_valid():
        form.save()
        return redirect("home")

    return render(request, "crear_tipo_lugar.html", {"form": form})

@login_required
def editar_tipo_lugar(request, tipo_lugar_id):
    tipo_lugar = get_object_or_404(TipoLugar, pk=tipo_lugar_id)
    if request.method =="GET":
        form = EditarTipoLugar(instance=tipo_lugar)
        return render(request, "editar_tipo_lugar.html",{
            "form": form,
            "tipo_lugar": tipo_lugar
        })
    form = EditarTipoLugar(request.POST, instance=tipo_lugar)
    if form.is_valid():
            form.save()
            return redirect("tipos_de_lugares")
    return render(request, "editar_tipo_lugar.html", {
        "form": form,
        "tipo_lugar": tipo_lugar
    })


@login_required  
def borrar_tipo_lugar(request, tipo_lugar_id):
    tipo_lugar = get_object_or_404(TipoLugar, pk=tipo_lugar_id)
    if request.method == 'POST':
        tipo_lugar.delete()
        return redirect("home")
    

## Categoria 
@login_required
def crear_categoria_objeto(request):
    if request.method == "GET":
        return render(request, "crear_categoria_objeto.html", {"form": CrearCategoriaObjeto()})

    form = CrearCategoriaObjeto(request.POST)
    if form.is_valid():
        form.save()
        return redirect("home")

    return render(request, "crear_categoria_objeto.html", {"form": form})

@login_required
def editar_categoria(request, categoria_id):
    categoria = get_object_or_404(CategoriaObjeto, pk=categoria_id)
    if request.method =="GET":
        form = EditarCategoria(instance=categoria)
        return render(request, "editar_categoria.html",{
            "form": form,
            "categoria": categoria
        })
    form = EditarCategoria(request.POST, instance=categoria)
    if form.is_valid():
            form.save()
            return redirect("categorias")
    return render(request, "editar_categoria.html", {
        "form": form,
        "categoria": categoria
    })

@login_required  
def borrar_categoria(request, categoria_id):
    categoria = get_object_or_404(CategoriaObjeto, pk=categoria_id)
    if request.method == 'POST':
        categoria.delete()
        return redirect("home")

## Objeto

@login_required
def crear_objeto(request):
    if request.method == "GET":
        return render(request, "crear_objeto.html", {"form": CrearObjeto()})

    form = CrearObjeto(request.POST)
    if form.is_valid():
        form.save()
        return redirect("home")

    return render(request, "crear_objeto.html", {"form": form})

@login_required
def editar_objeto(request, objeto_id):
    objeto = get_object_or_404(Objeto, pk=objeto_id)
    if request.method =="GET":
        form = EditarObjeto(instance=objeto)
        return render(request, "editar_objeto.html",{
            "form": form,
            "objeto": objeto
        })
    form = EditarObjeto(request.POST, instance=objeto)
    if form.is_valid():
            form.save()
            return redirect("objetos")
    return render(request, "editar_objeto.html", {
        "form": form,
        "objeto": objeto
    })

@login_required  
def borrar_objeto(request, objeto_id):
    objeto = get_object_or_404(Objeto, pk=objeto_id)
    if request.method == 'POST':
        objeto.delete()
        return redirect("home")


## Tipo de objeto


@login_required
def crear_tipo_objeto(request):
    if request.method == "GET":
        return render(request, "crear_tipo_objeto.html", {"form": CrearTipoObjeto()})

    form = CrearTipoObjeto(request.POST)
    if form.is_valid():
        form.save()
        return redirect("home")

    return render(request, "crear_tipo_objeto.html", {"form": form})


@login_required
def editar_tipo_objeto(request, tipo_objeto_id):
    tipo_objeto = get_object_or_404(TipoObjeto, pk=tipo_objeto_id)
    if request.method =="GET":
        form = EditarTipoObjeto(instance=tipo_objeto)
        return render(request, "editar_tipo_objeto.html",{
            "form": form,
            "tipo_objeto": tipo_objeto
        })
    form = EditarTipoObjeto(request.POST, instance=tipo_objeto)
    if form.is_valid():
            form.save()
            return redirect("tipos_de_objetos")
    return render(request, "editar_tipo_objeto.html", {
        "form": form,
        "tipo_objeto": tipo_objeto
    })

@login_required  
def borrar_tipo_objeto(request, tipo_objeto_id):
    tipo_objeto = get_object_or_404(TipoObjeto, pk=tipo_objeto_id)
    if request.method == 'POST':
        tipo_objeto.delete()
        return redirect("home")

## Historico

@login_required
def crear_historico(request, historico_id):
    historico = get_object_or_404(HistoricoObjeto, pk=historico_id)

    if request.method == "GET":
        return render(request, "crear_historico.html", {
            "form": CrearHistorico(),
            "lugar": historico
        })

    form = CrearHistorico(request.POST)
    if form.is_valid():
        his = form.save(commit=False)
        his.lugar = historico
        his.save()
        return redirect("home", historico_id=historico.id)

    return render(request, "crear_historico.html", {
        "form": form,
        "lugar": historico
    })

@login_required
def editar_historico(request, historico_id):
    historico = get_object_or_404(HistoricoObjeto, pk=historico_id)
    if request.method =="GET":
        form = EditarHistorico(instance=historico)
        return render(request, "editar_historico.html",{
            "form": form,
            "historico": historico
        })
    form = EditarHistorico(request.POST, instance=historico)
    if form.is_valid():
            form.save()
            return redirect("historicos")
    return render(request, "editar_historico.html", {
        "form": form,
        "historico": historico
    })

@login_required  
def borrar_historico(request, historico_id):
    historico = get_object_or_404(HistoricoObjeto, pk=historico_id)
    if request.method == 'POST':
        historico.delete()
        return redirect("home")