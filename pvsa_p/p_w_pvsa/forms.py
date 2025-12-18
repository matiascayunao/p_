from django.forms import ModelForm
from .models import Sector, Ubicacion, Piso, Lugar, TipoLugar, TipoObjeto, CategoriaObjeto, ObjetoLugar, Objeto, HistoricoObjeto

class CrearSector(ModelForm):
    class Meta:
        model = Sector
        fields = ['sector']

class CrearUbicacion(ModelForm):
    class Meta:
        model = Ubicacion
        fields = ["ubicacion", "sector"]

class CrearPiso(ModelForm):
    class Meta:
        model = Piso
        fields = ["piso", "ubicacion"]

class CrearLugar(ModelForm):
    class Meta:
        model = Lugar
        fields = ["nombre_del_lugar", "piso", "lugar_tipo_lugar"]

class CrearObjetoLugar(ModelForm):
    class Meta:
        model = ObjetoLugar
        fields = ["tipo_de_objeto", "cantidad", "estado", "detalle"]

class CrearTipoLugar(ModelForm):
    class Meta:
        model = TipoLugar
        fields = ["tipo_de_lugar"]

class CrearCategoriaObjeto(ModelForm):
    class Meta:
        model = CategoriaObjeto
        fields = ["nombre_de_la_categoria"]


class CrearObjeto(ModelForm):
    class Meta:
        model = Objeto
        fields = ["nombre_del_objeto", "categoria"]

class CrearTipoObjeto(ModelForm):
    class Meta:
        model = TipoObjeto
        fields = ["objeto", "marca", "material"]

class CrearHistorico(ModelForm):
    class Meta:
        model = HistoricoObjeto
        fields = ["objeto_del_lugar","cantidad_anterior","estado_anterior","detalle_anterior","fecha_anterior"]

## EDITAR


class EditarSector(ModelForm):
    class Meta:
        model = Sector
        fields = ["sector"]

class EditarUbicacion(ModelForm):
    class Meta:
        model = Ubicacion
        fields = ["ubicacion"]

class EditarPiso(ModelForm):
    class Meta:
        model = Piso
        fields = ["piso"]

class EditarTipoLugar(ModelForm):
    class Meta:
        model = TipoLugar
        fields = ["tipo_de_lugar"]

class EditarLugar(ModelForm):
    class Meta:
        model = Lugar
        fields = ["nombre_del_lugar", "piso", "lugar_tipo_lugar"]
        
class EditarCategoria(ModelForm):
    class Meta:
        model = CategoriaObjeto
        fields = ["nombre_de_la_categoria"]

class EditarObjeto(ModelForm):
    class Meta:
        model = Objeto
        fields = ["nombre_del_objeto", "categoria"]

class EditarTipoObjeto(ModelForm):
    class Meta:
        model = TipoObjeto
        fields = ["objeto", "marca", "material"]

class EditarObjetoLugar(ModelForm):
    class Meta:
        model = ObjetoLugar
        fields = ["tipo_de_objeto", "cantidad", "estado", "detalle"]

class EditarHistorico(ModelForm):
    class Meta:
        model = HistoricoObjeto
        fields = ["objeto_del_lugar","cantidad_anterior","estado_anterior","detalle_anterior","fecha_anterior"]


        