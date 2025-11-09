# panel_0/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Dispositivo(models.Model):
    ESTADO_CHOICES = [
        ('online', 'Online'),
        ('offline', 'Offline'),
        ('warning', 'Advertencia'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='dispositivos')
    nombre = models.CharField(max_length=100)
    icono = models.CharField(max_length=50, default='microchip')
    thingspeak_channel = models.IntegerField(null=True, blank=True)
    thingspeak_read_key = models.CharField(max_length=50, blank=True, null=True)
    mqtt_topic = models.CharField(max_length=200, blank=True, null=True)

    # Valores actuales
    valor1 = models.FloatField(null=True, blank=True)
    valor2 = models.FloatField(null=True, blank=True)
    valor3 = models.FloatField(null=True, blank=True)
    valor4 = models.FloatField(null=True, blank=True)
    valor5 = models.FloatField(null=True, blank=True)
    valor6 = models.FloatField(null=True, blank=True)
    valor7 = models.FloatField(null=True, blank=True)
    valor8 = models.FloatField(null=True, blank=True)

    # Etiquetas
    label1 = models.CharField(max_length=30, default="Field 1", blank=True)
    label2 = models.CharField(max_length=30, default="Field 2", blank=True)
    label3 = models.CharField(max_length=30, default="Field 3", blank=True)
    label4 = models.CharField(max_length=30, default="Field 4", blank=True)
    label5 = models.CharField(max_length=30, default="Field 5", blank=True)
    label6 = models.CharField(max_length=30, default="Field 6", blank=True)
    label7 = models.CharField(max_length=30, default="Field 7", blank=True)
    label8 = models.CharField(max_length=30, default="Field 8", blank=True)

    # Unidades
    unidad1 = models.CharField(max_length=10, default="°C", blank=True)
    unidad2 = models.CharField(max_length=10, default="%", blank=True)
    unidad3 = models.CharField(max_length=10, default="", blank=True)
    unidad4 = models.CharField(max_length=10, default="", blank=True)
    unidad5 = models.CharField(max_length=10, default="", blank=True)
    unidad6 = models.CharField(max_length=10, default="", blank=True)
    unidad7 = models.CharField(max_length=10, default="", blank=True)
    unidad8 = models.CharField(max_length=10, default="", blank=True)

    ultimo_dato = models.DateTimeField(null=True, blank=True)
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='offline')

    def actualizar_estado(self):
        if not self.ultimo_dato:
            self.estado = 'offline'
        else:
            minutos = (timezone.now() - self.ultimo_dato).total_seconds() / 60
            if minutos <= 5:
                self.estado = 'online'
            elif minutos <= 10:
                self.estado = 'warning'
            else:
                self.estado = 'offline'
        self.save(update_fields=['estado'])

    def __str__(self):
        return f"{self.user.username}: {self.nombre}"


class Lectura(models.Model):
    dispositivo = models.ForeignKey(
        Dispositivo, 
        on_delete=models.CASCADE, 
        related_name='panel_lecturas'
    )
    field1 = models.FloatField(null=True, blank=True)
    field2 = models.FloatField(null=True, blank=True)
    field3 = models.FloatField(null=True, blank=True)
    field4 = models.FloatField(null=True, blank=True)
    field5 = models.FloatField(null=True, blank=True)
    field6 = models.FloatField(null=True, blank=True)
    field7 = models.FloatField(null=True, blank=True)
    field8 = models.FloatField(null=True, blank=True)
    
    creado_en = models.DateTimeField(auto_now_add=True)  # ← SE LLENA AUTOMÁTICAMENTE

    class Meta:
        ordering = ['-creado_en']