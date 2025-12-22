from django.db import models, transaction
from django.utils import timezone

    
class Sector(models.Model):
    sector = models.CharField(max_length=100)

    def __str__(self):
        return f"Sector: {self.sector}"
     
class Ubicacion(models.Model):
    ubicacion = models.CharField(max_length=100)
    sector = models.ForeignKey(Sector, verbose_name="Sector", on_delete=models.RESTRICT)

    def __str__(self):
        return f"Ubicación: {self.ubicacion}"
    
class Piso(models.Model):
    piso = models.SmallIntegerField()
    ubicacion = models.ForeignKey(Ubicacion, verbose_name="Ubicacion", on_delete=models.RESTRICT)

    def __str__(self):
        return f"Piso: {self.piso} | Ubicación: {self.ubicacion}"
    
    
class TipoLugar(models.Model):
    tipo_de_lugar = models.CharField(max_length=100)

    def __str__(self):
        return f"Tipo de lugar: {self.tipo_de_lugar}"

class Lugar(models.Model):
    nombre_del_lugar = models.CharField(max_length=100) #100 o 150?
    piso = models.ForeignKey(Piso, verbose_name="Piso", on_delete=models.RESTRICT)

    lugar_tipo_lugar = models.ForeignKey(TipoLugar, verbose_name="Tipo de lugar", on_delete=models.RESTRICT)

    def __str__(self):
        return f"Lugar: {self.nombre_del_lugar}"
    
class CategoriaObjeto(models.Model):
    nombre_de_la_categoria = models.CharField(max_length=50)

    def __str__(self):
        return f"Categoria: {self.nombre_de_la_categoria}"
    
class Objeto(models.Model):
    nombre_del_objeto = models.CharField(max_length=50)

    categoria = models.ForeignKey(CategoriaObjeto, verbose_name="Categoria del objeto", on_delete=models.RESTRICT)

    def __str__(self):
        return f"Objeto: {self.nombre_del_objeto}"

class TipoObjeto(models.Model):
    
    marca = models.CharField(max_length=50)
    material= models.CharField(max_length=60, blank=True)

    objeto= models.ForeignKey(Objeto, verbose_name="Objeto", on_delete=models.RESTRICT)

    def __str__(self):
        return f"Tipo de objeto: {self.objeto} | Marca: {self.marca} | Material: {self.material}"
    
class ObjetoLugar(models.Model):

    ESTADO = {
        "B": "Bueno",
        "P": "Pendiente",
        "M": "Malo"
    }
    cantidad = models.SmallIntegerField()
    estado = models.CharField(max_length=1, choices=ESTADO)
    detalle = models.CharField(max_length=200, blank=True)
    fecha = models.DateField(auto_now_add=True)

    lugar= models.ForeignKey(Lugar, verbose_name= "Lugar", on_delete=models.RESTRICT)
    tipo_de_objeto = models.ForeignKey(TipoObjeto, verbose_name="Tipo de objeto", on_delete=models.RESTRICT)

    def __str__(self):
        fecha = self.fecha.strftime("%d/%m/%Y") if self.fecha else ""
        return f"{self.lugar} | {self.tipo_de_objeto} | Cant: {self.cantidad} | Estado: {self.get_estado_display()} | {fecha}"
    
    def save(self, *args, **kwargs):
        if self.pk:
            anterior = ObjetoLugar.objects.get(pk=self.pk)
            cambio = (anterior.cantidad != self.cantidad or anterior.estado != self.estado or (anterior.detalle or "") != (self.detalle or ""))
            if cambio:
                with transaction.atomic():
                    HistoricoObjeto.objects.create(
                        objeto_del_lugar=self, cantidad_anterior = anterior.cantidad, estado_anterior = anterior.estado, fecha_anterior=anterior.fecha

                    )
                    return super().save(*args,**kwargs)
            
        return super().save(*args, **kwargs)
    
class HistoricoObjeto(models.Model):
    ESTADO = {
        "B": "Bueno",
        "P": "Pendiente",
        "M": "Malo"
    }
    cantidad_anterior =models.SmallIntegerField()
    estado_anterior = models.CharField(max_length=1, choices=ESTADO)
    detalle_anterior= models.CharField(max_length=200, blank=True)
    fecha_anterior = models.DateField()

    objeto_del_lugar = models.ForeignKey(ObjetoLugar, verbose_name="Objeto del lugar", on_delete=models.RESTRICT ,null=True, blank=True)

    def __str__(self):
        fecha = self.fecha_anterior.strftime("%d/%m/%Y") if self.fecha_anterior else ""
        obj = str(self.objeto_del_lugar) if self.objeto_del_lugar else "Sin objeto del lugar"
        det = f" | Det: {self.detalle_anterior}" if self.detalle_anterior else ""
        return f"Histórico de: {obj} | Cant ant: {self.cantidad_anterior} | Estado ant: {self.get_estado_anterior_display()} | Fecha: {fecha}{det}"