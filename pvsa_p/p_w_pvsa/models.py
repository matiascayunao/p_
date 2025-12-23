from django.db import models, transaction
from django.utils import timezone


class Sector(models.Model):
    sector = models.CharField(max_length=100, unique=True )

    def __str__(self):
        return f"Sector: {self.sector}"


class Ubicacion(models.Model):
    ubicacion = models.CharField(max_length=100, unique=True )
    sector = models.ForeignKey(
        Sector,
        verbose_name="sector",
        on_delete=models.RESTRICT,
    )

    def __str__(self):
        return f"Ubicación: {self.ubicacion}"


class Piso(models.Model):
    piso = models.SmallIntegerField()
    ubicacion = models.ForeignKey(
        Ubicacion,
        verbose_name="ubicacion",
        on_delete=models.RESTRICT,
    )

    def __str__(self):
        return f"Piso: {self.piso} | Ubicación: {self.ubicacion}"


class TipoLugar(models.Model):
    tipo_de_lugar = models.CharField(max_length=100, unique=True )

    def __str__(self):
        return f"Tipo de lugar: {self.tipo_de_lugar}"


class Lugar(models.Model):
    nombre_del_lugar = models.CharField(max_length=100)
    piso = models.ForeignKey(
        Piso,
        verbose_name="piso",
        on_delete=models.RESTRICT,
    )
    lugar_tipo_lugar = models.ForeignKey(
        TipoLugar,
        verbose_name="tipo de lugar",
        on_delete=models.RESTRICT,
    )

    def __str__(self):
        return f"Lugar: {self.nombre_del_lugar}"


class CategoriaObjeto(models.Model):
    nombre_de_categoria = models.CharField(max_length=100, verbose_name="categoría", unique=True )

    def __str__(self):
        return f"Categoria: {self.nombre_de_categoria}"


class Objeto(models.Model):
    nombre_del_objeto = models.CharField(max_length=100, verbose_name="objeto", unique=True )
    objeto_categoria = models.ForeignKey(
        CategoriaObjeto,
        verbose_name="categoria",
        on_delete=models.RESTRICT,
    )

    def __str__(self):
        return f"Objeto: {self.nombre_del_objeto} | {self.objeto_categoria}"


class TipoObjeto(models.Model):
    objeto = models.ForeignKey(
        Objeto,
        verbose_name="objeto",
        on_delete=models.RESTRICT,
    )
    marca = models.CharField(max_length=100, verbose_name="marca")
    material = models.CharField(max_length=100, verbose_name="material")

    def __str__(self):
        return f"Tipo de objeto: {self.objeto} | Marca: {self.marca} | Material: {self.material}"


class ObjetoLugar(models.Model):
    ESTADO = (
        ("B", "Bueno"),
        ("P", "Pendiente"),
        ("M", "Malo"),
    )

    cantidad = models.SmallIntegerField()
    estado = models.CharField(max_length=1, choices=ESTADO)
    detalle = models.CharField(max_length=200, blank=True)
    fecha = models.DateField(auto_now_add=True)

    lugar = models.ForeignKey(
        "Lugar",
        verbose_name="lugar",
        on_delete=models.RESTRICT,
        related_name="objetos_lugar",
        null=True,
        blank=True,
    )

    tipo_de_objeto = models.ForeignKey(
        "TipoObjeto",
        verbose_name="tipo de objeto",
        on_delete=models.RESTRICT,
        related_name="objetos_lugar",
    )

    def __str__(self):
        return (
            f"Lugar: {self.lugar} | "
            f"Tipo de objeto: {self.tipo_de_objeto.objeto.nombre_del_objeto} | "
            f"Marca: {self.tipo_de_objeto.marca} | "
            f"Material: {self.tipo_de_objeto.material or '-'} | "
            f"Cant.: {self.cantidad} | "
            f"Estado: {self.get_estado_display()} | "
            f"Fecha: {self.fecha.strftime('%d/%m/%Y')}"
        )

    def save(self, *args, **kwargs):
        """
        Guarda histórico AUTOMÁTICO solo cuando cambia cantidad/estado/detalle.
        No duplica porque todo se hace aquí, y la vista NO crea Histórico.
        """
        if self.pk:
            anterior = ObjetoLugar.objects.get(pk=self.pk)

            hubo_cambio = (
                anterior.cantidad != self.cantidad
                or anterior.estado != self.estado
                or (anterior.detalle or "") != (self.detalle or "")
            )

            if hubo_cambio:
                with transaction.atomic():
                    super().save(*args, **kwargs)
                    HistoricoObjeto.objects.create(
                        objeto_del_lugar=self,
                        cantidad_anterior=anterior.cantidad,
                        estado_anterior=anterior.estado,
                        detalle_anterior=anterior.detalle or "",
                        fecha_anterior=anterior.fecha,
                    )
                return

        # creación inicial o sin cambios relevantes
        super().save(*args, **kwargs)


class HistoricoObjeto(models.Model):
    # reutilizamos las mismas choices
    ESTADO = ObjetoLugar.ESTADO

    objeto_del_lugar = models.ForeignKey(
        ObjetoLugar,
        verbose_name="objeto del lugar",
        on_delete=models.CASCADE,
        related_name="historicoobjeto",
    )
    cantidad_anterior = models.SmallIntegerField()
    estado_anterior = models.CharField(max_length=1, choices=ESTADO)
    detalle_anterior = models.CharField(max_length=200, blank=True)
    fecha_anterior = models.DateField()

    def __str__(self):
        obj = self.objeto_del_lugar
        return (
            f"Histórico de lugar: {obj.lugar} | "
            f"Tipo de objeto: {obj.tipo_de_objeto.objeto.nombre_del_objeto} | "
            f"Marca: {obj.tipo_de_objeto.marca} | "
            f"Material: {obj.tipo_de_objeto.material or '-'} | "
            f"Cant. ant.: {self.cantidad_anterior} | "
            f"Estado ant.: {self.get_estado_anterior_display()} | "
            f"Fecha ant.: {self.fecha_anterior.strftime('%d/%m/%Y')}"
        )