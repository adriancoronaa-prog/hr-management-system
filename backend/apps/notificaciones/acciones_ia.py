"""
Acciones de IA para el módulo de notificaciones
"""
from typing import Dict


def registrar_acciones():
    """Registra todas las acciones de notificaciones"""
    from apps.chat.acciones_registry import registrar_accion

    # ============================================================
    # ACCIÓN 42: Ver mis notificaciones
    # ============================================================
    registrar_accion(
        nombre='ver_mis_notificaciones',
        descripcion='Muestra las notificaciones pendientes del usuario actual',
        permisos=['es_admin', 'es_rrhh', 'es_jefe', 'es_empleado'],
        parametros={},
        ejemplo='Ver mis notificaciones',
        funcion=ver_mis_notificaciones
    )

    # ============================================================
    # ACCIÓN 43: Ver solicitudes pendientes de aprobar
    # ============================================================
    registrar_accion(
        nombre='ver_solicitudes_pendientes',
        descripcion='Muestra las solicitudes pendientes de aprobación para un jefe',
        permisos=['es_admin', 'es_rrhh', 'es_jefe'],
        parametros={},
        ejemplo='Ver solicitudes pendientes de aprobar',
        funcion=ver_solicitudes_pendientes
    )

    # ============================================================
    # ACCIÓN 44: Configurar notificaciones
    # ============================================================
    registrar_accion(
        nombre='configurar_notificaciones',
        descripcion='Configura las preferencias de notificaciones del usuario',
        permisos=['es_admin', 'es_rrhh', 'es_jefe', 'es_empleado'],
        parametros={
            'recibir_solicitudes': '(Opcional) true/false - Recibir notificaciones de solicitudes',
            'recibir_alertas': '(Opcional) true/false - Recibir alertas',
            'recibir_confirmaciones': '(Opcional) true/false - Recibir confirmaciones',
            'recibir_nomina': '(Opcional) true/false - Recibir notificaciones de nómina',
            'frecuencia_email': '(Opcional) inmediato/diario/semanal/nunca',
        },
        ejemplo='Configurar mis notificaciones para no recibir emails',
        funcion=configurar_notificaciones
    )

    # ============================================================
    # ACCIÓN 45: Marcar notificaciones como leídas
    # ============================================================
    registrar_accion(
        nombre='marcar_notificaciones_leidas',
        descripcion='Marca todas las notificaciones del usuario como leídas',
        permisos=['es_admin', 'es_rrhh', 'es_jefe', 'es_empleado'],
        parametros={},
        ejemplo='Marcar notificaciones como leídas',
        funcion=marcar_notificaciones_leidas
    )


# ========== Funciones de las acciones ==========

def ver_mis_notificaciones(usuario, parametros: Dict, contexto: Dict) -> Dict:
    """Muestra las notificaciones pendientes del usuario"""
    from .services import NotificacionService

    notificaciones = NotificacionService.obtener_notificaciones_pendientes(usuario)

    if not notificaciones.exists():
        return {
            'success': True,
            'mensaje': 'No tienes notificaciones pendientes.',
            'datos': {'total': 0, 'notificaciones': []}
        }

    lista = []
    for n in notificaciones[:20]:
        lista.append({
            'id': str(n.id),
            'tipo': n.get_tipo_display(),
            'titulo': n.titulo,
            'mensaje': n.mensaje[:100] + '...' if len(n.mensaje) > 100 else n.mensaje,
            'prioridad': n.prioridad,
            'fecha': n.created_at.strftime('%d/%m/%Y %H:%M'),
        })

    # Marcar como leídas las que se muestran
    for n in notificaciones[:20]:
        n.marcar_leida()

    return {
        'success': True,
        'mensaje': f'Tienes {notificaciones.count()} notificaciones pendientes.',
        'datos': {
            'total': notificaciones.count(),
            'notificaciones': lista
        }
    }


