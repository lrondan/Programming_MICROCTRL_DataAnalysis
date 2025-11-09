# panel_0/admin.py
from django.contrib import admin
from .models import Dispositivo, Lectura

@admin.register(Dispositivo)
class DispositivoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'user', 'thingspeak_channel', 'estado', 'ultimo_dato')
    list_filter = ('estado', 'user')
    search_fields = ('nombre', 'thingspeak_channel')
    readonly_fields = ('ultimo_dato', 'estado')

    fieldsets = (
        ('Información Básica', {
            'fields': ('user', 'nombre', 'icono', 'thingspeak_channel', 'thingspeak_read_key')
        }),
        ('Valores Actuales', {
            'fields': (('valor1', 'label1', 'unidad1'),
                       ('valor2', 'label2', 'unidad2'),
                       ('valor3', 'label3', 'unidad3'),
                       ('valor4', 'label4', 'unidad4'),
                       ('valor5', 'label5', 'unidad5'),
                       ('valor6', 'label6', 'unidad6'),
                       ('valor7', 'label7', 'unidad7'),
                       ('valor8', 'label8', 'unidad8'))
        }),
        ('Estado', {
            'fields': ('ultimo_dato', 'estado'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Lectura)
class LecturaAdmin(admin.ModelAdmin):
    list_display = ('dispositivo', 'creado_en', 'field1', 'field2', 'field3', 'field4')
    list_filter = ('dispositivo', 'creado_en')
    search_fields = ('dispositivo__nombre',)
    date_hierarchy = 'creado_en'
    readonly_fields = ('creado_en',)

    # Mostrar todos los fields en detalle
    fieldsets = (
        ('Dispositivo', {
            'fields': ('dispositivo',)
        }),
        ('Valores', {
            'fields': (('field1', 'field2', 'field3', 'field4'),
                       ('field5', 'field6', 'field7', 'field8'))
        }),
        ('Fecha', {
            'fields': ('creado_en',),
            'classes': ('collapse',)
        }),
    )

    # Optimizar: solo cargar datos necesarios
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('dispositivo')