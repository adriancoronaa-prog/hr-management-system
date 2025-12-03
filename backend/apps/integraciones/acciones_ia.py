"""
Acciones IA para integraciones (Google Calendar, Auditoria)
"""
from typing import Dict
from datetime import date


def registrar_acciones():
    """Registra las acciones de integraciones"""
    from apps.chat.acciones_registry import registrar_accion

    # ============================================================
    # ACCION 49: Configurar Google Calendar
    # ============================================================
    registrar_accion(
        nombre='configurar_google_calendar',
        descripcion='Configura la integracion con Google Calendar',
        permisos=['es_admin'],
        parametros={
            'calendar_id': '(Opcional) ID del calendario',
            'sincronizar_vacaciones': '(Opcional) true/false',
            'sincronizar_cumpleanos': '(Opcional) true/false',
            'sincronizar_aniversarios': '(Opcional) true/false',
        },
        ejemplo='Configura Google Calendar para sincronizar vacaciones',
        funcion=accion_configurar_calendar,
        confirmacion_requerida=True
    )

    # ============================================================
    # ACCION 50: Sincronizar calendario
    # ============================================================
    registrar_accion(
        nombre='sincronizar_calendario',
        descripcion='Sincroniza eventos con Google Calendar',
        permisos=['es_admin', 'es_rrhh'],
        parametros={
            'tipo': '(Opcional) cumpleanos, aniversarios, todo',
        },
        ejemplo='Sincroniza los cumpleanos con Google Calendar',
        funcion=accion_sincronizar_calendario,
        confirmacion_requerida=True
    )

    # ============================================================
    # ACCION 51: Ver eventos del calendario
    # ============================================================
    registrar_accion(
        nombre='ver_eventos_calendario',
        descripcion='Muestra eventos sincronizados con el calendario',
        permisos=['es_admin', 'es_rrhh', 'es_jefe'],
        parametros={
            'mes': '(Opcional) Mes a consultar (1-12)',
            'tipo': '(Opcional) vacaciones, cumpleanos, aniversarios',
        },
        ejemplo='Muestra los eventos del calendario de este mes',
        funcion=accion_ver_eventos
    )

    # ============================================================
    # ACCION 52: Estado de Google Calendar
    # ============================================================
    registrar_accion(
        nombre='estado_google_calendar',
        descripcion='Muestra el estado de la integracion con Google Calendar',
        permisos=['es_admin', 'es_rrhh'],
        parametros={},
        ejemplo='Como esta la integracion con Google Calendar?',
        funcion=accion_estado_calendar
    )

    # ============================================================
    # ACCION 53: Ver auditoria
    # ============================================================
    registrar_accion(
        nombre='ver_auditoria',
        descripcion='Muestra el registro de auditoria del sistema',
        permisos=['es_admin'],
        parametros={
            'usuario_email': '(Opcional) Filtrar por usuario',
            'accion': '(Opcional) crear, modificar, eliminar, aprobar, rechazar',
            'limite': '(Opcional) Cantidad de registros, default: 20',
        },
        ejemplo='Muestra los ultimos cambios en el sistema',
        funcion=accion_ver_auditoria
    )

    # ============================================================
    # ACCION 54: Historial de objeto
    # ============================================================
    registrar_accion(
        nombre='historial_objeto',
        descripcion='Muestra el historial de cambios de un objeto especifico',
        permisos=['es_admin', 'es_rrhh'],
        parametros={
            'tipo': 'empleado, solicitud, nomina',
            'id': 'ID del objeto',
        },
        ejemplo='Muestra el historial de cambios del empleado Juan',
        funcion=accion_historial_objeto
    )

    print("[OK] Acciones de Integraciones registradas")


# ========== Funciones de las acciones ==========

