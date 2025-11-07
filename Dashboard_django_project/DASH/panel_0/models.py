# panel_0/models.py
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class Dispositivo(models.Model):
    ESTADO_CHOICES = [
        ('online', 'Online'),
        ('offline', 'Offline'),
        ('warning', 'Advertencia'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='dispositivos')
    nombre = models.CharField(max_length=100)
    icono = models.CharField(max_length=50, default='microchip')
    thingspeak_channel = models.IntegerField(unique=True, null=True, blank=True)
    mqtt_topic = models.CharField(max_length=200, blank=True, null=True)

    # Valores del ESP32 (field1 a field8)
    valor1 = models.FloatField(null=True, blank=True)
    valor2 = models.FloatField(null=True, blank=True)
    valor3 = models.FloatField(null=True, blank=True)
    valor4 = models.FloatField(null=True, blank=True)
    valor5 = models.FloatField(null=True, blank=True)
    valor6 = models.FloatField(null=True, blank=True)
    valor7 = models.FloatField(null=True, blank=True)
    valor8 = models.FloatField(null=True, blank=True)

    # Etiquetas personalizadas
    label1 = models.CharField(max_length=30, default="Field 1", blank=True)
    label2 = models.CharField(max_length=30, default="Field 2", blank=True)
    label3 = models.CharField(max_length=30, default="Field 3", blank=True)
    label4 = models.CharField(max_length=30, default="Field 4", blank=True)
    label5 = models.CharField(max_length=30, default="Field 5", blank=True)
    label6 = models.CharField(max_length=30, default="Field 6", blank=True)
    label7 = models.CharField(max_length=30, default="Field 7", blank=True)
    label8 = models.CharField(max_length=30, default="Field 8", blank=True)

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
            if minutos > 10:
                self.estado = 'offline'
            elif minutos > 5:
                self.estado = 'warning'
            else:
                self.estado = 'online'
        self.save()

    def __str__(self):
        return f"{self.user.username}: {self.nombre}"

    class Meta:
        verbose_name = "Dispositivo ESP32"
        verbose_name_plural = "Dispositivos ESP32"
        unique_together = ('user', 'thingspeak_channel')