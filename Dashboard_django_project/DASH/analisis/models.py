# analisis/models.py
from django.db import models
from panel_0.models import Dispositivo

class Lectura(models.Model):
    dispositivo = models.ForeignKey(Dispositivo, on_delete=models.CASCADE, related_name='lecturas')
    campo = models.CharField(max_length=10)  # 'field1', 'field2', etc.
    valor = models.FloatField()
    timestamp = models.DateTimeField(db_index=True)  # Index para búsquedas rápidas

    class Meta:
        unique_together = ('dispositivo', 'campo', 'timestamp')
        indexes = [
            models.Index(fields=['dispositivo', 'campo']),
            models.Index(fields=['timestamp']),
        ]

    def __str__(self):
        return f"{self.dispositivo} - {self.campo}: {self.valor} @ {self.timestamp}"
