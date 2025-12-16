from django.forms import ModelForm
from .models import Sector

class CrearSector(ModelForm):
    class Meta:
        model = Sector
        fields = ['sector']