"""
Acciones de IA para el módulo de reportes
"""
from typing import Dict


def registrar_acciones():
    """Registra las acciones de reportes en el registro central"""
    from apps.chat.acciones_registry import registrar_accion
    
    registrar_accion(
        nombre='dashboard_empresa',
        descripcion='Muestra el dashboard con métricas de una empresa',
        permisos=['es_admin', 'es_rrhh'],
        parametros={
            'empresa_id': '(Opcional) ID de la empresa',
        },
        ejemplo='Muéstrame el dashboard de la empresa',
        funcion=dashboard_empresa
    )
    
    registrar_accion(
        nombre='dashboard_empleado',
        descripcion='Muestra el dashboard con métricas de un empleado',
        permisos=['es_admin', 'es_rrhh', 'es_jefe', 'es_empleado'],
        parametros={
            'empleado_id': '(Opcional) ID del empleado',
        },
        ejemplo='Muéstrame mi dashboard',
        funcion=dashboard_empleado
    )
    
    registrar_accion(
        nombre='calcular_liquidacion',
        descripcion='Calcula la liquidación o finiquito de un empleado',
        permisos=['es_admin', 'es_rrhh'],
        parametros={
            'empleado_id': 'ID del empleado',
            'fecha_baja': '(Opcional) Fecha de baja, default: hoy',
            'es_despido_injustificado': '(Opcional) Si es despido injustificado, default: true',
        },
        ejemplo='Calcula la liquidación de Juan si lo despidieran hoy',
        funcion=calcular_liquidacion
    )
    
    registrar_accion(
        nombre='generar_pdf_empleado',
        descripcion='Genera un PDF con el reporte del empleado',
        permisos=['es_admin', 'es_rrhh', 'es_jefe', 'es_empleado'],
        parametros={
            'empleado_id': '(Opcional) ID del empleado',
            'incluir_liquidacion': '(Opcional) Incluir cálculo de liquidación',
        },
        ejemplo='Genera mi reporte en PDF',
        funcion=generar_pdf_empleado
    )

    # ============================================================
    # ACCION 55: Exportar empleados a Excel
    # ============================================================
    registrar_accion(
        nombre='exportar_empleados_excel',
        descripcion='Exporta lista de empleados a Excel',
        permisos=['es_admin', 'es_rrhh'],
        parametros={
            'estado': '(Opcional) activo, baja, todos',
            'departamento': '(Opcional) Filtrar por departamento',
        },
        ejemplo='Exporta los empleados a Excel',
        funcion=accion_exportar_empleados_excel
    )

    # ============================================================
    # ACCION 56: Exportar nomina a Excel
    # ============================================================
    registrar_accion(
        nombre='exportar_nomina_excel',
        descripcion='Exporta la nomina de un periodo a Excel',
        permisos=['es_admin', 'es_rrhh'],
        parametros={
            'periodo_id': '(Opcional) ID del periodo',
        },
        ejemplo='Exporta la nomina del periodo actual a Excel',
        funcion=accion_exportar_nomina_excel
    )

    # ============================================================
    # ACCION 57: Exportar incidencias a Excel
    # ============================================================
    registrar_accion(
        nombre='exportar_incidencias_excel',
        descripcion='Exporta incidencias a Excel',
        permisos=['es_admin', 'es_rrhh'],
        parametros={
            'mes': '(Opcional) Mes (1-12)',
            'ano': '(Opcional) Ano',
        },
        ejemplo='Exporta las incidencias de este mes a Excel',
        funcion=accion_exportar_incidencias_excel
    )

    # ============================================================
    # ACCION 58: Exportar solicitudes a Excel
    # ============================================================
    registrar_accion(
        nombre='exportar_solicitudes_excel',
        descripcion='Exporta solicitudes a Excel',
        permisos=['es_admin', 'es_rrhh'],
        parametros={
            'estado': '(Opcional) pendiente, aprobada, rechazada, todos',
            'tipo': '(Opcional) vacaciones, permiso, otro',
        },
        ejemplo='Exporta las solicitudes a Excel',
        funcion=accion_exportar_solicitudes_excel
    )


# ============ IMPLEMENTACIÓN DE FUNCIONES ============

