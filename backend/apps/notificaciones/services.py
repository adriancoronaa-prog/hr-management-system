"""
Servicio principal de notificaciones
"""
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from .models import Notificacion, ConfiguracionNotificaciones
from .email_service import EmailService
import logging

logger = logging.getLogger(__name__)


class NotificacionService:
    """Servicio centralizado para crear y gestionar notificaciones"""

    @staticmethod
    def crear_notificacion(
        destinatario,
        tipo,
        titulo,
        mensaje,
        objeto_relacionado=None,
        prioridad='media',
        enviar_email=True,
        datos_extra=None
    ):
        """
        Crea una notificación y opcionalmente envía email

        Args:
            destinatario: Usuario destinatario
            tipo: Tipo de notificación (solicitud, aprobacion, alerta, etc.)
            titulo: Título corto
            mensaje: Mensaje completo
            objeto_relacionado: Objeto Django relacionado (opcional)
            prioridad: baja, media, alta, urgente
            enviar_email: Si debe enviar email inmediatamente
            datos_extra: Dict con datos adicionales

        Returns:
            Notificacion: Objeto de notificación creado
        """
        try:
            # Verificar configuración del usuario
            config = NotificacionService._obtener_config(destinatario)

            # Verificar si el usuario quiere este tipo de notificación
            if not NotificacionService._usuario_acepta_tipo(config, tipo):
                logger.info(f"Usuario {destinatario.email} tiene deshabilitadas notificaciones tipo {tipo}")
                return None

            # Preparar content type si hay objeto relacionado
            content_type = None
            object_id = None
            if objeto_relacionado:
                content_type = ContentType.objects.get_for_model(objeto_relacionado)
                object_id = str(objeto_relacionado.pk)

            # Crear notificación
            notificacion = Notificacion.objects.create(
                destinatario=destinatario,
                tipo=tipo,
                prioridad=prioridad,
                titulo=titulo,
                mensaje=mensaje,
                content_type=content_type,
                object_id=object_id,
                datos_extra=datos_extra or {},
            )

            # Enviar email si corresponde
            if enviar_email and config.frecuencia_email == 'inmediato':
                NotificacionService._enviar_email_notificacion(notificacion)

            return notificacion

        except Exception as e:
            logger.error(f"Error creando notificación: {str(e)}")
            raise

    @staticmethod
    def notificar_solicitud_pendiente(solicitante, jefe, tipo_solicitud, solicitud, detalles):
        """
        Notifica al jefe sobre una nueva solicitud pendiente

        Args:
            solicitante: Empleado que hace la solicitud
            jefe: Usuario jefe que debe aprobar
            tipo_solicitud: String descriptivo (ej: "Vacaciones", "Modificación KPI")
            solicitud: Objeto de la solicitud
            detalles: Dict con detalles para mostrar
        """
        titulo = f'Solicitud de {tipo_solicitud} pendiente'
        mensaje = f'{solicitante.nombre_completo} ha enviado una solicitud de {tipo_solicitud} que requiere tu aprobación.'

        return NotificacionService.crear_notificacion(
            destinatario=jefe,
            tipo='solicitud',
            titulo=titulo,
            mensaje=mensaje,
            objeto_relacionado=solicitud,
            prioridad='alta',
            datos_extra={
                'solicitante_id': str(solicitante.id),
                'solicitante_nombre': solicitante.nombre_completo,
                'tipo_solicitud': tipo_solicitud,
                'detalles': detalles,
            }
        )

    @staticmethod
    def notificar_aprobacion(destinatario, tipo_solicitud, solicitud, aprobador, comentarios=''):
        """Notifica que una solicitud fue aprobada"""
        titulo = f'{tipo_solicitud} aprobada'
        mensaje = f'Tu solicitud de {tipo_solicitud} ha sido aprobada por {aprobador.get_full_name()}.'
        if comentarios:
            mensaje += f' Comentarios: {comentarios}'

        return NotificacionService.crear_notificacion(
            destinatario=destinatario,
            tipo='aprobacion',
            titulo=titulo,
            mensaje=mensaje,
            objeto_relacionado=solicitud,
            datos_extra={
                'aprobador_nombre': aprobador.get_full_name(),
                'comentarios': comentarios,
            }
        )

    @staticmethod
    def notificar_rechazo(destinatario, tipo_solicitud, solicitud, rechazador, motivo):
        """Notifica que una solicitud fue rechazada"""
        titulo = f'{tipo_solicitud} rechazada'
        mensaje = f'Tu solicitud de {tipo_solicitud} ha sido rechazada por {rechazador.get_full_name()}. Motivo: {motivo}'

        return NotificacionService.crear_notificacion(
            destinatario=destinatario,
            tipo='rechazo',
            titulo=titulo,
            mensaje=mensaje,
            objeto_relacionado=solicitud,
            prioridad='alta',
            datos_extra={
                'rechazador_nombre': rechazador.get_full_name(),
                'motivo': motivo,
            }
        )

    @staticmethod
    def notificar_alerta_vencimiento(destinatario, documento, dias_restantes):
        """Notifica sobre documento próximo a vencer"""
        prioridad = 'urgente' if dias_restantes <= 3 else 'alta' if dias_restantes <= 7 else 'media'
        titulo = f'Documento próximo a vencer ({dias_restantes} días)'
        mensaje = f'El documento {documento.nombre} del empleado {documento.empleado.nombre_completo} vence el {documento.fecha_vencimiento}.'

        return NotificacionService.crear_notificacion(
            destinatario=destinatario,
            tipo='alerta',
            titulo=titulo,
            mensaje=mensaje,
            objeto_relacionado=documento,
            prioridad=prioridad,
            datos_extra={
                'empleado_id': str(documento.empleado.id),
                'empleado_nombre': documento.empleado.nombre_completo,
                'fecha_vencimiento': str(documento.fecha_vencimiento),
                'dias_restantes': dias_restantes,
            }
        )

    @staticmethod
    def notificar_recibo_nomina(empleado, recibo):
        """Notifica que hay un nuevo recibo de nómina disponible"""
        # Obtener usuario del empleado
        if not empleado.usuario:
            return None

        titulo = f'Recibo de nómina disponible'
        mensaje = f'Tu recibo de nómina del periodo {recibo.periodo_inicio} - {recibo.periodo_fin} está disponible.'

        return NotificacionService.crear_notificacion(
            destinatario=empleado.usuario,
            tipo='nomina',
            titulo=titulo,
            mensaje=mensaje,
            objeto_relacionado=recibo,
            datos_extra={
                'periodo_inicio': str(recibo.periodo_inicio),
                'periodo_fin': str(recibo.periodo_fin),
            }
        )

    @staticmethod
    def obtener_notificaciones_pendientes(usuario):
        """Obtiene notificaciones no leídas del usuario"""
        return Notificacion.objects.filter(
            destinatario=usuario,
            fecha_lectura__isnull=True
        ).order_by('-created_at')

    @staticmethod
    def obtener_solicitudes_pendientes(jefe):
        """Obtiene solicitudes pendientes de aprobar para un jefe"""
        return Notificacion.objects.filter(
            destinatario=jefe,
            tipo='solicitud',
            estado='pendiente'
        ).order_by('-created_at')

    @staticmethod
    def marcar_como_leida(notificacion_id, usuario):
        """Marca una notificación como leída"""
        try:
            notificacion = Notificacion.objects.get(
                id=notificacion_id,
                destinatario=usuario
            )
            notificacion.marcar_leida()
            return True
        except Notificacion.DoesNotExist:
            return False

    @staticmethod
    def marcar_todas_leidas(usuario):
        """Marca todas las notificaciones del usuario como leídas"""
        return Notificacion.objects.filter(
            destinatario=usuario,
            fecha_lectura__isnull=True
        ).update(
            fecha_lectura=timezone.now(),
            estado='leida'
        )

    # ========== Métodos privados ==========

    @staticmethod
    def _obtener_config(usuario):
        """Obtiene o crea configuración de notificaciones"""
        config, _ = ConfiguracionNotificaciones.objects.get_or_create(
            usuario=usuario,
            defaults={
                'recibir_solicitudes': True,
                'recibir_alertas': True,
                'recibir_confirmaciones': True,
                'recibir_nomina': True,
            }
        )
        return config

    @staticmethod
    def _usuario_acepta_tipo(config, tipo):
        """Verifica si el usuario acepta un tipo de notificación"""
        mapping = {
            'solicitud': config.recibir_solicitudes,
            'aprobacion': config.recibir_confirmaciones,
            'rechazo': config.recibir_confirmaciones,
            'alerta': config.recibir_alertas,
            'recordatorio': config.recibir_alertas,
            'confirmacion': config.recibir_confirmaciones,
            'nomina': config.recibir_nomina,
            'documento': config.recibir_alertas,
            'sistema': True,  # Siempre se envían
        }
        return mapping.get(tipo, True)

    @staticmethod
    def _enviar_email_notificacion(notificacion):
        """Envía email para una notificación"""
        try:
            # Mapear tipo a template
            template_mapping = {
                'solicitud': 'solicitud_aprobacion',
                'aprobacion': 'confirmacion_aprobacion',
                'rechazo': 'notificacion_rechazo',
                'alerta': 'alerta_vencimiento',
                'nomina': 'recibo_nomina',
            }

            template = template_mapping.get(notificacion.tipo, 'notificacion_general')

            resultado = EmailService.enviar_email(
                destinatario=notificacion.destinatario.email,
                asunto=notificacion.titulo,
                template_name=template,
                contexto={
                    'notificacion': notificacion,
                    'datos': notificacion.datos_extra,
                },
                prioridad=notificacion.prioridad
            )

            if resultado['exito']:
                notificacion.enviada_email = True
                notificacion.fecha_envio_email = timezone.now()
                notificacion.estado = 'enviada'
            else:
                notificacion.error_envio = resultado['mensaje']
                notificacion.estado = 'fallida'

            notificacion.save()
            return resultado

        except Exception as e:
            logger.error(f"Error enviando email para notificación {notificacion.id}: {str(e)}")
            notificacion.error_envio = str(e)
            notificacion.estado = 'fallida'
            notificacion.save()
            return {'exito': False, 'mensaje': str(e)}
