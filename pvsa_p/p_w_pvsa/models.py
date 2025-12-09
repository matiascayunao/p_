from django.db import models


class Ubicacion(models.Model):
    ubicacion_nombre = models.CharField(max_length=100)
    
    def __str__(self):
        return self.ubicacion_nombre
    
class Sector(models.Model):
    sector_nombre = models.CharField(max_length=100)

    sector_ubicacion = models.ForeignKey(Ubicacion, verbose_name=" relacionado ubicacion", on_delete=models.RESTRICT),


    def __str__(self):
        return self.sector_nombre
    
class TipoLugar(models.Model):
    # tl = Tipo Lugar<
    tl_nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.tl_nombre

class Lugar(models.Model):
    lugar_nombre = models.CharField(max_length=100) #100 o 150?

    lugar_sector = models.ForeignKey(Sector, verbose_name="relacionado sector", on_delete=models.RESTRICT)
    lugar_tipo_lugar = models.ForeignKey(TipoLugar, verbose_name="relacionado tipo lugar", on_delete=models.RESTRICT)

    def __str__(self):
        return self.lugar_nombre
    
class CategoriaObjeto(models.Model):
    categoria_nombre = models.CharField(max_length=50)

    def __str__(self):
        return self.categoria_nombre
    
class Objeto(models.Model):
    objeto_nombre = models.CharField(max_lenght=50)

    objeto_categoria = models.ForeignKey(CategoriaObjeto, verbose_name="relacionado categoria objeto", on_delete=models.RESTRICT)

    def __str__(self):
        return self.objeto_nombre

class TipoObjeto(models.Model):
    #to = Tipo Objeto
    to_marca = models.CharField(max_length=50)
    to_material = models.CharField(max_length=60)

    to_objeto= models.ForeignKey(Objeto, verbose_name="relacionado objeto", on_delete=models.RESTRICT)

    def __str__(self):
        return f"{self.to_marca} {self.to_material}"
    
class ObjetoLugar(models.Model):

    # ol = Objeto Lugar
    ESTADO = {
        "B": "Bueno",
        "P": "Pendiente",
        "M": "Malo"
    }
    ol_cantidad = models.SmallIntegerField()
    ol_estado = models.CharField(max_length=1, choices=ESTADO)
    ol_detalle = models.CharField(max_length=200)
    ol_fecha = models.DateField.auto_now_add()

    ol_lugar= models.ForeignKey(Lugar, verbose_name= "relacionado lugar", on_delete=models.RESTRICT)
    ol_tipo_objeto = models.ForeignKey(TipoObjeto, verbose_name="relacionado tipo objeto", on_delete=models.RESTRICT)

    def __str__(self):
        return f"{self.ol_cantidad} {self.ol_estado} { self.ol_detalle} {self.ol_fecha}"  #no sé si agregar el lugar o el tipo de objeto
    
class HistoricoObjeto(models.Model):
    # ho = Historico Objeto
    ESTADO = {
        "B": "Bueno",
        "P": "Pendiente",
        "M": "Malo"
    }
    ho_ant_cant =models.SmallIntegerField()
    ho_ant_estado = models.CharField(max_length=1, choices=ESTADO)
    ho_ant_detalle = models.CharField(max_length=200)
    ho_ant_fecha = models.DateField.auto_now_add()

    ho_objeto_lugar = models.ForeignKey(ObjetoLugar, verbose_name="relacionado objeto lugar", on_delete=models.RESTRICT)

    def __str__(self):
        return f"{self.ho_ant_cant} {self.ho_ant_estado} {self.ho_ant_detalle} {self.ho_ant_fecha}"