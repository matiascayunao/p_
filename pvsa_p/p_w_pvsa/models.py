from django.db import models

    
class Sector(models.Model):
    sector = models.CharField(max_length=100)

    def __str__(self):
        return self.sector
     
class Ubicacion(models.Model):
    ubicacion = models.CharField(max_length=100)
    sector = models.ForeignKey(Sector, verbose_name="relacionado con sector", on_delete=models.RESTRICT)
    def __str__(self):
        return self.ubicacion
    
class TipoLugar(models.Model):
    tipo_de_lugar = models.CharField(max_length=100)

    def __str__(self):
        return self.tipo_de_lugar

class Lugar(models.Model):
    nombre_del_lugar = models.CharField(max_length=100) #100 o 150?
    ubicacion = models.ForeignKey(Ubicacion, verbose_name="relacionado con ubicacion", on_delete=models.RESTRICT)

    lugar_tipo_lugar = models.ForeignKey(TipoLugar, verbose_name="relacionado con tipo lugar", on_delete=models.RESTRICT)

    def __str__(self):
        return self.nombre_del_lugar
    
class CategoriaObjeto(models.Model):
    nombre_de_la_categoria = models.CharField(max_length=50)

    def __str__(self):
        return self.nombre_de_la_categoria
    
class Objeto(models.Model):
    nombre_del_objeto = models.CharField(max_length=50)

    categoria = models.ForeignKey(CategoriaObjeto, verbose_name="relacionado con categoria objeto", on_delete=models.RESTRICT)

    def __str__(self):
        return self.nombre_del_objeto

class TipoObjeto(models.Model):
    
    marca = models.CharField(max_length=50)
    material= models.CharField(max_length=60)

    objeto= models.ForeignKey(Objeto, verbose_name="relacionado con objeto", on_delete=models.RESTRICT)

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
    detalle = models.CharField(max_length=200)
    fecha = models.DateField()

    lugar= models.ForeignKey(Lugar, verbose_name= "relacionado lugar", on_delete=models.RESTRICT)
    tipo_de_objeto = models.ForeignKey(TipoObjeto, verbose_name="relacionado tipo objeto", on_delete=models.RESTRICT)

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
    detalle_anterior= models.CharField(max_length=200)
    fecha_anterior = models.DateField()

    objeto_del_lugar = models.ForeignKey(ObjetoLugar, verbose_name="relacionado con objeto lugar", on_delete=models.RESTRICT)

    def __str__(self):
        return f"{self.cantidad_anterior} {self.estado_anterior} {self.detalle_anterior} {self.fecha_anterior}"