def dashboard_empresa(usuario, params: Dict, contexto: Dict) -> Dict:
    """Muestra métricas de empresa"""
    from apps.empresas.models import Empresa
    from apps.reportes.services import MetricasEmpresa
    
    empresa_id = params.get('empresa_id') or (contexto.get('empresa_contexto').id if contexto.get('empresa_contexto') else None)
    
    if not empresa_id:
        return {'success': False, 'error': 'Debes especificar la empresa'}
    
    try:
        empresa = Empresa.objects.get(pk=empresa_id)
    except Empresa.DoesNotExist:
        return {'success': False, 'error': 'Empresa no encontrada'}
    
    metricas = MetricasEmpresa(empresa)
    datos = metricas.obtener_resumen_completo()
    
    # Formatear para respuesta legible
    emp = datos['empleados']
    costos = datos['costos_proyectados']
    
    resumen = f"""
=== Dashboard de {empresa.razon_social} ===

** Empleados: **
- Activos: {emp['activos']} de {emp['total']} totales
- Antiguedad promedio: {emp['antiguedad_promedio_anos']} anos
- Salario promedio: ${emp['salario_mensual_promedio']:,.2f}/mes

** Nomina: **
- Mensual estimada: ${emp['nomina_mensual_estimada']:,.2f}
- Aguinaldo proyectado: ${costos['aguinaldo_proyectado']:,.2f}
- Costo anual estimado: ${costos['costo_anual_estimado']:,.2f}
"""
    
    return {
        'success': True,
        'mensaje': resumen,
        'datos': datos
    }


def dashboard_empleado(usuario, params: Dict, contexto: Dict) -> Dict:
    """Muestra métricas de empleado"""
    from apps.empleados.models import Empleado
    from apps.reportes.services import MetricasEmpleado
    from apps.chat.permisos import validar_acceso_recurso
    
    empleado_id = params.get('empleado_id')
    
    if empleado_id:
        try:
            empleado = Empleado.objects.get(pk=empleado_id)
        except Empleado.DoesNotExist:
            return {'success': False, 'error': 'Empleado no encontrado'}
        
        if not validar_acceso_recurso(usuario, empleado, 'ver'):
            return {'success': False, 'error': 'No tienes acceso a este empleado'}
    elif hasattr(usuario, 'empleado') and usuario.empleado:
        empleado = usuario.empleado
    else:
        return {'success': False, 'error': 'No se especificó empleado'}
    
    metricas = MetricasEmpleado(empleado)
    datos = metricas.obtener_resumen_completo()
    
    ant = datos['antiguedad']
    sal = datos['salario']
    vac = datos['vacaciones']
    prest = datos['prestaciones']
    
    resumen = f"""
=== Dashboard de {empleado.nombre_completo} ===

** Antiguedad: ** {ant['descripcion']}

** Salario: **
- Diario: ${sal['salario_diario']:,.2f}
- Mensual: ${sal['salario_mensual']:,.2f}

** Vacaciones: **
- Dias por ley: {vac['dias_por_ley']}
- Dias tomados este ano: {vac['dias_tomados_ano']}
- Dias pendientes: {vac['dias_pendientes']}
- Prima vacacional: ${vac['prima_vacacional_monto']:,.2f}

** Prestaciones: **
- Aguinaldo: ${prest['aguinaldo']['monto']:,.2f} ({prest['aguinaldo']['dias']} dias)
"""
    
    return {
        'success': True,
        'mensaje': resumen,
        'datos': datos
    }


