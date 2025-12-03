"""
Acciones de IA para el módulo de Desempeño y KPIs
"""
from typing import Dict
from decimal import Decimal
from datetime import date, datetime


def registrar_acciones():
    """Registra las acciones de desempeño en el registro central"""
    from apps.chat.acciones_registry import registrar_accion
    
    # === KPIs ===
    registrar_accion(
        nombre='asignar_kpi',
        descripcion='Asigna un KPI a un empleado con meta y periodo',
        permisos=['es_admin', 'es_rrhh', 'es_jefe', 'es_empleado'],
        parametros={
            'empleado_id': 'ID del empleado (opcional si es para sí mismo)',
            'nombre': 'Nombre del KPI',
            'descripcion': '(Opcional) Descripción del KPI',
            'meta': 'Valor de la meta a alcanzar',
            'periodo': 'Periodo del KPI (ej: 2024-Q4, 2024-12)',
            'fecha_inicio': 'Fecha de inicio (YYYY-MM-DD)',
            'fecha_fin': 'Fecha de fin (YYYY-MM-DD)',
            'peso': '(Opcional) Peso en la evaluación, default: 100',
            'tipo_medicion': '(Opcional) numero, porcentaje, moneda, boolean, escala',
        },
        ejemplo='Asigna un KPI de ventas de $100,000 a Juan para el Q4',
        funcion=accion_asignar_kpi,
        confirmacion_requerida=True
    )
    
    registrar_accion(
        nombre='ver_mis_kpis',
        descripcion='Muestra los KPIs asignados al usuario actual',
        permisos=['es_empleado', 'es_jefe', 'es_rrhh', 'es_admin'],
        parametros={
            'periodo': '(Opcional) Filtrar por periodo',
        },
        ejemplo='Muéstrame mis KPIs',
        funcion=accion_ver_mis_kpis
    )
    
    registrar_accion(
        nombre='ver_kpis_equipo',
        descripcion='Muestra los KPIs del equipo (solo para jefes)',
        permisos=['es_jefe', 'es_rrhh', 'es_admin'],
        parametros={
            'periodo': '(Opcional) Filtrar por periodo',
        },
        ejemplo='Muéstrame los KPIs de mi equipo',
        funcion=accion_ver_kpis_equipo
    )
    
    registrar_accion(
        nombre='registrar_avance_kpi',
        descripcion='Registra un avance o resultado en un KPI',
        permisos=['es_empleado', 'es_jefe', 'es_rrhh', 'es_admin'],
        parametros={
            'kpi_id': 'ID del KPI',
            'valor': 'Valor logrado',
            'comentarios': '(Opcional) Comentarios sobre el avance',
        },
        ejemplo='Registra que logré $75,000 en el KPI de ventas',
        funcion=accion_registrar_avance
    )
    
    registrar_accion(
        nombre='solicitar_cambio_kpi',
        descripcion='Solicita un cambio en un KPI (requiere aprobación del jefe)',
        permisos=['es_empleado'],
        parametros={
            'kpi_id': 'ID del KPI a modificar',
            'cambios': 'Diccionario con los cambios (meta, nombre, descripcion, fecha_fin)',
            'motivo': 'Motivo del cambio solicitado',
        },
        ejemplo='Solicita cambiar mi meta de ventas de $100,000 a $80,000',
        funcion=accion_solicitar_cambio
    )
    
    registrar_accion(
        nombre='ver_solicitudes_pendientes',
        descripcion='Muestra las solicitudes de cambio de KPIs pendientes de aprobar',
        permisos=['es_jefe', 'es_rrhh', 'es_admin'],
        parametros={},
        ejemplo='¿Hay solicitudes de KPIs pendientes de aprobar?',
        funcion=accion_ver_solicitudes_pendientes
    )
    
    registrar_accion(
        nombre='aprobar_cambio_kpi',
        descripcion='Aprueba o rechaza un cambio solicitado en un KPI',
        permisos=['es_jefe', 'es_rrhh', 'es_admin'],
        parametros={
            'kpi_id': 'ID del KPI',
            'aprobar': 'true para aprobar, false para rechazar',
            'comentario': '(Opcional) Comentario sobre la decisión',
        },
        ejemplo='Aprueba el cambio de meta de Juan',
        funcion=accion_aprobar_cambio,
        confirmacion_requerida=True
    )
    
    registrar_accion(
        nombre='resumen_desempeno_equipo',
        descripcion='Muestra un resumen del desempeño del equipo',
        permisos=['es_jefe', 'es_rrhh', 'es_admin'],
        parametros={},
        ejemplo='¿Cómo va el desempeño de mi equipo?',
        funcion=accion_resumen_equipo
    )


# ============ IMPLEMENTACIÓN DE FUNCIONES ============

