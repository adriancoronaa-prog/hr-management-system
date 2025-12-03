from django.contrib import admin
from .models import ConfiguracionNotificaciones, Notificacion


@admin.register(ConfiguracionNotificaciones)
class ConfiguracionNotificacionesAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'frecuencia_email', 'recibir_solicitudes', 'recibir_alertas']
    list_filter = ['frecuencia_email', 'recibir_solicitudes', 'recibir_alertas']
    search_fields = ['usuario__email']


@admin.register(Notificacion)
class NotificacionAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'tipo', 'destinatario', 'estado', 'prioridad', 'created_at']
    list_filter = ['tipo', 'estado', 'prioridad', 'enviada_email']
    search_fields = ['titulo', 'mensaje', 'destinatario__email']
    date_hierarchy = 'created_at'
    readonly_fields = ['id', 'created_at']
