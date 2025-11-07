# panel_0/forms.py
from django import forms
from .models import Dispositivo

class DispositivoForm(forms.ModelForm):
    class Meta:
        model = Dispositivo
        fields = ['nombre', 'thingspeak_channel', 'icono', 'label1', 'unidad1', 'label2', 'unidad2']
        widgets = {
            'nombre': forms.TextInput(attrs={'placeholder': 'ESP32 Sala'}),
            'thingspeak_channel': forms.NumberInput(attrs={'placeholder': '1234567'}),
            'icono': forms.Select(choices=[
                ('microchip', 'Microchip'),
                ('thermometer-half', 'Temperatura'),
                ('tint', 'Humedad'),
                ('wind', 'Viento'),
                ('lightbulb', 'Luz'),
                ('bolt', 'Voltaje'),
            ]),
        }