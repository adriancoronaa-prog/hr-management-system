"""
Modelos para el sistema genérico de solicitudes/aprobaciones
"""
import uuid
from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class Solicitud(models.Model):
    """
    Modelo genérico para solicitudes que requieren aprobación.
    Puede relacionarse con cualquier objeto (vacaciones, KPIs, permisos, etc.)
    """

    class Meta:
        verbose_name = 'Solicitud'
        verbose_name_plural = 'Solicitudes'
        db_table = 'solicitudes_registro'
        ordering = ['-created_at']

    TIPO_CHOICES = [
        ('vacaciones', 'Vacaciones'),
        ('permiso', 'Permiso'),
        ('incapacidad', 'Incapacidad'),
        ('kpi', 'Modificación de KPI'),
        ('salario', 'Modificación de Salario'),
        ('documento', 'Documento'),
        ('baja', 'Baja'),
        ('otro', 'Otro'),
    ]

    ESTADO_CHOICES = [
        ('borrador', 'Borrador'),
        ('pendiente', 'Pendiente de Aprobación'),
        ('aprobada', 'Aprobada'),
        ('rechazada', 'Rechazada'),
        ('cancelada', 'Cancelada'),
    ]

    PRIORIDAD_CHOICES = [
        ('baja', 'Baja'),
        ('media', 'Media'),
        ('alta', 'Alta'),
        ('urgente', 'Urgente'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Tipo de solicitud
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    prioridad = models.CharField(max_length=10, choices=PRIORIDAD_CHOICES, default='media')

    # Solicitante
    solicitante = models.ForeignKey(
        'empleados.Empleado',
        on_delete=models.CASCADE,
        related_name='solicitudes_realizadas'
    )

    # Aprobador (jefe directo o asignado)
    aprobador = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='solicitudes_por_aprobar'
    )

    # Estado
    estado = models.CharField(max_length=15, choices=ESTADO_CHOICES, default='borrador')

    # Objeto relacionado (genérico)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.CharField(max_length=50, null=True, blank=True)
    objeto_relacionado = GenericForeignKey('content_type', 'object_id')

    # Datos específicos de la solicitud
    datos = models.JSONField(default=dict, blank=True)

    # Fechas
    fecha_envio = models.DateTimeField(null=True, blank=True)
    fecha_respuesta = models.DateTimeField(null=True, blank=True)

    # Respuesta
    respondido_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='solicitudes_respondidas'
    )
    comentarios_respuesta = models.TextField(blank=True)
    motivo_rechazo = models.TextField(blank=True)

    # Auditoría
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.get_tipo_display()}: {self.titulo} - {self.solicitante}'

    def enviar(self):
        """Envía la solicitud para aprobación"""
        from django.utils import timezone
        from apps.notificaciones.services import NotificacionService

        if self.estado != 'borrador':
            raise ValueError('Solo se pueden enviar solicitudes en estado borrador')

        # Determinar aprobador si no está asignado
        if not self.aprobador and self.solicitante.jefe_directo:
            if self.solicitante.jefe_directo.usuario:
                self.aprobador = self.solicitante.jefe_directo.usuario

        if not self.aprobador:
            raise ValueError('No se pudo determinar el aprobador para esta solicitud')

        self.estado = 'pendiente'
        self.fecha_envio = timezone.now()
        self.save()

        # Notificar al aprobador
        NotificacionService.notificar_solicitud_pendiente(
            solicitante=self.solicitante,
            jefe=self.aprobador,
            tipo_solicitud=self.get_tipo_display(),
            solicitud=self,
            detalles=self.datos
        )

        return self

    def aprobar(self, usuario, comentarios=''):
        """Aprueba la solicitud"""
        from django.utils import timezone
        from apps.notificaciones.services import NotificacionService

        if self.estado != 'pendiente':
            raise ValueError('Solo se pueden aprobar solicitudes pendientes')

        self.estado = 'aprobada'
        self.fecha_respuesta = timezone.now()
        self.respondido_por = usuario
        self.comentarios_respuesta = comentarios
        self.save()

        # Notificar al solicitante
        if self.solicitante.usuario:
            NotificacionService.notificar_aprobacion(
                destinatario=self.solicitante.usuario,
                tipo_solicitud=self.get_tipo_display(),
                solicitud=self,
                aprobador=usuario,
                comentarios=comentarios
            )

        return self

    def rechazar(self, usuario, motivo):
        """Rechaza la solicitud"""
        from django.utils import timezone
        from apps.notificaciones.services import NotificacionService

        if self.estado != 'pendiente':
            raise ValueError('Solo se pueden rechazar solicitudes pendientes')

        self.estado = 'rechazada'
        self.fecha_respuesta = timezone.now()
        self.respondido_por = usuario
        self.motivo_rechazo = motivo
        self.save()

        # Notificar al solicitante
        if self.solicitante.usuario:
            NotificacionService.notificar_rechazo(
                destinatario=self.solicitante.usuario,
                tipo_solicitud=self.get_tipo_display(),
                solicitud=self,
                rechazador=usuario,
                motivo=motivo
            )

        return self

    def cancelar(self):
        """Cancela la solicitud"""
        if self.estado in ['aprobada', 'rechazada']:
            raise ValueError('No se pueden cancelar solicitudes ya procesadas')

        self.estado = 'cancelada'
        self.save()
        return self

    @classmethod
    def crear_desde_vacaciones(cls, solicitud_vacaciones):
        """Crea una Solicitud genérica desde SolicitudVacaciones"""
        content_type = ContentType.objects.get_for_model(solicitud_vacaciones)

        solicitud = cls.objects.create(
            tipo='vacaciones',
            titulo=f'Vacaciones: {solicitud_vacaciones.fecha_inicio} - {solicitud_vacaciones.fecha_fin}',
            descripcion=solicitud_vacaciones.motivo or '',
            solicitante=solicitud_vacaciones.empleado,
            aprobador=solicitud_vacaciones.empleado.jefe_directo.usuario if solicitud_vacaciones.empleado.jefe_directo and solicitud_vacaciones.empleado.jefe_directo.usuario else None,
            content_type=content_type,
            object_id=str(solicitud_vacaciones.pk),
            datos={
                'fecha_inicio': str(solicitud_vacaciones.fecha_inicio),
                'fecha_fin': str(solicitud_vacaciones.fecha_fin),
                'dias_solicitados': solicitud_vacaciones.dias_solicitados,
                'motivo': solicitud_vacaciones.motivo or '',
            }
        )
        return solicitud
