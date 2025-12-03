"""
Acciones de IA para gestion de usuarios y perfil
"""
from typing import Dict
from django.db.models import Q


def registrar_acciones():
    """Registra todas las acciones de usuarios en el registry"""
    from apps.chat.acciones_registry import registrar_accion
    from .services import UsuarioService
    from .models import Usuario, SolicitudCambioDatos

    # ============================================================
    # ACCION 60: Ver mi perfil
    # ============================================================
    def ver_mi_perfil(usuario, params: Dict, contexto: Dict) -> Dict:
        """Obtiene el perfil del usuario actual"""
        perfil = UsuarioService.obtener_mi_perfil(usuario)

        info = f"**Tu Perfil**\n\n"
        info += f"- Email: {perfil['email']}\n"
        info += f"- Nombre: {perfil['nombre_completo']}\n"
        info += f"- Rol: {perfil['rol_display']}\n"
        info += f"- Notificaciones email: {'Si' if perfil['notificaciones_email'] else 'No'}\n"
        info += f"- Tema oscuro: {'Si' if perfil['tema_oscuro'] else 'No'}\n"

        if perfil.get('empleado'):
            emp = perfil['empleado']
            info += f"\n**Datos de Empleado:**\n"
            info += f"- Empresa: {emp['empresa']}\n"
            info += f"- Puesto: {emp['puesto']}\n"
            info += f"- Departamento: {emp['departamento']}\n"
            info += f"- Fecha ingreso: {emp['fecha_ingreso']}\n"

        if perfil.get('empresas'):
            info += f"\n**Empresas asignadas:** {len(perfil['empresas'])}\n"
            for e in perfil['empresas'][:5]:
                info += f"- {e['nombre']}\n"

        return {
            'exito': True,
            'mensaje': info,
            'datos': perfil
        }

    registrar_accion(
        nombre='ver_mi_perfil',
        descripcion='Muestra informacion del perfil del usuario actual',
        permisos=['es_admin', 'es_rrhh', 'es_jefe', 'es_empleado'],
        parametros={},
        ejemplo='Muestrame mi perfil',
        funcion=ver_mi_perfil
    )

    # ============================================================
    # ACCION 61: Actualizar mi perfil
    # ============================================================
    def actualizar_mi_perfil(usuario, params: Dict, contexto: Dict) -> Dict:
        """Actualiza el perfil del usuario"""
        datos = {}
        if 'nombre' in params:
            datos['first_name'] = params['nombre']
        if 'apellido' in params:
            datos['last_name'] = params['apellido']
        if 'notificaciones_email' in params:
            datos['notificaciones_email'] = params['notificaciones_email']
        if 'tema_oscuro' in params:
            datos['tema_oscuro'] = params['tema_oscuro']

        if not datos:
            return {
                'exito': False,
                'mensaje': 'No especificaste que datos actualizar. Puedes cambiar: nombre, apellido, notificaciones_email, tema_oscuro'
            }

        resultado = UsuarioService.actualizar_perfil(usuario, datos)

        cambios_texto = []
        for campo, vals in resultado.get('cambios', {}).items():
            cambios_texto.append(f"- {campo}: {vals['anterior']} -> {vals['nuevo']}")

        return {
            'exito': True,
            'mensaje': f"Perfil actualizado:\n" + "\n".join(cambios_texto) if cambios_texto else "No hubo cambios",
            'datos': resultado
        }

    registrar_accion(
        nombre='actualizar_mi_perfil',
        descripcion='Actualiza datos del perfil del usuario',
        permisos=['es_admin', 'es_rrhh', 'es_jefe', 'es_empleado'],
        parametros={
            'nombre': '(Opcional) Nombre',
            'apellido': '(Opcional) Apellido',
            'notificaciones_email': '(Opcional) true/false',
            'tema_oscuro': '(Opcional) true/false',
        },
        ejemplo='Actualiza mi nombre a Juan',
        funcion=actualizar_mi_perfil
    )

    # ============================================================
    # ACCION 62: Cambiar mi password
    # ============================================================
    def cambiar_mi_password(usuario, params: Dict, contexto: Dict) -> Dict:
        """Cambia el password del usuario"""
        password_actual = params.get('password_actual')
        password_nuevo = params.get('password_nuevo')

        if not password_actual or not password_nuevo:
            return {
                'exito': False,
                'mensaje': 'Debes proporcionar el password actual y el nuevo'
            }

        if len(password_nuevo) < 8:
            return {
                'exito': False,
                'mensaje': 'El nuevo password debe tener al menos 8 caracteres'
            }

        resultado = UsuarioService.cambiar_password(usuario, password_actual, password_nuevo)
        return resultado

    registrar_accion(
        nombre='cambiar_mi_password',
        descripcion='Cambia el password del usuario actual',
        permisos=['es_admin', 'es_rrhh', 'es_jefe', 'es_empleado'],
        parametros={
            'password_actual': 'Password actual',
            'password_nuevo': 'Nuevo password (min 8 caracteres)',
        },
        ejemplo='Cambia mi password',
        funcion=cambiar_mi_password
    )

    # ============================================================
    # ACCION 63: Solicitar cambio de datos
    # ============================================================
    def solicitar_cambio_datos(usuario, params: Dict, contexto: Dict) -> Dict:
        """Crea una solicitud de cambio de datos sensibles"""
        if not usuario.empleado:
            return {
                'exito': False,
                'mensaje': 'No tienes un perfil de empleado vinculado'
            }

        tipo = params.get('tipo', '').lower()
        valor_nuevo = params.get('valor_nuevo', '')
        justificacion = params.get('justificacion', '')

        tipos_validos = [t[0] for t in SolicitudCambioDatos.TipoCambio.choices]
        if tipo not in tipos_validos:
            return {
                'exito': False,
                'mensaje': f'Tipo invalido. Opciones: {", ".join(tipos_validos)}'
            }

        mapeo_campos = {
            'rfc': 'rfc',
            'curp': 'curp',
            'nss': 'numero_seguro_social',
            'cuenta_bancaria': 'cuenta_bancaria',
            'direccion': 'direccion',
            'telefono': 'telefono',
            'email_personal': 'email_personal',
            'contacto_emergencia': 'contacto_emergencia',
        }

        campo = mapeo_campos.get(tipo, tipo)
        datos_nuevos = {campo: valor_nuevo}

        solicitud = UsuarioService.crear_solicitud_cambio(
            empleado=usuario.empleado,
            tipo_cambio=tipo,
            datos_nuevos=datos_nuevos,
            justificacion=justificacion
        )

        return {
            'exito': True,
            'mensaje': f'Solicitud de cambio de {solicitud.get_tipo_cambio_display()} creada. Sera revisada por RRHH.',
            'datos': {
                'id': solicitud.id,
                'tipo': solicitud.tipo_cambio,
                'estado': solicitud.estado
            }
        }

    registrar_accion(
        nombre='solicitar_cambio_datos',
        descripcion='Solicita un cambio de datos personales sensibles',
        permisos=['es_empleado'],
        parametros={
            'tipo': 'Tipo: rfc, curp, nss, cuenta_bancaria, direccion, telefono, email_personal, contacto_emergencia',
            'valor_nuevo': 'Nuevo valor',
            'justificacion': '(Opcional) Motivo del cambio',
        },
        ejemplo='Solicita cambiar mi RFC a XAXX010101000',
        funcion=solicitar_cambio_datos
    )

    # ============================================================
    # ACCION 64: Mis solicitudes de cambio
    # ============================================================
    def mis_solicitudes_cambio(usuario, params: Dict, contexto: Dict) -> Dict:
        """Lista las solicitudes de cambio del usuario"""
        estado = params.get('estado')

        if usuario.empleado:
            solicitudes = SolicitudCambioDatos.objects.filter(
                empleado=usuario.empleado
            ).select_related('revisado_por').order_by('-created_at')

            if estado:
                solicitudes = solicitudes.filter(estado=estado)

            solicitudes = list(solicitudes[:20])
        else:
            solicitudes = []

        if not solicitudes:
            return {
                'exito': True,
                'mensaje': 'No tienes solicitudes de cambio de datos',
                'datos': []
            }

        texto = f"**Tus Solicitudes de Cambio ({len(solicitudes)})**\n\n"
        for sol in solicitudes:
            estado_txt = {'pendiente': '(Pendiente)', 'aprobada': '(OK)', 'rechazada': '(X)'}.get(sol.estado, '')
            texto += f"- {sol.get_tipo_cambio_display()} {estado_txt}\n"
            texto += f"  Fecha: {sol.created_at.strftime('%d/%m/%Y')}\n"
            if sol.comentario_revision:
                texto += f"  Comentario: {sol.comentario_revision[:50]}\n"
            texto += "\n"

        return {
            'exito': True,
            'mensaje': texto,
            'datos': [{'id': s.id, 'tipo': s.tipo_cambio, 'estado': s.estado} for s in solicitudes]
        }

    registrar_accion(
        nombre='mis_solicitudes_cambio',
        descripcion='Lista mis solicitudes de cambio de datos',
        permisos=['es_empleado'],
        parametros={
            'estado': '(Opcional) Filtrar: pendiente, aprobada, rechazada',
        },
        ejemplo='Muestrame mis solicitudes de cambio',
        funcion=mis_solicitudes_cambio
    )

    # ============================================================
    # ACCION 65: Listar solicitudes de cambio (RRHH)
    # ============================================================
    def listar_solicitudes_cambio(usuario, params: Dict, contexto: Dict) -> Dict:
        """Lista solicitudes de cambio para revision de RRHH"""
        solicitudes = UsuarioService.listar_solicitudes_cambio(
            usuario=usuario,
            estado=params.get('estado'),
            empleado_id=params.get('empleado_id')
        )

        if not solicitudes:
            return {
                'exito': True,
                'mensaje': 'No hay solicitudes de cambio',
                'datos': []
            }

        texto = f"**Solicitudes de Cambio ({len(solicitudes)})**\n\n"
        for sol in solicitudes:
            texto += f"**{sol.empleado.nombre_completo}** - {sol.get_tipo_cambio_display()}\n"
            texto += f"  Estado: {sol.get_estado_display()}\n"
            texto += f"  Valor actual: {sol.datos_actuales}\n"
            texto += f"  Valor nuevo: {sol.datos_nuevos}\n"
            texto += f"  Fecha: {sol.created_at.strftime('%d/%m/%Y %H:%M')}\n\n"

        return {
            'exito': True,
            'mensaje': texto,
            'datos': [
                {
                    'id': s.id,
                    'empleado': s.empleado.nombre_completo,
                    'tipo': s.tipo_cambio,
                    'estado': s.estado,
                }
                for s in solicitudes
            ]
        }

    registrar_accion(
        nombre='listar_solicitudes_cambio',
        descripcion='Lista solicitudes de cambio de datos pendientes de revision',
        permisos=['es_admin', 'es_rrhh'],
        parametros={
            'estado': '(Opcional) Filtrar: pendiente, aprobada, rechazada',
            'empleado_id': '(Opcional) Filtrar por empleado',
        },
        ejemplo='Muestrame las solicitudes de cambio pendientes',
        funcion=listar_solicitudes_cambio
    )

    # ============================================================
    # ACCION 66: Aprobar cambio de datos
    # ============================================================
    def aprobar_cambio_datos(usuario, params: Dict, contexto: Dict) -> Dict:
        """Aprueba una solicitud de cambio de datos"""
        solicitud_id = params.get('solicitud_id')
        if not solicitud_id:
            return {
                'exito': False,
                'mensaje': 'Debes indicar el ID de la solicitud'
            }

        try:
            solicitud = SolicitudCambioDatos.objects.select_related('empleado').get(id=solicitud_id)
        except SolicitudCambioDatos.DoesNotExist:
            return {
                'exito': False,
                'mensaje': 'Solicitud no encontrada'
            }

        if not usuario.es_admin:
            if not usuario.tiene_acceso_empresa(solicitud.empleado.empresa_id):
                return {
                    'exito': False,
                    'mensaje': 'No tienes acceso a este empleado'
                }

        resultado = UsuarioService.aprobar_solicitud_cambio(
            solicitud=solicitud,
            usuario_aprobador=usuario,
            comentario=params.get('comentario', '')
        )

        if resultado['exito']:
            return {
                'exito': True,
                'mensaje': f"Solicitud aprobada. Se actualizo {solicitud.get_tipo_cambio_display()} de {solicitud.empleado.nombre_completo}"
            }

        return resultado

    registrar_accion(
        nombre='aprobar_cambio_datos',
        descripcion='Aprueba una solicitud de cambio de datos',
        permisos=['es_admin', 'es_rrhh'],
        parametros={
            'solicitud_id': 'ID de la solicitud',
            'comentario': '(Opcional) Comentario de aprobacion',
        },
        ejemplo='Aprueba la solicitud de cambio 5',
        funcion=aprobar_cambio_datos
    )

    # ============================================================
    # ACCION 67: Rechazar cambio de datos
    # ============================================================
    def rechazar_cambio_datos(usuario, params: Dict, contexto: Dict) -> Dict:
        """Rechaza una solicitud de cambio de datos"""
        solicitud_id = params.get('solicitud_id')
        motivo = params.get('motivo', '')

        if not solicitud_id:
            return {
                'exito': False,
                'mensaje': 'Debes indicar el ID de la solicitud'
            }

        if not motivo:
            return {
                'exito': False,
                'mensaje': 'Debes indicar el motivo del rechazo'
            }

        try:
            solicitud = SolicitudCambioDatos.objects.select_related('empleado').get(id=solicitud_id)
        except SolicitudCambioDatos.DoesNotExist:
            return {
                'exito': False,
                'mensaje': 'Solicitud no encontrada'
            }

        if not usuario.es_admin:
            if not usuario.tiene_acceso_empresa(solicitud.empleado.empresa_id):
                return {
                    'exito': False,
                    'mensaje': 'No tienes acceso a este empleado'
                }

        resultado = UsuarioService.rechazar_solicitud_cambio(
            solicitud=solicitud,
            usuario_rechazador=usuario,
            comentario=motivo
        )

        if resultado['exito']:
            return {
                'exito': True,
                'mensaje': f"Solicitud rechazada. Se notifico a {solicitud.empleado.nombre_completo}"
            }

        return resultado

    registrar_accion(
        nombre='rechazar_cambio_datos',
        descripcion='Rechaza una solicitud de cambio de datos',
        permisos=['es_admin', 'es_rrhh'],
        parametros={
            'solicitud_id': 'ID de la solicitud',
            'motivo': 'Motivo del rechazo',
        },
        ejemplo='Rechaza la solicitud 5 porque el RFC es invalido',
        funcion=rechazar_cambio_datos
    )

    # ============================================================
    # ACCION 68: Listar usuarios
    # ============================================================
    def listar_usuarios(usuario, params: Dict, contexto: Dict) -> Dict:
        """Lista usuarios del sistema"""
        queryset = Usuario.objects.all()

        if params.get('rol'):
            queryset = queryset.filter(rol=params['rol'])

        if params.get('activo') is not None:
            queryset = queryset.filter(is_active=params['activo'])

        if params.get('busqueda'):
            busqueda = params['busqueda']
            queryset = queryset.filter(
                Q(email__icontains=busqueda) |
                Q(first_name__icontains=busqueda) |
                Q(last_name__icontains=busqueda)
            )

        usuarios = list(queryset.order_by('-date_joined')[:50])

        if not usuarios:
            return {
                'exito': True,
                'mensaje': 'No se encontraron usuarios',
                'datos': []
            }

        texto = f"**Usuarios ({len(usuarios)})**\n\n"
        for u in usuarios:
            estado = "(Activo)" if u.is_active else "(Inactivo)"
            texto += f"- {u.email} - {u.get_rol_display()} {estado}\n"

        return {
            'exito': True,
            'mensaje': texto,
            'datos': [
                {
                    'id': u.id,
                    'email': u.email,
                    'nombre': u.get_full_name(),
                    'rol': u.rol,
                    'activo': u.is_active
                }
                for u in usuarios
            ]
        }

    registrar_accion(
        nombre='listar_usuarios',
        descripcion='Lista usuarios del sistema',
        permisos=['es_admin'],
        parametros={
            'rol': '(Opcional) Filtrar: admin, empleador, empleado',
            'activo': '(Opcional) true/false',
            'busqueda': '(Opcional) Buscar por email o nombre',
        },
        ejemplo='Muestrame los usuarios del sistema',
        funcion=listar_usuarios
    )

    # ============================================================
    # ACCION 69: Crear usuario
    # ============================================================
    def crear_usuario(usuario, params: Dict, contexto: Dict) -> Dict:
        """Crea un nuevo usuario"""
        email = params.get('email', '').strip().lower()
        password = params.get('password', '')

        if not email or not password:
            return {
                'exito': False,
                'mensaje': 'Email y password son requeridos'
            }

        if Usuario.objects.filter(email=email).exists():
            return {
                'exito': False,
                'mensaje': f'Ya existe un usuario con email {email}'
            }

        try:
            nuevo_usuario = UsuarioService.crear_usuario(
                email=email,
                password=password,
                rol=params.get('rol', 'empleado'),
                first_name=params.get('nombre', ''),
                last_name=params.get('apellido', ''),
                activar=params.get('activar', False),
                enviar_email=not params.get('activar', False)
            )

            estado = "activado" if nuevo_usuario.is_active else "pendiente de activacion (email enviado)"
            return {
                'exito': True,
                'mensaje': f"Usuario {email} creado. Estado: {estado}",
                'datos': {
                    'id': nuevo_usuario.id,
                    'email': nuevo_usuario.email,
                    'rol': nuevo_usuario.rol,
                    'activo': nuevo_usuario.is_active
                }
            }
        except Exception as e:
            return {
                'exito': False,
                'mensaje': f'Error creando usuario: {str(e)}'
            }

    registrar_accion(
        nombre='crear_usuario',
        descripcion='Crea un nuevo usuario en el sistema',
        permisos=['es_admin'],
        parametros={
            'email': 'Email del usuario',
            'password': 'Password inicial',
            'rol': '(Opcional) admin, empleador, empleado',
            'nombre': '(Opcional) Nombre',
            'apellido': '(Opcional) Apellido',
            'activar': '(Opcional) true para activar inmediatamente',
        },
        ejemplo='Crea un usuario juan@empresa.com con password Temporal123',
        funcion=crear_usuario
    )

    # ============================================================
    # ACCION 70: Activar/Desactivar usuario
    # ============================================================
    def activar_usuario(usuario, params: Dict, contexto: Dict) -> Dict:
        """Activa o desactiva un usuario"""
        usuario_id = params.get('usuario_id')
        activo = params.get('activo', True)

        try:
            usuario_target = Usuario.objects.get(id=usuario_id)
        except Usuario.DoesNotExist:
            return {
                'exito': False,
                'mensaje': 'Usuario no encontrado'
            }

        if usuario_target.id == usuario.id:
            return {
                'exito': False,
                'mensaje': 'No puedes desactivar tu propia cuenta'
            }

        usuario_target.is_active = activo
        usuario_target.save(update_fields=['is_active'])

        estado = "activado" if activo else "desactivado"
        return {
            'exito': True,
            'mensaje': f"Usuario {usuario_target.email} {estado}"
        }

    registrar_accion(
        nombre='activar_usuario',
        descripcion='Activa o desactiva un usuario',
        permisos=['es_admin'],
        parametros={
            'usuario_id': 'ID del usuario',
            'activo': 'true para activar, false para desactivar',
        },
        ejemplo='Desactiva el usuario 5',
        funcion=activar_usuario
    )

    # ============================================================
    # ACCION 71: Reenviar activacion
    # ============================================================
    def reenviar_activacion(usuario, params: Dict, contexto: Dict) -> Dict:
        """Reenvia email de activacion"""
        email = params.get('email', '').strip().lower()

        if not email:
            return {
                'exito': False,
                'mensaje': 'Debes indicar el email'
            }

        resultado = UsuarioService.reenviar_activacion(email)
        return resultado

    registrar_accion(
        nombre='reenviar_activacion',
        descripcion='Reenvia el email de activacion a un usuario',
        permisos=['es_admin'],
        parametros={
            'email': 'Email del usuario',
        },
        ejemplo='Reenvia el email de activacion a juan@empresa.com',
        funcion=reenviar_activacion
    )

    print("  - 12 acciones de usuarios registradas")