def calcular_liquidacion(usuario, params: Dict, contexto: Dict) -> Dict:
    """Calcula liquidación de empleado"""
    from apps.empleados.models import Empleado
    from apps.reportes.services import MetricasEmpleado
    from datetime import date, datetime
    
    empleado_id = params.get('empleado_id')
    
    if not empleado_id:
        return {'success': False, 'error': 'Debes especificar el empleado'}
    
    try:
        empleado = Empleado.objects.get(pk=empleado_id)
    except Empleado.DoesNotExist:
        return {'success': False, 'error': 'Empleado no encontrado'}
    
    fecha_baja = params.get('fecha_baja', date.today())
    if isinstance(fecha_baja, str):
        fecha_baja = datetime.strptime(fecha_baja, '%Y-%m-%d').date()
    
    es_despido = params.get('es_despido_injustificado', True)
    
    metricas = MetricasEmpleado(empleado)
    liq = metricas.calcular_liquidacion(fecha_baja, es_despido)
    
    fin = liq['finiquito']
    liq_det = liq['liquidacion']
    
    tipo = "Liquidación (Despido Injustificado)" if es_despido else "Finiquito (Renuncia)"
    
    resumen = f"""
💰 **{tipo} de {empleado.nombre_completo}**

📅 Fecha de baja: {fecha_baja.strftime('%d/%m/%Y')}
⏱️ Antigüedad: {liq['antiguedad']['anos']} años, {liq['antiguedad']['meses']} meses

**FINIQUITO:**
- Aguinaldo proporcional: ${fin['aguinaldo_proporcional']:,.2f}
- Vacaciones proporcionales: ${fin['vacaciones_proporcionales_monto']:,.2f}
- Prima vacacional: ${fin['prima_vacacional']:,.2f}
- **Subtotal:** ${fin['subtotal_finiquito']:,.2f}
"""
    
    if es_despido:
        resumen += f"""
**LIQUIDACIÓN:**
- Indemnización 3 meses: ${liq_det['indemnizacion_3_meses']:,.2f}
- 20 días por año: ${liq_det['indemnizacion_20_dias_ano']:,.2f}
- Prima de antigüedad: ${liq_det['prima_antiguedad']:,.2f}
- **Subtotal:** ${liq_det['subtotal_liquidacion']:,.2f}
"""
    
    resumen += f"""
━━━━━━━━━━━━━━━━━━━━━━
**TOTAL A PAGAR: ${liq['total_a_pagar']:,.2f}**
"""
    
    return {
        'success': True,
        'mensaje': resumen,
        'datos': liq
    }


def generar_pdf_empleado(usuario, params: Dict, contexto: Dict) -> Dict:
    """Genera PDF del empleado"""
    # Por ahora retorna la URL donde descargar
    empleado_id = params.get('empleado_id')

    if not empleado_id:
        if hasattr(usuario, 'empleado') and usuario.empleado:
            empleado_id = usuario.empleado.id
        else:
            return {'success': False, 'error': 'No se especifico empleado'}

    incluir_liq = params.get('incluir_liquidacion', False)

    url = f"/api/reportes/empleado/{empleado_id}/dashboard/pdf/"
    if incluir_liq:
        url += "?incluir_liquidacion=true"

    return {
        'success': True,
        'mensaje': f'PDF disponible para descarga',
        'url': url
    }


# ============ FUNCIONES DE EXPORTACION EXCEL ============

def accion_exportar_empleados_excel(usuario, params: Dict, contexto: Dict) -> Dict:
    """Exporta empleados a Excel"""
    from apps.empleados.models import Empleado
    from .excel_service import ExcelService
    from datetime import date
    import base64

    empresa = contexto.get('empresa_contexto')
    if not empresa:
        return {'success': False, 'error': 'No hay empresa en contexto'}

    estado = params.get('estado', 'activo')
    departamento = params.get('departamento')

    empleados = Empleado.objects.filter(empresa=empresa)

    if estado != 'todos':
        empleados = empleados.filter(estado=estado)

    if departamento:
        empleados = empleados.filter(departamento__icontains=departamento)

    empleados = empleados.order_by('apellido_paterno', 'nombre')

    if not empleados.exists():
        return {'success': False, 'error': 'No hay empleados con los filtros especificados'}

    buffer = ExcelService.generar_reporte_empleados(empleados, empresa.razon_social)

    # Convertir a base64 para enviar al frontend
    excel_base64 = base64.b64encode(buffer.getvalue()).decode()

    return {
        'success': True,
        'mensaje': f'Reporte generado con {empleados.count()} empleados',
        'archivo': {
            'nombre': f'empleados_{empresa.rfc}_{date.today().strftime("%Y%m%d")}.xlsx',
            'contenido_base64': excel_base64,
            'tipo': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        }
    }


