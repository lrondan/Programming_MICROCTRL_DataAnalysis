# panel_0/admin.py
from django.contrib import admin
from .models import Dispositivo

@admin.register(Dispositivo)
class DispositivoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'user','thingspeak_channel', 'estado', 'ultimo_dato')
    list_filter = ('user', 'estado','ultimo_dato')
    search_fields = ('user__username', 'nombre', 'thingspeak_channel')
    fieldsets = (
        ('General', {
            'fields': ('nombre', 'icono', 'thingspeak_channel', 'mqtt_topic')
        }),
        ('Campo 1', {'fields': ('label1', 'valor1', 'unidad1')}),
        ('Campo 2', {'fields': ('label2', 'valor2', 'unidad2')}),
        ('Campo 3', {'fields': ('label3', 'valor3', 'unidad3')}),
        ('Campo 4', {'fields': ('label4', 'valor4', 'unidad4')}),
        ('Campo 5', {'fields': ('label5', 'valor5', 'unidad5')}),
        ('Campo 6', {'fields': ('label6', 'valor6', 'unidad6')}),
        ('Campo 7', {'fields': ('label7', 'valor7', 'unidad7')}),
        ('Campo 8', {'fields': ('label8', 'valor8', 'unidad8')}),
        ('Estado', {'fields': ('estado', 'ultimo_dato'), 'classes': ('collapse',)}),
    )
    readonly_fields = ('estado', 'ultimo_dato', 'valor1', 'valor2', 'valor3', 'valor4', 'valor5', 'valor6', 'valor7', 'valor8')