def accion_asignar_kpi(usuario, params: Dict, contexto: Dict) -> Dict:
    """Asigna un KPI a un empleado"""
    from apps.empleados.models import Empleado
    from .services import asignar_kpi
    
    empleado_id = params.get('empleado_id')
    nombre = params.get('nombre')
    meta = params.get('meta')
    periodo = params.get('periodo')
    
    if not nombre or not meta:
        return {'success': False, 'error': 'Se requiere nombre y meta del KPI'}
    
    # Determinar empleado
    if empleado_id:
        try:
            empleado = Empleado.objects.get(pk=empleado_id)
        except Empleado.DoesNotExist:
            return {'success': False, 'error': 'Empleado no encontrado'}
    elif hasattr(usuario, 'empleado') and usuario.empleado:
        empleado = usuario.empleado
    else:
        return {'success': False, 'error': 'Debes especificar el empleado'}
    
    # Determinar quién asigna
    asignado_por = usuario.empleado if hasattr(usuario, 'empleado') else None
    
    # Parsear fechas
    fecha_inicio = params.get('fecha_inicio', date.today())
    fecha_fin = params.get('fecha_fin')
    
    if isinstance(fecha_inicio, str):
        fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
    
    if fecha_fin:
        if isinstance(fecha_fin, str):
            fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
    else:
        # Default: fin de trimestre/mes según periodo
        if not periodo:
            periodo = fecha_inicio.strftime('%Y-%m')
        fecha_fin = fecha_inicio.replace(day=28) + timedelta(days=4)
        fecha_fin = fecha_fin.replace(day=1) - timedelta(days=1)  # Último día del mes
    
    if not periodo:
        periodo = fecha_inicio.strftime('%Y-%m')
    
    return asignar_kpi(
        empleado=empleado,
        asignado_por=asignado_por,
        periodo=periodo,
        meta=Decimal(str(meta)),
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        nombre_personalizado=nombre,
        descripcion=params.get('descripcion', ''),
        tipo_medicion=params.get('tipo_medicion', 'numero'),
        peso=Decimal(str(params.get('peso', 100))),
    )


def accion_ver_mis_kpis(usuario, params: Dict, contexto: Dict) -> Dict:
    """Muestra los KPIs del usuario"""
    from .services import GestorKPIs
    
    if not hasattr(usuario, 'empleado') or not usuario.empleado:
        return {'success': False, 'error': 'No tienes un perfil de empleado asociado'}
    
    gestor = GestorKPIs(usuario.empleado)
    kpis = gestor.obtener_kpis_activos()
    
    if not kpis:
        return {
            'success': True,
            'mensaje': 'No tienes KPIs asignados actualmente.',
            'kpis': []
        }
    
    # Formatear respuesta
    lineas = [f"📊 **Tus KPIs ({len(kpis)} activos)**\n"]
    
    for kpi in kpis:
        estado_emoji = "✅" if kpi['estado'] == 'activo' else "⏳"
        progreso = f"{kpi['porcentaje']:.1f}%" if kpi['porcentaje'] else "Sin avance"
        valor = kpi['valor_logrado'] if kpi['valor_logrado'] else 0
        
        lineas.append(f"{estado_emoji} **{kpi['nombre']}** ({kpi['periodo']})")
        lineas.append(f"   Meta: {kpi['meta']:,.2f} | Logrado: {valor:,.2f} | {progreso}")
        
        if kpi['tiene_cambios_pendientes']:
            lineas.append(f"   ⚠️ Cambios pendientes de aprobación")
        lineas.append("")
    
    return {
        'success': True,
        'mensaje': "\n".join(lineas),
        'kpis': kpis
    }


def accion_ver_kpis_equipo(usuario, params: Dict, contexto: Dict) -> Dict:
    """Muestra los KPIs del equipo"""
    from .services import GestorKPIsJefe
    
    if not hasattr(usuario, 'empleado') or not usuario.empleado:
        return {'success': False, 'error': 'No tienes un perfil de empleado asociado'}
    
    empleado = usuario.empleado
    
    if not empleado.subordinados.exists() and usuario.rol not in ['administrador', 'empleador']:
        return {'success': False, 'error': 'No tienes equipo a cargo'}
    
    gestor = GestorKPIsJefe(empleado)
    kpis = gestor.obtener_kpis_equipo(params.get('periodo'))
    
    if not kpis:
        return {
            'success': True,
            'mensaje': 'No hay KPIs asignados a tu equipo.',
            'kpis': []
        }
    
    # Agrupar por empleado
    por_empleado = {}
    for kpi in kpis:
        emp = kpi['empleado']
        if emp not in por_empleado:
            por_empleado[emp] = []
        por_empleado[emp].append(kpi)
    
    lineas = [f"📊 **KPIs del Equipo ({len(kpis)} total)**\n"]
    
    for emp, kpis_emp in por_empleado.items():
        lineas.append(f"👤 **{emp}**")
        for kpi in kpis_emp:
            estado = "⏳" if kpi['requiere_aprobacion'] else "✅"
            progreso = f"{kpi['porcentaje']:.1f}%" if kpi['porcentaje'] else "Sin avance"
            lineas.append(f"   {estado} {kpi['nombre_kpi']}: {progreso}")
        lineas.append("")
    
    return {
        'success': True,
        'mensaje': "\n".join(lineas),
        'kpis': kpis
    }


