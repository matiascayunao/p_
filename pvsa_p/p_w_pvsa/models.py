from django.db import models

    
class Sector(models.Model):
    sector = models.CharField(max_length=100)

    def __str__(self):
        return self.sector
     
class Ubicacion(models.Model):
    ubicacion = models.CharField(max_length=100)
    sector = models.ForeignKey(Sector, verbose_name="Sector", on_delete=models.RESTRICT)

    def __str__(self):
        return self.ubicacion
    
class Piso(models.Model):
    piso = models.SmallIntegerField()
    ubicacion = models.ForeignKey(Ubicacion, verbose_name="Ubicacion", on_delete=models.RESTRICT)

    def __str__(self):
        return f"{self.piso}, {self.ubicacion}"
    
class TipoLugar(models.Model):
    tipo_de_lugar = models.CharField(max_length=100)

    def __str__(self):
        return self.tipo_de_lugar

class Lugar(models.Model):
    nombre_del_lugar = models.CharField(max_length=100) #100 o 150?
    piso = models.ForeignKey(Piso, verbose_name="Piso", on_delete=models.RESTRICT)

    lugar_tipo_lugar = models.ForeignKey(TipoLugar, verbose_name="Tipo de lugar", on_delete=models.RESTRICT)

    def __str__(self):
        return self.nombre_del_lugar
    
class CategoriaObjeto(models.Model):
    nombre_de_la_categoria = models.CharField(max_length=50)

    def __str__(self):
        return self.nombre_de_la_categoria
    
class Objeto(models.Model):
    nombre_del_objeto = models.CharField(max_length=50)

    categoria = models.ForeignKey(CategoriaObjeto, verbose_name="Categoria del objeto", on_delete=models.RESTRICT)

    def __str__(self):
        return self.nombre_del_objeto

class TipoObjeto(models.Model):
    
    marca = models.CharField(max_length=50)
    material= models.CharField(max_length=60)

    objeto= models.ForeignKey(Objeto, verbose_name="Objeto", on_delete=models.RESTRICT)

    def __str__(self):
        return f"{self.marca} {self.material}"
    
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
        return f"{self.cantidad} {self.estado} { self.detalle} {self.fecha}"  
    
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
        return f"{self.cantidad_anterior} {self.estado_anterior} {self.detalle_anterior} {self.fecha_anterior}"