def accion_configurar_calendar(usuario, params: Dict, contexto: Dict) -> Dict:
    """Configura Google Calendar"""
    from .models import ConfiguracionGoogleCalendar

    empresa = contexto.get('empresa_contexto')
    if not empresa:
        return {'success': False, 'error': 'No hay empresa en contexto'}

    config, created = ConfiguracionGoogleCalendar.objects.get_or_create(empresa=empresa)

    cambios = []

    if 'calendar_id' in params:
        config.calendar_id = params['calendar_id']
        cambios.append(f"Calendar ID: {params['calendar_id']}")

    if 'sincronizar_vacaciones' in params:
        valor = str(params['sincronizar_vacaciones']).lower()
        config.sincronizar_vacaciones = valor in ['true', '1', 'si', 'yes']
        cambios.append(f"Vacaciones: {'Si' if config.sincronizar_vacaciones else 'No'}")

    if 'sincronizar_cumpleanos' in params:
        valor = str(params['sincronizar_cumpleanos']).lower()
        config.sincronizar_cumpleanos = valor in ['true', '1', 'si', 'yes']
        cambios.append(f"Cumpleanos: {'Si' if config.sincronizar_cumpleanos else 'No'}")

    if 'sincronizar_aniversarios' in params:
        valor = str(params['sincronizar_aniversarios']).lower()
        config.sincronizar_aniversarios = valor in ['true', '1', 'si', 'yes']
        cambios.append(f"Aniversarios: {'Si' if config.sincronizar_aniversarios else 'No'}")

    config.save()

    return {
        'success': True,
        'mensaje': f'Configuracion actualizada: {", ".join(cambios)}' if cambios else 'Sin cambios. Configuracion actual mostrada.',
        'datos': {
            'activo': config.activo,
            'requiere_autorizacion': not config.credentials_json,
            'sincronizar_vacaciones': config.sincronizar_vacaciones,
            'sincronizar_cumpleanos': config.sincronizar_cumpleanos,
            'sincronizar_aniversarios': config.sincronizar_aniversarios,
        }
    }


def accion_sincronizar_calendario(usuario, params: Dict, contexto: Dict) -> Dict:
    """Sincroniza eventos con Google Calendar"""
    from .google_calendar import SincronizadorCalendario

    empresa = contexto.get('empresa_contexto')
    if not empresa:
        return {'success': False, 'error': 'No hay empresa en contexto'}

    tipo = params.get('tipo', 'todo')

    sincronizador = SincronizadorCalendario(empresa)

    if not sincronizador.config:
        return {
            'success': False,
            'error': 'Google Calendar no esta configurado. Usa "configurar_google_calendar" primero.'
        }

    if not sincronizador.service or not sincronizador.service.service:
        return {
            'success': False,
            'error': 'Google Calendar no esta autorizado. Se requiere completar el flujo OAuth.'
        }

    resultados = {}

    if tipo in ['cumpleanos', 'todo']:
        resultados['cumpleanos'] = sincronizador.sincronizar_cumpleanos_anual()

    if tipo in ['aniversarios', 'todo']:
        resultados['aniversarios'] = sincronizador.sincronizar_aniversarios_anual()

    total = sum(resultados.values())

    # Actualizar ultima sincronizacion
    from django.utils import timezone
    sincronizador.config.ultima_sincronizacion = timezone.now()
    sincronizador.config.save()

    return {
        'success': True,
        'mensaje': f'Se sincronizaron {total} eventos con Google Calendar',
        'datos': {
            'detalle': resultados,
            'total': total
        }
    }


def accion_ver_eventos(usuario, params: Dict, contexto: Dict) -> Dict:
    """Muestra eventos del calendario"""
    from .models import EventoSincronizado

    empresa = contexto.get('empresa_contexto')
    if not empresa:
        return {'success': False, 'error': 'No hay empresa en contexto'}

    mes = int(params.get('mes', date.today().month))
    tipo = params.get('tipo')
    ano = date.today().year

    eventos = EventoSincronizado.objects.filter(
        empresa=empresa,
        fecha_inicio__year=ano,
        fecha_inicio__month=mes
    )

    if tipo:
        eventos = eventos.filter(tipo=tipo)

    eventos = eventos.order_by('fecha_inicio')[:30]

    lista = [{
        'titulo': e.titulo,
        'tipo': e.get_tipo_display(),
        'fecha': e.fecha_inicio.strftime('%d/%m/%Y'),
        'empleado': e.empleado.nombre_completo if e.empleado else 'N/A',
        'sincronizado': 'Si' if e.sincronizado else 'No',
    } for e in eventos]

    return {
        'success': True,
        'mensaje': f'{len(lista)} eventos en {mes}/{ano}',
        'datos': {
            'eventos': lista,
            'total': len(lista)
        }
    }