def accion_registrar_avance(usuario, params: Dict, contexto: Dict) -> Dict:
    """Registra avance en un KPI"""
    from .services import registrar_avance_kpi
    
    kpi_id = params.get('kpi_id')
    valor = params.get('valor')
    
    if not kpi_id or valor is None:
        return {'success': False, 'error': 'Se requiere kpi_id y valor'}
    
    if not hasattr(usuario, 'empleado') or not usuario.empleado:
        return {'success': False, 'error': 'No tienes un perfil de empleado asociado'}
    
    return registrar_avance_kpi(
        asignacion_id=kpi_id,
        empleado=usuario.empleado,
        valor=valor,
        comentarios=params.get('comentarios', '')
    )


def accion_solicitar_cambio(usuario, params: Dict, contexto: Dict) -> Dict:
    """Solicita cambio en un KPI"""
    from .services import solicitar_cambio_kpi
    
    kpi_id = params.get('kpi_id')
    cambios = params.get('cambios', {})
    motivo = params.get('motivo', '')
    
    if not kpi_id or not cambios:
        return {'success': False, 'error': 'Se requiere kpi_id y cambios'}
    
    if not hasattr(usuario, 'empleado') or not usuario.empleado:
        return {'success': False, 'error': 'No tienes un perfil de empleado asociado'}
    
    return solicitar_cambio_kpi(
        asignacion_id=kpi_id,
        empleado=usuario.empleado,
        cambios=cambios,
        motivo=motivo
    )


def accion_ver_solicitudes_pendientes(usuario, params: Dict, contexto: Dict) -> Dict:
    """Muestra solicitudes pendientes de aprobar"""
    from .services import GestorKPIsJefe
    
    if not hasattr(usuario, 'empleado') or not usuario.empleado:
        return {'success': False, 'error': 'No tienes un perfil de empleado asociado'}
    
    gestor = GestorKPIsJefe(usuario.empleado)
    pendientes = gestor.obtener_solicitudes_pendientes()
    
    if not pendientes:
        return {
            'success': True,
            'mensaje': '✅ No hay solicitudes de cambio pendientes.',
            'solicitudes': []
        }
    
    lineas = [f"⏳ **Solicitudes Pendientes ({len(pendientes)})**\n"]
    
    for sol in pendientes:
        lineas.append(f"👤 **{sol['empleado']}** - {sol['nombre_kpi']}")
        lineas.append(f"   Cambios: {sol['cambios_propuestos']}")
        lineas.append(f"   Motivo: {sol['motivo'] or 'No especificado'}")
        lineas.append(f"   ID: {sol['id']}")
        lineas.append("")
    
    return {
        'success': True,
        'mensaje': "\n".join(lineas),
        'solicitudes': pendientes
    }


def accion_aprobar_cambio(usuario, params: Dict, contexto: Dict) -> Dict:
    """Aprueba o rechaza cambio en KPI"""
    from .services import aprobar_cambio_kpi
    
    kpi_id = params.get('kpi_id')
    aprobar = params.get('aprobar', True)
    
    if isinstance(aprobar, str):
        aprobar = aprobar.lower() in ['true', 'si', 'sí', 'yes', '1']
    
    if not kpi_id:
        return {'success': False, 'error': 'Se requiere kpi_id'}
    
    if not hasattr(usuario, 'empleado') or not usuario.empleado:
        return {'success': False, 'error': 'No tienes un perfil de empleado asociado'}
    
    return aprobar_cambio_kpi(
        asignacion_id=kpi_id,
        jefe=usuario.empleado,
        aprobar=aprobar,
        comentario=params.get('comentario', '')
    )


def accion_resumen_equipo(usuario, params: Dict, contexto: Dict) -> Dict:
    """Muestra resumen de desempeño del equipo"""
    from .services import GestorKPIsJefe
    
    if not hasattr(usuario, 'empleado') or not usuario.empleado:
        return {'success': False, 'error': 'No tienes un perfil de empleado asociado'}
    
    empleado = usuario.empleado
    
    if not empleado.subordinados.exists() and usuario.rol not in ['administrador', 'empleador']:
        return {'success': False, 'error': 'No tienes equipo a cargo'}
    
    gestor = GestorKPIsJefe(empleado)
    resumen = gestor.obtener_resumen_equipo()
    
    lineas = [f"📈 **Resumen de Desempeño del Equipo**\n"]
    lineas.append(f"👥 Total subordinados: {resumen['total_subordinados']}")
    lineas.append(f"⏳ Solicitudes pendientes: {resumen['solicitudes_pendientes']}\n")
    
    lineas.append("**Ranking por desempeño:**")
    for i, emp in enumerate(resumen['empleados'], 1):
        promedio = emp['promedio_cumplimiento']
        if promedio is not None:
            emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
            lineas.append(f"{emoji} {emp['nombre']}: {promedio:.1f}% ({emp['kpis_activos']} KPIs)")
        else:
            lineas.append(f"{i}. {emp['nombre']}: Sin KPIs evaluados")
    
    return {
        'success': True,
        'mensaje': "\n".join(lineas),
        'datos': resumen
    }
