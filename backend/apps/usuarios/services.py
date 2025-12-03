"""
Servicio para gestion de usuarios
"""
from typing import Optional, Dict, List
from django.utils import timezone
from django.contrib.auth.hashers import make_password
from django.db import transaction

from .models import Usuario, TokenUsuario, SolicitudCambioDatos
from apps.notificaciones.services import NotificacionService


class UsuarioService:
    """Servicio para operaciones de gestion de usuarios"""

    @classmethod
    def crear_usuario(
        cls,
        email: str,
        password: str,
        rol: str = 'empleado',
        enviar_email: bool = True,
        activar: bool = False,
        **kwargs
    ) -> Usuario:
        """
        Crea un nuevo usuario y envia email de activacion
        """
        with transaction.atomic():
            # Crear usuario
            usuario = Usuario.objects.create(
                email=email,
                username=email,
                password=make_password(password),
                rol=rol,
                is_active=activar,
                **kwargs
            )

            # Si no esta activo, crear token de activacion
            if not activar and enviar_email:
                token = TokenUsuario.crear_token_activacion(usuario)
                cls._enviar_email_activacion(usuario, token)

            return usuario

    @classmethod
    def activar_cuenta(cls, token: str) -> Dict:
        """
        Activa una cuenta de usuario usando el token
        """
        try:
            token_obj = TokenUsuario.objects.get(
                token=token,
                tipo=TokenUsuario.TipoToken.ACTIVACION
            )
        except TokenUsuario.DoesNotExist:
            return {
                'exito': False,
                'mensaje': 'Token invalido o no encontrado'
            }

        if not token_obj.es_valido:
            return {
                'exito': False,
                'mensaje': 'El token ha expirado o ya fue utilizado'
            }

        # Activar usuario
        usuario = token_obj.usuario
        usuario.is_active = True
        usuario.save(update_fields=['is_active'])

        # Marcar token como usado
        token_obj.usar()

        return {
            'exito': True,
            'mensaje': 'Cuenta activada correctamente',
            'usuario': usuario
        }

    @classmethod
    def solicitar_reset_password(cls, email: str) -> Dict:
        """
        Inicia el proceso de reset de password
        """
        try:
            usuario = Usuario.objects.get(email=email, is_active=True)
        except Usuario.DoesNotExist:
            # Por seguridad, no revelamos si el email existe
            return {
                'exito': True,
                'mensaje': 'Si el email existe, recibiras instrucciones para restablecer tu password'
            }

        # Crear token de reset
        token = TokenUsuario.crear_token_reset(usuario)

        # Enviar email
        cls._enviar_email_reset(usuario, token)

        return {
            'exito': True,
            'mensaje': 'Si el email existe, recibiras instrucciones para restablecer tu password'
        }

    @classmethod
    def resetear_password(cls, token: str, nuevo_password: str) -> Dict:
        """
        Resetea el password usando el token
        """
        try:
            token_obj = TokenUsuario.objects.get(
                token=token,
                tipo=TokenUsuario.TipoToken.RESET_PASSWORD
            )
        except TokenUsuario.DoesNotExist:
            return {
                'exito': False,
                'mensaje': 'Token invalido o no encontrado'
            }

        if not token_obj.es_valido:
            return {
                'exito': False,
                'mensaje': 'El token ha expirado o ya fue utilizado'
            }

        # Cambiar password
        usuario = token_obj.usuario
        usuario.password = make_password(nuevo_password)
        usuario.save(update_fields=['password'])

        # Marcar token como usado
        token_obj.usar()

        # Enviar notificacion de password cambiado
        cls._enviar_email_password_cambiado(usuario)

        return {
            'exito': True,
            'mensaje': 'Password actualizado correctamente'
        }

    @classmethod
    def cambiar_password(cls, usuario: Usuario, password_actual: str, nuevo_password: str) -> Dict:
        """
        Cambia el password del usuario autenticado
        """
        if not usuario.check_password(password_actual):
            return {
                'exito': False,
                'mensaje': 'El password actual es incorrecto'
            }

        usuario.password = make_password(nuevo_password)
        usuario.save(update_fields=['password'])

        # Enviar notificacion
        cls._enviar_email_password_cambiado(usuario)

        return {
            'exito': True,
            'mensaje': 'Password actualizado correctamente'
        }

    @classmethod
    def actualizar_perfil(cls, usuario: Usuario, datos: Dict) -> Dict:
        """
        Actualiza datos del perfil del usuario
        """
        campos_permitidos = [
            'first_name', 'last_name',
            'notificaciones_email', 'notificaciones_push', 'tema_oscuro'
        ]

        cambios = {}
        for campo in campos_permitidos:
            if campo in datos:
                valor_anterior = getattr(usuario, campo)
                setattr(usuario, campo, datos[campo])
                cambios[campo] = {
                    'anterior': valor_anterior,
                    'nuevo': datos[campo]
                }

        if cambios:
            usuario.save()

        return {
            'exito': True,
            'mensaje': 'Perfil actualizado',
            'cambios': cambios
        }

    @classmethod
    def reenviar_activacion(cls, email: str) -> Dict:
        """
        Reenvia el email de activacion
        """
        try:
            usuario = Usuario.objects.get(email=email, is_active=False)
        except Usuario.DoesNotExist:
            return {
                'exito': False,
                'mensaje': 'Usuario no encontrado o ya esta activo'
            }

        # Crear nuevo token
        token = TokenUsuario.crear_token_activacion(usuario)

        # Enviar email
        cls._enviar_email_activacion(usuario, token)

        return {
            'exito': True,
            'mensaje': 'Email de activacion reenviado'
        }

    @classmethod
    def crear_solicitud_cambio(
        cls,
        empleado,
        tipo_cambio: str,
        datos_nuevos: Dict,
        justificacion: str = '',
        documento=None
    ) -> SolicitudCambioDatos:
        """
        Crea una solicitud de cambio de datos sensibles
        """
        # Obtener datos actuales
        datos_actuales = {}
        for campo in datos_nuevos.keys():
            if hasattr(empleado, campo):
                valor = getattr(empleado, campo)
                datos_actuales[campo] = str(valor) if valor else ''

        solicitud = SolicitudCambioDatos.objects.create(
            empleado=empleado,
            tipo_cambio=tipo_cambio,
            datos_actuales=datos_actuales,
            datos_nuevos=datos_nuevos,
            justificacion=justificacion,
            documento_soporte=documento
        )

        # Notificar a RRHH
        cls._notificar_nueva_solicitud_cambio(solicitud)

        return solicitud

    @classmethod
    def aprobar_solicitud_cambio(
        cls,
        solicitud: SolicitudCambioDatos,
        usuario_aprobador: Usuario,
        comentario: str = ''
    ) -> Dict:
        """
        Aprueba una solicitud de cambio de datos
        """
        if solicitud.estado != SolicitudCambioDatos.Estado.PENDIENTE:
            return {
                'exito': False,
                'mensaje': 'La solicitud ya fue procesada'
            }

        solicitud.aprobar(usuario_aprobador, comentario)

        # Notificar al empleado
        cls._notificar_solicitud_procesada(solicitud, aprobada=True)

        return {
            'exito': True,
            'mensaje': 'Solicitud aprobada y cambios aplicados'
        }

    @classmethod
    def rechazar_solicitud_cambio(
        cls,
        solicitud: SolicitudCambioDatos,
        usuario_rechazador: Usuario,
        comentario: str = ''
    ) -> Dict:
        """
        Rechaza una solicitud de cambio de datos
        """
        if solicitud.estado != SolicitudCambioDatos.Estado.PENDIENTE:
            return {
                'exito': False,
                'mensaje': 'La solicitud ya fue procesada'
            }

        solicitud.rechazar(usuario_rechazador, comentario)

        # Notificar al empleado
        cls._notificar_solicitud_procesada(solicitud, aprobada=False)

        return {
            'exito': True,
            'mensaje': 'Solicitud rechazada'
        }

    @classmethod
    def listar_solicitudes_cambio(
        cls,
        usuario: Usuario,
        estado: Optional[str] = None,
        empleado_id: Optional[int] = None
    ) -> List[SolicitudCambioDatos]:
        """
        Lista solicitudes de cambio segun permisos del usuario
        """
        queryset = SolicitudCambioDatos.objects.select_related('empleado', 'revisado_por')

        # Filtrar por permisos
        if usuario.es_empleado and usuario.empleado:
            queryset = queryset.filter(empleado=usuario.empleado)
        elif usuario.es_empleador:
            empresas_ids = usuario.empresas.values_list('id', flat=True)
            queryset = queryset.filter(empleado__empresa_id__in=empresas_ids)
        # Admin ve todas

        if estado:
            queryset = queryset.filter(estado=estado)

        if empleado_id:
            queryset = queryset.filter(empleado_id=empleado_id)

        return list(queryset.order_by('-created_at')[:50])

    @classmethod
    def obtener_mi_perfil(cls, usuario: Usuario) -> Dict:
        """
        Obtiene datos del perfil del usuario
        """
        perfil = {
            'id': usuario.id,
            'email': usuario.email,
            'nombre': usuario.first_name,
            'apellido': usuario.last_name,
            'nombre_completo': usuario.get_full_name() or usuario.email,
            'rol': usuario.rol,
            'rol_display': usuario.get_rol_display(),
            'notificaciones_email': usuario.notificaciones_email,
            'notificaciones_push': usuario.notificaciones_push,
            'tema_oscuro': usuario.tema_oscuro,
            'ultimo_acceso': usuario.last_login.isoformat() if usuario.last_login else None,
            'fecha_registro': usuario.date_joined.isoformat() if usuario.date_joined else None,
        }

        # Si tiene empleado vinculado
        if usuario.empleado:
            emp = usuario.empleado
            perfil['empleado'] = {
                'id': emp.id,
                'nombre_completo': emp.nombre_completo,
                'puesto': emp.puesto,
                'departamento': emp.departamento,
                'empresa': emp.empresa.razon_social if emp.empresa else None,
                'fecha_ingreso': emp.fecha_ingreso.isoformat() if emp.fecha_ingreso else None,
            }

        # Empresas asignadas (para empleador)
        if usuario.es_empleador:
            perfil['empresas'] = [
                {'id': e.id, 'nombre': e.razon_social}
                for e in usuario.empresas.filter(activa=True)
            ]

        return perfil

    # ============ METODOS PRIVADOS PARA EMAILS ============

    @classmethod
    def _enviar_email_activacion(cls, usuario: Usuario, token: TokenUsuario):
        """Envia email de activacion de cuenta"""
        try:
            from django.conf import settings
            url_activacion = f"{getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')}/activar/{token.token}"

            NotificacionService.enviar_email(
                destinatario=usuario.email,
                asunto='Activa tu cuenta - Sistema RRHH',
                template='usuarios/activacion.html',
                contexto={
                    'usuario': usuario,
                    'url_activacion': url_activacion,
                    'horas_valido': 48
                }
            )
        except Exception as e:
            print(f"Error enviando email de activacion: {e}")

    @classmethod
    def _enviar_email_reset(cls, usuario: Usuario, token: TokenUsuario):
        """Envia email de reset de password"""
        try:
            from django.conf import settings
            url_reset = f"{getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')}/reset-password/{token.token}"

            NotificacionService.enviar_email(
                destinatario=usuario.email,
                asunto='Restablecer Password - Sistema RRHH',
                template='usuarios/reset_password.html',
                contexto={
                    'usuario': usuario,
                    'url_reset': url_reset,
                    'horas_valido': 24
                }
            )
        except Exception as e:
            print(f"Error enviando email de reset: {e}")

    @classmethod
    def _enviar_email_password_cambiado(cls, usuario: Usuario):
        """Notifica que el password fue cambiado"""
        try:
            NotificacionService.enviar_email(
                destinatario=usuario.email,
                asunto='Tu password ha sido actualizado - Sistema RRHH',
                template='usuarios/password_cambiado.html',
                contexto={
                    'usuario': usuario,
                    'fecha': timezone.now()
                }
            )
        except Exception as e:
            print(f"Error enviando notificacion de password: {e}")

    @classmethod
    def _notificar_nueva_solicitud_cambio(cls, solicitud: SolicitudCambioDatos):
        """Notifica a RRHH de nueva solicitud de cambio"""
        try:
            empleado = solicitud.empleado
            if empleado.empresa:
                # Obtener usuarios RRHH de la empresa
                usuarios_rrhh = Usuario.objects.filter(
                    rol__in=['admin', 'empleador'],
                    empresas=empleado.empresa,
                    is_active=True
                )

                for usuario in usuarios_rrhh:
                    NotificacionService.enviar_notificacion(
                        usuario=usuario,
                        tipo='solicitud',
                        titulo='Nueva solicitud de cambio de datos',
                        mensaje=f'{empleado.nombre_completo} solicita cambio de {solicitud.get_tipo_cambio_display()}',
                        url=f'/solicitudes-cambio/{solicitud.id}'
                    )
        except Exception as e:
            print(f"Error notificando solicitud: {e}")

    @classmethod
    def _notificar_solicitud_procesada(cls, solicitud: SolicitudCambioDatos, aprobada: bool):
        """Notifica al empleado que su solicitud fue procesada"""
        try:
            empleado = solicitud.empleado
            if hasattr(empleado, 'usuario') and empleado.usuario:
                estado = 'aprobada' if aprobada else 'rechazada'
                NotificacionService.enviar_notificacion(
                    usuario=empleado.usuario,
                    tipo='sistema',
                    titulo=f'Solicitud {estado}',
                    mensaje=f'Tu solicitud de cambio de {solicitud.get_tipo_cambio_display()} ha sido {estado}',
                    url=f'/mis-solicitudes/{solicitud.id}'
                )
        except Exception as e:
            print(f"Error notificando: {e}")
