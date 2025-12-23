from django.forms import ModelForm, formset_factory
from django import forms
from .models import (
    Sector,
    Ubicacion,
    Piso,
    Lugar,
    TipoLugar,
    TipoObjeto,
    CategoriaObjeto,
    ObjetoLugar,
    Objeto,
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


class CrearObjetoLugar(forms.ModelForm):
    class Meta:
        model = ObjetoLugar
        fields = ["tipo_de_objeto", "cantidad", "estado", "detalle"]
        widgets = {
            "cantidad": forms.NumberInput(attrs={"class": "form-control"}),
            "estado": forms.Select(attrs={"class": "form-select"}),
            "detalle": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Detalle (opcional)"}
            ),
        }


class CrearTipoLugar(ModelForm):
    class Meta:
        model = TipoLugar
        fields = ["tipo_de_lugar"]


class CrearCategoriaObjeto(ModelForm):
    class Meta:
        model = CategoriaObjeto
        fields = ["nombre_de_categoria"]


class CrearObjeto(ModelForm):
    class Meta:
        model = Objeto
        fields = ["nombre_del_objeto", "objeto_categoria"]


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
        fields = ["nombre_de_categoria"]


class EditarObjeto(ModelForm):
    class Meta:
        model = Objeto
        fields = ["nombre_del_objeto", "objeto_categoria"]


class EditarTipoObjeto(ModelForm):
    class Meta:
        model = TipoObjeto
        fields = ["objeto", "marca", "material"]


class EditarObjetoLugar(forms.ModelForm):
    class Meta:
        model = ObjetoLugar
        fields = ["tipo_de_objeto", "cantidad", "estado", "detalle"]
        widgets = {
            "tipo_de_objeto": forms.Select(attrs={"class": "form-select"}),
            "cantidad": forms.NumberInput(attrs={"class": "form-control"}),
            "estado": forms.Select(attrs={"class": "form-select"}),
            "detalle": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Detalle (opcional)"}
            ),
        }


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
# FORMULARIO ÚNICO DE ESTRUCTURA
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
    tipo_de_objeto = forms.ModelChoiceField(
        label="Tipo de objeto",
        queryset=TipoObjeto.objects.select_related("objeto")
        .all()
        .order_by("objeto__nombre_del_objeto", "marca", "material"),
        widget=forms.Select(attrs={"class": "form-select form-select-sm"}),
    )

    cantidad = forms.IntegerField(
        label="Cant.",
        min_value=0,
        widget=forms.NumberInput(
            attrs={
                "class": "form-control form-control-sm",
                "style": "width: 80px;",
            }
        ),
    )

    estado = forms.ChoiceField(
        label="Estado",
        choices=ObjetoLugar.ESTADO,  # <-- SIN .items()
        widget=forms.Select(attrs={"class": "form-select form-select-sm"}),
    )

    detalle = forms.CharField(
        label="Detalle",
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control form-control-sm",
                "placeholder": "Detalle (opcional)",
            }
        ),
    )


ObjetoLugarFilaFormSet = formset_factory(
    ObjetoLugarFilaForm,
    extra=2,
    can_delete=False,
)