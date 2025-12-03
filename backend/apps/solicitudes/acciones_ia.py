"""
Acciones de IA para el módulo de solicitudes
"""
from typing import Dict


def registrar_acciones():
    """Registra todas las acciones de solicitudes"""
    from apps.chat.acciones_registry import registrar_accion

    # ============================================================
    # ACCIÓN 46: Crear solicitud genérica
    # ============================================================
    registrar_accion(
        nombre='crear_solicitud',
        descripcion='Crea una nueva solicitud para aprobacion del jefe',
        permisos=['es_admin', 'es_rrhh', 'es_jefe', 'es_empleado'],
        parametros={
            'tipo': 'Tipo: vacaciones, permiso, kpi, salario, otro',
            'titulo': 'Titulo de la solicitud',
            'descripcion': '(Opcional) Descripcion detallada',
            'empleado_id': 'ID del empleado solicitante',
            'prioridad': '(Opcional) baja, media, alta, urgente',
        },
        ejemplo='Crear solicitud de permiso para manana',
        funcion=crear_solicitud,
        confirmacion_requerida=True
    )

    # ============================================================
    # ACCIÓN 47: Aprobar solicitud
    # ============================================================
    registrar_accion(
        nombre='aprobar_solicitud',
        descripcion='Aprueba una solicitud pendiente',
        permisos=['es_admin', 'es_rrhh', 'es_jefe'],
        parametros={
            'solicitud_id': 'ID de la solicitud a aprobar',
            'comentarios': '(Opcional) Comentarios de aprobacion',
        },
        ejemplo='Aprobar la solicitud de vacaciones',
        funcion=aprobar_solicitud,
        confirmacion_requerida=True
    )

    # ============================================================
    # ACCIÓN 48: Rechazar solicitud
    # ============================================================
    registrar_accion(
        nombre='rechazar_solicitud',
        descripcion='Rechaza una solicitud pendiente',
        permisos=['es_admin', 'es_rrhh', 'es_jefe'],
        parametros={
            'solicitud_id': 'ID de la solicitud a rechazar',
            'motivo': 'Motivo del rechazo (requerido)',
        },
        ejemplo='Rechazar solicitud por falta de cobertura',
        funcion=rechazar_solicitud,
        confirmacion_requerida=True
    )

    # ============================================================
    # ACCIÓN 49: Ver mis solicitudes
    # ============================================================
    registrar_accion(
        nombre='ver_mis_solicitudes',
        descripcion='Muestra las solicitudes realizadas por un empleado',
        permisos=['es_admin', 'es_rrhh', 'es_jefe', 'es_empleado'],
        parametros={
            'empleado_id': '(Opcional) ID del empleado, si no se especifica usa el actual',
            'estado': '(Opcional) Filtrar por estado: pendiente, aprobada, rechazada',
        },
        ejemplo='Ver mis solicitudes pendientes',
        funcion=ver_mis_solicitudes
    )


# ========== Funciones de las acciones ==========

def crear_solicitud(usuario, parametros: Dict, contexto: Dict) -> Dict:
    """Crea una nueva solicitud para aprobacion del jefe"""
    from apps.empleados.models import Empleado
    from .services import SolicitudService

    empleado_id = parametros.get('empleado_id')
    tipo = parametros.get('tipo', 'otro')
    titulo = parametros.get('titulo', 'Nueva solicitud')

    if not empleado_id:
        return {'success': False, 'error': 'Debes especificar el empleado'}

    try:
        empleado = Empleado.objects.get(id=empleado_id)
    except Empleado.DoesNotExist:
        return {'success': False, 'error': 'Empleado no encontrado'}

    if not empleado.jefe_directo:
        return {
            'success': False,
            'error': f'{empleado.nombre_completo} no tiene jefe directo asignado. No se puede crear la solicitud.'
        }

    solicitud = SolicitudService.crear_solicitud(
        tipo=tipo,
        titulo=titulo,
        solicitante=empleado,
        descripcion=parametros.get('descripcion', ''),
        prioridad=parametros.get('prioridad', 'media'),
        datos=parametros.get('datos', {}),
        enviar_inmediatamente=True
    )

    return {
        'success': True,
        'mensaje': f'Solicitud creada y enviada a {solicitud.aprobador.get_full_name() if solicitud.aprobador else "aprobador"}',
        'datos': {
            'solicitud_id': str(solicitud.id),
            'tipo': solicitud.get_tipo_display(),
            'estado': solicitud.get_estado_display(),
            'aprobador': solicitud.aprobador.get_full_name() if solicitud.aprobador else None,
        }
    }


