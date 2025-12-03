"""
Servicio de envío de emails
"""
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class EmailService:
    """Servicio centralizado para envío de emails"""

    @staticmethod
    def enviar_email(destinatario, asunto, template_name, contexto, prioridad='media'):
        """
        Envía un email usando un template HTML

        Args:
            destinatario: Email del destinatario
            asunto: Asunto del email
            template_name: Nombre del template (sin extensión)
            contexto: Diccionario con variables para el template
            prioridad: Nivel de prioridad (baja, media, alta, urgente)

        Returns:
            dict: {'exito': bool, 'mensaje': str}
        """
        try:
            # Agregar contexto común
            contexto.update({
                'frontend_url': getattr(settings, 'FRONTEND_URL', 'http://localhost:3000'),
                'empresa_nombre': 'Sistema RRHH',
                'prioridad': prioridad,
            })

            # Renderizar template HTML
            html_content = render_to_string(f'emails/{template_name}.html', contexto)
            text_content = strip_tags(html_content)

            # Configurar prioridad en headers
            headers = {}
            if prioridad == 'urgente':
                headers['X-Priority'] = '1'
                headers['X-MSMail-Priority'] = 'High'
            elif prioridad == 'alta':
                headers['X-Priority'] = '2'

            # Crear email con alternativas
            email = EmailMultiAlternatives(
                subject=asunto,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[destinatario] if isinstance(destinatario, str) else destinatario,
                headers=headers
            )
            email.attach_alternative(html_content, "text/html")

            # Enviar
            email.send(fail_silently=False)

            logger.info(f"Email enviado exitosamente a {destinatario}: {asunto}")
            return {'exito': True, 'mensaje': 'Email enviado correctamente'}

        except Exception as e:
            logger.error(f"Error enviando email a {destinatario}: {str(e)}")
            return {'exito': False, 'mensaje': str(e)}

    @staticmethod
    def enviar_solicitud_aprobacion(jefe, solicitante, tipo_solicitud, detalles, url_aprobar=None):
        """Envía notificación de solicitud pendiente al jefe"""
        return EmailService.enviar_email(
            destinatario=jefe.email,
            asunto=f'[Solicitud Pendiente] {tipo_solicitud} de {solicitante.get_full_name()}',
            template_name='solicitud_aprobacion',
            contexto={
                'jefe': jefe,
                'solicitante': solicitante,
                'tipo_solicitud': tipo_solicitud,
                'detalles': detalles,
                'url_aprobar': url_aprobar,
            },
            prioridad='alta'
        )

    @staticmethod
    def enviar_confirmacion_aprobacion(destinatario, tipo_solicitud, aprobador, comentarios=''):
        """Envía confirmación de solicitud aprobada"""
        return EmailService.enviar_email(
            destinatario=destinatario.email,
            asunto=f'[Aprobada] Tu solicitud de {tipo_solicitud}',
            template_name='confirmacion_aprobacion',
            contexto={
                'destinatario': destinatario,
                'tipo_solicitud': tipo_solicitud,
                'aprobador': aprobador,
                'comentarios': comentarios,
            },
            prioridad='media'
        )

    @staticmethod
    def enviar_notificacion_rechazo(destinatario, tipo_solicitud, rechazador, motivo):
        """Envía notificación de solicitud rechazada"""
        return EmailService.enviar_email(
            destinatario=destinatario.email,
            asunto=f'[Rechazada] Tu solicitud de {tipo_solicitud}',
            template_name='notificacion_rechazo',
            contexto={
                'destinatario': destinatario,
                'tipo_solicitud': tipo_solicitud,
                'rechazador': rechazador,
                'motivo': motivo,
            },
            prioridad='media'
        )

    @staticmethod
    def enviar_alerta_vencimiento(destinatario, tipo_documento, empleado, fecha_vencimiento, dias_restantes):
        """Envía alerta de documento próximo a vencer"""
        prioridad = 'urgente' if dias_restantes <= 3 else 'alta' if dias_restantes <= 7 else 'media'
        return EmailService.enviar_email(
            destinatario=destinatario.email,
            asunto=f'[Alerta] {tipo_documento} de {empleado.nombre_completo} vence en {dias_restantes} días',
            template_name='alerta_vencimiento',
            contexto={
                'destinatario': destinatario,
                'tipo_documento': tipo_documento,
                'empleado': empleado,
                'fecha_vencimiento': fecha_vencimiento,
                'dias_restantes': dias_restantes,
            },
            prioridad=prioridad
        )

    @staticmethod
    def enviar_recibo_nomina(empleado, periodo, url_descarga=None):
        """Envía notificación de recibo de nómina disponible"""
        return EmailService.enviar_email(
            destinatario=empleado.email_personal or empleado.email_corporativo,
            asunto=f'[Nómina] Tu recibo del periodo {periodo} está disponible',
            template_name='recibo_nomina',
            contexto={
                'empleado': empleado,
                'periodo': periodo,
                'url_descarga': url_descarga,
            },
            prioridad='media'
        )

    @staticmethod
    def enviar_bienvenida(empleado, credenciales=None):
        """Envía email de bienvenida a nuevo empleado"""
        return EmailService.enviar_email(
            destinatario=empleado.email_personal or empleado.email_corporativo,
            asunto=f'Bienvenido/a a {empleado.empresa.nombre if empleado.empresa else "la empresa"}',
            template_name='bienvenida',
            contexto={
                'empleado': empleado,
                'credenciales': credenciales,
            },
            prioridad='media'
        )
