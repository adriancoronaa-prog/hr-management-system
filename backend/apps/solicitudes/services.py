"""
Servicio para gestionar solicitudes
"""
from django.db.models import Q
from django.utils import timezone
from .models import Solicitud


class SolicitudService:
    """Servicio centralizado para gestión de solicitudes"""

    @staticmethod
    def crear_solicitud(
        tipo,
        titulo,
        solicitante,
        descripcion='',
        prioridad='media',
        objeto_relacionado=None,
        datos=None,
        aprobador=None,
        enviar_inmediatamente=False
    ):
        """
        Crea una nueva solicitud

        Args:
            tipo: Tipo de solicitud (vacaciones, permiso, kpi, etc.)
            titulo: Título descriptivo
            solicitante: Empleado que hace la solicitud
            descripcion: Descripción detallada
            prioridad: baja, media, alta, urgente
            objeto_relacionado: Objeto Django relacionado
            datos: Dict con datos adicionales
            aprobador: Usuario aprobador (si no se especifica, usa jefe_directo)
            enviar_inmediatamente: Si True, envía la solicitud al crearla

        Returns:
            Solicitud: Objeto creado
        """
        from django.contrib.contenttypes.models import ContentType

        # Preparar content type si hay objeto relacionado
        content_type = None
        object_id = None
        if objeto_relacionado:
            content_type = ContentType.objects.get_for_model(objeto_relacionado)
            object_id = str(objeto_relacionado.pk)

        # Determinar aprobador
        if not aprobador and solicitante.jefe_directo and solicitante.jefe_directo.usuario:
            aprobador = solicitante.jefe_directo.usuario

        solicitud = Solicitud.objects.create(
            tipo=tipo,
            titulo=titulo,
            descripcion=descripcion,
            prioridad=prioridad,
            solicitante=solicitante,
            aprobador=aprobador,
            content_type=content_type,
            object_id=object_id,
            datos=datos or {},
        )

        if enviar_inmediatamente:
            solicitud.enviar()

        return solicitud

    @staticmethod
    def obtener_pendientes_aprobador(usuario):
        """Obtiene solicitudes pendientes para un aprobador"""
        return Solicitud.objects.filter(
            aprobador=usuario,
            estado='pendiente'
        ).select_related('solicitante', 'content_type')

    @staticmethod
    def obtener_solicitudes_empleado(empleado, estado=None):
        """Obtiene solicitudes de un empleado"""
        qs = Solicitud.objects.filter(solicitante=empleado)
        if estado:
            qs = qs.filter(estado=estado)
        return qs.select_related('aprobador', 'respondido_por')

    @staticmethod
    def aprobar_solicitud(solicitud_id, usuario, comentarios=''):
        """Aprueba una solicitud"""
        solicitud = Solicitud.objects.get(id=solicitud_id)

        # Verificar que el usuario puede aprobar
        if solicitud.aprobador != usuario:
            raise PermissionError('No tienes permiso para aprobar esta solicitud')

        return solicitud.aprobar(usuario, comentarios)

    @staticmethod
    def rechazar_solicitud(solicitud_id, usuario, motivo):
        """Rechaza una solicitud"""
        solicitud = Solicitud.objects.get(id=solicitud_id)

        # Verificar que el usuario puede rechazar
        if solicitud.aprobador != usuario:
            raise PermissionError('No tienes permiso para rechazar esta solicitud')

        if not motivo:
            raise ValueError('Debe proporcionar un motivo para el rechazo')

        return solicitud.rechazar(usuario, motivo)

    @staticmethod
    def obtener_resumen_pendientes(usuario):
        """Obtiene resumen de solicitudes pendientes para dashboard"""
        pendientes = Solicitud.objects.filter(
            aprobador=usuario,
            estado='pendiente'
        )

        return {
            'total': pendientes.count(),
            'urgentes': pendientes.filter(prioridad='urgente').count(),
            'altas': pendientes.filter(prioridad='alta').count(),
            'por_tipo': {
                tipo[0]: pendientes.filter(tipo=tipo[0]).count()
                for tipo in Solicitud.TIPO_CHOICES
            }
        }