def aprobar_solicitud(usuario, parametros: Dict, contexto: Dict) -> Dict:
    """Aprueba una solicitud pendiente"""
    from .services import SolicitudService

    solicitud_id = parametros.get('solicitud_id')
    if not solicitud_id:
        return {'success': False, 'error': 'Debes especificar la solicitud a aprobar'}

    try:
        solicitud = SolicitudService.aprobar_solicitud(
            solicitud_id=solicitud_id,
            usuario=usuario,
            comentarios=parametros.get('comentarios', '')
        )

        return {
            'success': True,
            'mensaje': f'Solicitud de {solicitud.get_tipo_display()} aprobada. Se notifico a {solicitud.solicitante.nombre_completo}.',
            'datos': {
                'solicitud_id': str(solicitud.id),
                'tipo': solicitud.get_tipo_display(),
                'solicitante': solicitud.solicitante.nombre_completo,
            }
        }
    except PermissionError as e:
        return {'success': False, 'error': str(e)}
    except Exception as e:
        return {'success': False, 'error': f'Error al aprobar: {str(e)}'}


def rechazar_solicitud(usuario, parametros: Dict, contexto: Dict) -> Dict:
    """Rechaza una solicitud pendiente"""
    from .services import SolicitudService

    solicitud_id = parametros.get('solicitud_id')
    motivo = parametros.get('motivo')

    if not solicitud_id:
        return {'success': False, 'error': 'Debes especificar la solicitud a rechazar'}
    if not motivo:
        return {'success': False, 'error': 'Debes proporcionar un motivo para el rechazo'}

    try:
        solicitud = SolicitudService.rechazar_solicitud(
            solicitud_id=solicitud_id,
            usuario=usuario,
            motivo=motivo
        )

        return {
            'success': True,
            'mensaje': f'Solicitud de {solicitud.get_tipo_display()} rechazada. Se notifico a {solicitud.solicitante.nombre_completo}.',
            'datos': {
                'solicitud_id': str(solicitud.id),
                'tipo': solicitud.get_tipo_display(),
                'solicitante': solicitud.solicitante.nombre_completo,
                'motivo': motivo,
            }
        }
    except PermissionError as e:
        return {'success': False, 'error': str(e)}
    except Exception as e:
        return {'success': False, 'error': f'Error al rechazar: {str(e)}'}


def ver_mis_solicitudes(usuario, parametros: Dict, contexto: Dict) -> Dict:
    """Muestra las solicitudes realizadas por un empleado"""
    from apps.empleados.models import Empleado
    from .services import SolicitudService

    # Si es empleado, buscar su registro
    empleado_id = parametros.get('empleado_id')
    if empleado_id:
        try:
            empleado = Empleado.objects.get(id=empleado_id)
        except Empleado.DoesNotExist:
            return {'success': False, 'error': 'Empleado no encontrado'}
    else:
        # Buscar empleado del usuario actual
        empleado = Empleado.objects.filter(usuario=usuario).first()
        if not empleado:
            return {'success': False, 'error': 'No se encontro tu registro de empleado'}

    estado = parametros.get('estado')
    solicitudes = SolicitudService.obtener_solicitudes_empleado(empleado, estado)

    if not solicitudes.exists():
        return {
            'success': True,
            'mensaje': 'No tienes solicitudes registradas.',
            'datos': {'total': 0, 'solicitudes': []}
        }

    lista = []
    for s in solicitudes[:20]:
        lista.append({
            'id': str(s.id),
            'tipo': s.get_tipo_display(),
            'titulo': s.titulo,
            'estado': s.get_estado_display(),
            'prioridad': s.prioridad,
            'fecha_envio': s.fecha_envio.strftime('%d/%m/%Y') if s.fecha_envio else None,
            'aprobador': s.aprobador.get_full_name() if s.aprobador else None,
        })

    return {
        'success': True,
        'mensaje': f'Tienes {solicitudes.count()} solicitudes.',
        'datos': {
            'total': solicitudes.count(),
            'solicitudes': lista
        }
    }