def accion_estado_calendar(usuario, params: Dict, contexto: Dict) -> Dict:
    """Muestra estado de la integracion"""
    from .models import ConfiguracionGoogleCalendar, EventoSincronizado

    empresa = contexto.get('empresa_contexto')
    if not empresa:
        return {'success': False, 'error': 'No hay empresa en contexto'}

    try:
        config = empresa.config_google_calendar
    except ConfiguracionGoogleCalendar.DoesNotExist:
        return {
            'success': True,
            'mensaje': 'Google Calendar no esta configurado. Usa "configurar_google_calendar" para comenzar.',
            'datos': {'configurado': False}
        }

    total_eventos = EventoSincronizado.objects.filter(empresa=empresa).count()

    return {
        'success': True,
        'mensaje': 'Estado de Google Calendar',
        'datos': {
            'configurado': True,
            'activo': config.activo,
            'autorizado': bool(config.credentials_json),
            'sincronizar_vacaciones': config.sincronizar_vacaciones,
            'sincronizar_cumpleanos': config.sincronizar_cumpleanos,
            'sincronizar_aniversarios': config.sincronizar_aniversarios,
            'ultima_sincronizacion': config.ultima_sincronizacion.strftime('%d/%m/%Y %H:%M') if config.ultima_sincronizacion else 'Nunca',
            'total_eventos': total_eventos,
            'ultimo_error': config.error_ultimo or 'Ninguno',
        }
    }


def accion_ver_auditoria(usuario, params: Dict, contexto: Dict) -> Dict:
    """Muestra el registro de auditoria del sistema"""
    from .models import RegistroAuditoria
    from apps.usuarios.models import Usuario

    limite = int(params.get('limite', 20))
    usuario_email = params.get('usuario_email')
    accion_filtro = params.get('accion')

    registros = RegistroAuditoria.objects.all()

    if usuario_email:
        try:
            usuario_filtro = Usuario.objects.get(email__icontains=usuario_email)
            registros = registros.filter(usuario=usuario_filtro)
        except Usuario.DoesNotExist:
            return {'success': False, 'error': f'Usuario {usuario_email} no encontrado'}

    if accion_filtro:
        registros = registros.filter(accion=accion_filtro)

    registros = registros.order_by('-created_at')[:limite]

    lista = [{
        'fecha': r.created_at.strftime('%d/%m/%Y %H:%M'),
        'usuario': r.usuario.email if r.usuario else 'Sistema',
        'accion': r.get_accion_display(),
        'descripcion': r.descripcion[:100] + '...' if len(r.descripcion) > 100 else r.descripcion,
        'modelo': r.modelo or 'N/A',
        'ip': r.ip_address or 'N/A',
    } for r in registros]

    return {
        'success': True,
        'mensaje': f'{len(lista)} registros de auditoria',
        'datos': {
            'registros': lista,
            'total': len(lista)
        }
    }


def accion_historial_objeto(usuario, params: Dict, contexto: Dict) -> Dict:
    """Muestra el historial de cambios de un objeto especifico"""
    from .models import RegistroAuditoria
    from django.contrib.contenttypes.models import ContentType

    tipo = params.get('tipo')
    objeto_id = params.get('id')

    if not tipo or not objeto_id:
        return {'success': False, 'error': 'Especifica tipo e id del objeto'}

    # Mapear tipos a modelos
    modelo_map = {
        'empleado': 'empleados.Empleado',
        'solicitud': 'solicitudes.Solicitud',
        'nomina': 'nomina.PeriodoNomina',
        'recibo': 'nomina.ReciboNomina',
        'usuario': 'usuarios.Usuario',
    }

    if tipo not in modelo_map:
        return {
            'success': False,
            'error': f'Tipo no valido. Opciones: {", ".join(modelo_map.keys())}'
        }

    app_label, model_name = modelo_map[tipo].split('.')

    try:
        ct = ContentType.objects.get(app_label=app_label, model=model_name.lower())
    except ContentType.DoesNotExist:
        return {'success': False, 'error': 'Modelo no encontrado'}

    registros = RegistroAuditoria.objects.filter(
        content_type=ct,
        object_id=str(objeto_id)
    ).order_by('-created_at')[:30]

    if not registros.exists():
        return {
            'success': True,
            'mensaje': f'No hay historial para {tipo} ID {objeto_id}',
            'datos': {'registros': []}
        }

    lista = [{
        'fecha': r.created_at.strftime('%d/%m/%Y %H:%M'),
        'usuario': r.usuario.email if r.usuario else 'Sistema',
        'accion': r.get_accion_display(),
        'descripcion': r.descripcion,
    } for r in registros]

    return {
        'success': True,
        'mensaje': f'{len(lista)} cambios registrados para {tipo} ID {objeto_id}',
        'datos': {
            'registros': lista,
            'total': len(lista)
        }
    }
