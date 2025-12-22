from django.forms import ModelForm, formset_factory
from django import forms
from .models import (
    Sector, Ubicacion, Piso, Lugar, TipoLugar,
    TipoObjeto, CategoriaObjeto, ObjetoLugar, Objeto,
    HistoricoObjeto,
)

# -------------------
# CREAR
# -------------------

class CrearSector(ModelForm):
    class Meta:
        model = Sector
        fields = ["sector"]


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


class CrearHistorico(forms.ModelForm):
    fecha_anterior = forms.DateField(
        input_formats=["%d/%m/%Y"],
        widget=forms.DateInput(
            format="%d/%m/%Y",
            attrs={"class": "form-control", "placeholder": "dd/mm/aaaa"},
        ),
    )

    class Meta:
        model = HistoricoObjeto
        fields = [
            "objeto_del_lugar",
            "cantidad_anterior",
            "estado_anterior",
            "detalle_anterior",
            "fecha_anterior",
        ]
        widgets = {
            "objeto_del_lugar": forms.Select(attrs={"class": "form-select"}),
            "cantidad_anterior": forms.NumberInput(attrs={"class": "form-control"}),
            "estado_anterior": forms.Select(attrs={"class": "form-select"}),
            "detalle_anterior": forms.TextInput(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["objeto_del_lugar"].disabled = True


# -------------------
# EDITAR
# -------------------

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
        fields = [
            "objeto_del_lugar",
            "cantidad_anterior",
            "estado_anterior",
            "detalle_anterior",
            "fecha_anterior",
        ]


# -------------------
# FORMULARIO UNICO DE ESTRUCTURA
# -------------------

class BaseEstructuraForm(forms.Form):
    sector = forms.CharField(max_length=100, label="Sector")
    ubicacion = forms.CharField(max_length=100, label="Ubicación")
    piso = forms.IntegerField(label="Piso", min_value=0)
    nombre_del_lugar = forms.CharField(max_length=100, label="Nombre del lugar")

    tipo_lugar_existente = forms.ModelChoiceField(
        label="Tipo de lugar (existente)",
        queryset=TipoLugar.objects.all(),
        required=False,
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    nuevo_tipo_lugar = forms.CharField(
        label="Nuevo tipo de lugar",
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            if isinstance(field.widget, forms.Select):
                field.widget.attrs.setdefault("class", "form-select")
            else:
                field.widget.attrs.setdefault("class", "form-control")

    def clean(self):
        cleaned = super().clean()
        existente = cleaned.get("tipo_lugar_existente")
        nuevo = (cleaned.get("nuevo_tipo_lugar") or "").strip()

        if not existente and not nuevo:
            raise forms.ValidationError(
                "Debes seleccionar un tipo de lugar existente o escribir uno nuevo."
            )

        cleaned["nuevo_tipo_lugar"] = nuevo
        return cleaned


class ObjetoLugarFilaForm(forms.Form):
    # EXISTENTE
    tipo_de_objeto = forms.ModelChoiceField(
        label="Tipo de objeto (existente)",
        queryset=TipoObjeto.objects.select_related("objeto", "objeto__categoria"),
        required=False,
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    # DATOS DEL OBJETO EN EL LUGAR
    cantidad = forms.IntegerField(
        label="Cantidad",
        required=False,
        min_value=1,
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )
    estado = forms.ChoiceField(
        label="Estado",
        required=False,
        choices=ObjetoLugar.ESTADO.items(),
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    detalle = forms.CharField(
        label="Detalle",
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )

    # PARA CREAR NUEVOS
    nueva_categoria = forms.CharField(
        label="Nueva categoría",
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    nuevo_objeto = forms.CharField(
        label="Nuevo objeto",
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    marca = forms.CharField(
        label="Marca",
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    material = forms.CharField(
        label="Material",
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )


ObjetoLugarFilaFormSet = formset_factory(
    ObjetoLugarFilaForm,
    extra=2,
    can_delete=False,
)