def ver_solicitudes_pendientes(usuario, parametros: Dict, contexto: Dict) -> Dict:
    """Muestra las solicitudes pendientes de aprobación para un jefe"""
    from .services import NotificacionService

    solicitudes = NotificacionService.obtener_solicitudes_pendientes(usuario)

    if not solicitudes.exists():
        return {
            'success': True,
            'mensaje': 'No tienes solicitudes pendientes de aprobar.',
            'datos': {'total': 0, 'solicitudes': []}
        }

    lista = []
    for s in solicitudes:
        datos = s.datos_extra or {}
        lista.append({
            'id': str(s.id),
            'tipo_solicitud': datos.get('tipo_solicitud', 'Solicitud'),
            'solicitante': datos.get('solicitante_nombre', 'Desconocido'),
            'detalles': datos.get('detalles', {}),
            'fecha': s.created_at.strftime('%d/%m/%Y %H:%M'),
            'prioridad': s.prioridad,
        })

    return {
        'success': True,
        'mensaje': f'Tienes {solicitudes.count()} solicitudes pendientes de aprobar.',
        'datos': {
            'total': solicitudes.count(),
            'solicitudes': lista
        }
    }


def configurar_notificaciones(usuario, parametros: Dict, contexto: Dict) -> Dict:
    """Configura las preferencias de notificaciones del usuario"""
    from .models import ConfiguracionNotificaciones

    config, created = ConfiguracionNotificaciones.objects.get_or_create(
        usuario=usuario
    )

    cambios = []

    if 'recibir_solicitudes' in parametros:
        valor = parametros['recibir_solicitudes']
        config.recibir_solicitudes = valor in [True, 'true', 'True', '1', 'si', 'yes']
        cambios.append(f"Solicitudes: {'activadas' if config.recibir_solicitudes else 'desactivadas'}")

    if 'recibir_alertas' in parametros:
        valor = parametros['recibir_alertas']
        config.recibir_alertas = valor in [True, 'true', 'True', '1', 'si', 'yes']
        cambios.append(f"Alertas: {'activadas' if config.recibir_alertas else 'desactivadas'}")

    if 'recibir_confirmaciones' in parametros:
        valor = parametros['recibir_confirmaciones']
        config.recibir_confirmaciones = valor in [True, 'true', 'True', '1', 'si', 'yes']
        cambios.append(f"Confirmaciones: {'activadas' if config.recibir_confirmaciones else 'desactivadas'}")

    if 'recibir_nomina' in parametros:
        valor = parametros['recibir_nomina']
        config.recibir_nomina = valor in [True, 'true', 'True', '1', 'si', 'yes']
        cambios.append(f"Nomina: {'activadas' if config.recibir_nomina else 'desactivadas'}")

    if 'frecuencia_email' in parametros:
        freq = parametros['frecuencia_email']
        if freq in ['inmediato', 'diario', 'semanal', 'nunca']:
            config.frecuencia_email = freq
            cambios.append(f"Frecuencia email: {freq}")

    if cambios:
        config.save()
        return {
            'success': True,
            'mensaje': f'Configuracion actualizada: {", ".join(cambios)}',
            'datos': {
                'cambios': cambios,
                'configuracion_actual': {
                    'recibir_solicitudes': config.recibir_solicitudes,
                    'recibir_alertas': config.recibir_alertas,
                    'recibir_confirmaciones': config.recibir_confirmaciones,
                    'recibir_nomina': config.recibir_nomina,
                    'frecuencia_email': config.frecuencia_email,
                }
            }
        }
    else:
        return {
            'success': True,
            'mensaje': 'Tu configuracion actual de notificaciones:',
            'datos': {
                'configuracion_actual': {
                    'recibir_solicitudes': config.recibir_solicitudes,
                    'recibir_alertas': config.recibir_alertas,
                    'recibir_confirmaciones': config.recibir_confirmaciones,
                    'recibir_nomina': config.recibir_nomina,
                    'frecuencia_email': config.frecuencia_email,
                }
            }
        }


def marcar_notificaciones_leidas(usuario, parametros: Dict, contexto: Dict) -> Dict:
    """Marca todas las notificaciones como leidas"""
    from .services import NotificacionService

    cantidad = NotificacionService.marcar_todas_leidas(usuario)

    if cantidad == 0:
        return {
            'success': True,
            'mensaje': 'No tenias notificaciones pendientes.',
            'datos': {'marcadas': 0}
        }

    return {
        'success': True,
        'mensaje': f'Se marcaron {cantidad} notificaciones como leidas.',
        'datos': {'marcadas': cantidad}
    }
