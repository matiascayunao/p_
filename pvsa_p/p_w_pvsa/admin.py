from django.contrib import admin
import nested_admin
from .models import Ubicacion, TipoLugar, TipoObjeto, Lugar, Objeto, ObjetoLugar, CategoriaObjeto,HistoricoObjeto, Sector



class SectorInline(nested_admin.NestedStackedInline):
    model = Sector
    extra = 0
class UbicacionInline(nested_admin.NestedStackedInline):
    model = Ubicacion
    extra = 0
    inlines = [SectorInline]
class TipoLugarInline(nested_admin.NestedStackedInline):
    model = TipoLugar
    extra = 0
    inline=[UbicacionInline]
class LugarInline(nested_admin.NestedStackedInline):
    model = Lugar
    extra = 0
    inline = [TipoLugarInline]

class CategoriaInline(nested_admin.NestedStackedInline):
    model = CategoriaObjeto
    extra = 0
class ObjetoInline(nested_admin.NestedStackedInline):
    model = Objeto
    extra = 0
    inline=[CategoriaInline]
class TipoObjetoInline(nested_admin.NestedStackedInline):
    model = TipoObjeto
    extra = 0
    inline=[ObjetoInline]

class ObjetoLugarInline(nested_admin.NestedStackedInline):
    model = ObjetoLugar
    extra = 0
    inline = [LugarInline, TipoObjetoInline]

class HistoricoObjetoInline(nested_admin.NestedStackedInline):
    model = HistoricoObjeto
    inline=[ObjetoInline]

class StoreAdmin(nested_admin.NestedModelAdmin):
    inlines=[]
    



admin.site.register(Ubicacion)
admin.site.register(Sector)
admin.site.register(TipoLugar)
admin.site.register(Lugar)

admin.site.register(CategoriaObjeto)
admin.site.register(Objeto)
admin.site.register(TipoObjeto)
admin.site.register(ObjetoLugar)
admin.site.register(HistoricoObjeto)
