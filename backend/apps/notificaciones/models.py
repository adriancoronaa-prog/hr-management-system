"""
Modelos para el sistema de notificaciones
"""
import uuid
from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class ConfiguracionNotificaciones(models.Model):
    """Preferencias de notificación por usuario"""

    class Meta:
        verbose_name = 'Configuración de Notificaciones'
        verbose_name_plural = 'Configuraciones de Notificaciones'
        db_table = 'notificaciones_configuracion'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='config_notificaciones'
    )

    # Tipos de notificación habilitados
    recibir_solicitudes = models.BooleanField(default=True, help_text='Notificar solicitudes pendientes de aprobación')
    recibir_alertas = models.BooleanField(default=True, help_text='Alertas de vencimientos y recordatorios')
    recibir_confirmaciones = models.BooleanField(default=True, help_text='Confirmaciones de acciones completadas')
    recibir_nomina = models.BooleanField(default=True, help_text='Notificaciones de nómina y recibos')

    # Frecuencia de resúmenes
    FRECUENCIA_CHOICES = [
        ('inmediato', 'Inmediato'),
        ('diario', 'Resumen Diario'),
        ('semanal', 'Resumen Semanal'),
        ('nunca', 'Nunca'),
    ]
    frecuencia_email = models.CharField(max_length=20, choices=FRECUENCIA_CHOICES, default='inmediato')

    # Horario preferido para resúmenes
    hora_envio = models.TimeField(default='09:00', help_text='Hora preferida para envío de resúmenes')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Config notificaciones - {self.usuario.email}'


class Notificacion(models.Model):
    """Registro de notificaciones enviadas"""

    class Meta:
        verbose_name = 'Notificación'
        verbose_name_plural = 'Notificaciones'
        db_table = 'notificaciones_registro'
        ordering = ['-created_at']

    TIPO_CHOICES = [
        ('solicitud', 'Solicitud de Aprobación'),
        ('aprobacion', 'Aprobación'),
        ('rechazo', 'Rechazo'),
        ('alerta', 'Alerta'),
        ('recordatorio', 'Recordatorio'),
        ('confirmacion', 'Confirmación'),
        ('nomina', 'Nómina'),
        ('documento', 'Documento'),
        ('sistema', 'Sistema'),
    ]

    PRIORIDAD_CHOICES = [
        ('baja', 'Baja'),
        ('media', 'Media'),
        ('alta', 'Alta'),
        ('urgente', 'Urgente'),
    ]

    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('enviada', 'Enviada'),
        ('leida', 'Leída'),
        ('fallida', 'Fallida'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Destinatario
    destinatario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notificaciones_recibidas'
    )

    # Contenido
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    prioridad = models.CharField(max_length=10, choices=PRIORIDAD_CHOICES, default='media')
    titulo = models.CharField(max_length=200)
    mensaje = models.TextField()

    # Objeto relacionado (genérico)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.CharField(max_length=50, null=True, blank=True)
    objeto_relacionado = GenericForeignKey('content_type', 'object_id')

    # Estado
    estado = models.CharField(max_length=15, choices=ESTADO_CHOICES, default='pendiente')
    enviada_email = models.BooleanField(default=False)
    fecha_envio_email = models.DateTimeField(null=True, blank=True)
    error_envio = models.TextField(blank=True)

    # Tracking
    fecha_lectura = models.DateTimeField(null=True, blank=True)

    # Metadatos
    datos_extra = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.tipo}: {self.titulo} -> {self.destinatario.email}'

    def marcar_leida(self):
        """Marca la notificación como leída"""
        from django.utils import timezone
        if not self.fecha_lectura:
            self.fecha_lectura = timezone.now()
            self.estado = 'leida'
            self.save(update_fields=['fecha_lectura', 'estado'])
