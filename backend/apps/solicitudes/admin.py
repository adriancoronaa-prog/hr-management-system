from django.contrib import admin
from .models import Solicitud


@admin.register(Solicitud)
class SolicitudAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'tipo', 'solicitante', 'aprobador', 'estado', 'prioridad', 'fecha_envio']
    list_filter = ['tipo', 'estado', 'prioridad']
    search_fields = ['titulo', 'descripcion', 'solicitante__nombres', 'solicitante__apellido_paterno']
    date_hierarchy = 'created_at'
    readonly_fields = ['id', 'created_at', 'updated_at']

    fieldsets = (
        ('Información', {
            'fields': ('id', 'tipo', 'titulo', 'descripcion', 'prioridad')
        }),
        ('Participantes', {
            'fields': ('solicitante', 'aprobador')
        }),
        ('Estado', {
            'fields': ('estado', 'fecha_envio', 'fecha_respuesta')
        }),
        ('Respuesta', {
            'fields': ('respondido_por', 'comentarios_respuesta', 'motivo_rechazo')
        }),
        ('Datos Adicionales', {
            'fields': ('datos',),
            'classes': ('collapse',)
        }),
        ('Auditoría', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