def accion_exportar_nomina_excel(usuario, params: Dict, contexto: Dict) -> Dict:
    """Exporta nomina a Excel"""
    from apps.nomina.models import PeriodoNomina, ReciboNomina
    from .excel_service import ExcelService
    import base64

    empresa = contexto.get('empresa_contexto')
    if not empresa:
        return {'success': False, 'error': 'No hay empresa en contexto'}

    periodo_id = params.get('periodo_id')

    if periodo_id:
        try:
            periodo = PeriodoNomina.objects.get(pk=periodo_id, empresa=empresa)
        except PeriodoNomina.DoesNotExist:
            return {'success': False, 'error': 'Periodo no encontrado'}
    else:
        periodo = PeriodoNomina.objects.filter(empresa=empresa).order_by('-fecha_inicio').first()
        if not periodo:
            return {'success': False, 'error': 'No hay periodos de nomina'}

    recibos = list(ReciboNomina.objects.filter(periodo=periodo).select_related('empleado').order_by('empleado__apellido_paterno'))

    if not recibos:
        return {'success': False, 'error': 'No hay recibos en este periodo'}

    buffer = ExcelService.generar_reporte_nomina(periodo, recibos)
    excel_base64 = base64.b64encode(buffer.getvalue()).decode()

    return {
        'success': True,
        'mensaje': f'Reporte de nomina generado: {len(recibos)} recibos',
        'archivo': {
            'nombre': f'nomina_{periodo.tipo_periodo}_{periodo.numero_periodo}_{periodo.ano}.xlsx',
            'contenido_base64': excel_base64,
            'tipo': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        }
    }


def accion_exportar_incidencias_excel(usuario, params: Dict, contexto: Dict) -> Dict:
    """Exporta incidencias a Excel"""
    from apps.nomina.models import IncidenciaNomina
    from .excel_service import ExcelService
    from datetime import date
    import base64

    empresa = contexto.get('empresa_contexto')
    if not empresa:
        return {'success': False, 'error': 'No hay empresa en contexto'}

    mes = int(params.get('mes', date.today().month))
    ano = int(params.get('ano', date.today().year))

    incidencias = list(IncidenciaNomina.objects.filter(
        empleado__empresa=empresa,
        fecha_inicio__month=mes,
        fecha_inicio__year=ano
    ).select_related('empleado').order_by('-fecha_inicio'))

    if not incidencias:
        return {'success': False, 'error': f'No hay incidencias en {mes}/{ano}'}

    buffer = ExcelService.generar_reporte_incidencias(incidencias, mes, ano)
    excel_base64 = base64.b64encode(buffer.getvalue()).decode()

    return {
        'success': True,
        'mensaje': f'Reporte de incidencias: {len(incidencias)} registros',
        'archivo': {
            'nombre': f'incidencias_{mes}_{ano}.xlsx',
            'contenido_base64': excel_base64,
            'tipo': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        }
    }


def accion_exportar_solicitudes_excel(usuario, params: Dict, contexto: Dict) -> Dict:
    """Exporta solicitudes a Excel"""
    from apps.solicitudes.models import Solicitud
    from .excel_service import ExcelService
    from datetime import date
    import base64

    empresa = contexto.get('empresa_contexto')
    if not empresa:
        return {'success': False, 'error': 'No hay empresa en contexto'}

    estado = params.get('estado')
    tipo = params.get('tipo')

    solicitudes = Solicitud.objects.filter(solicitante__empresa=empresa)

    if estado and estado != 'todos':
        solicitudes = solicitudes.filter(estado=estado)

    if tipo:
        solicitudes = solicitudes.filter(tipo=tipo)

    solicitudes = list(solicitudes.select_related('solicitante', 'aprobador').order_by('-created_at')[:500])

    if not solicitudes:
        return {'success': False, 'error': 'No hay solicitudes con los filtros especificados'}

    buffer = ExcelService.generar_reporte_solicitudes(solicitudes, empresa.razon_social)
    excel_base64 = base64.b64encode(buffer.getvalue()).decode()

    return {
        'success': True,
        'mensaje': f'Reporte de solicitudes: {len(solicitudes)} registros',
        'archivo': {
            'nombre': f'solicitudes_{date.today().strftime("%Y%m%d")}.xlsx',
            'contenido_base64': excel_base64,
            'tipo': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        }
    }
