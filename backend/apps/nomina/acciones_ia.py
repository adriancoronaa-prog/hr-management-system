"""
Acciones de IA para el módulo de Nómina
"""
from typing import Dict
from datetime import date, datetime
from decimal import Decimal


def registrar_acciones():
    """Registra las acciones de nómina en el registro central"""
    from apps.chat.acciones_registry import registrar_accion
    
    registrar_accion(
        nombre='crear_periodo_nomina',
        descripcion='Crea periodos de nómina',
        permisos=['es_admin', 'es_rrhh'],
        parametros={
            'tipo': 'Tipo: semanal, quincenal, mensual',
            'año': 'Año del periodo',
        },
        ejemplo='Crea los periodos quincenales del 2025',
        funcion=accion_crear_periodo,
        confirmacion_requerida=True
    )
    
    registrar_accion(
        nombre='ver_periodos_nomina',
        descripcion='Lista los periodos de nómina',
        permisos=['es_admin', 'es_rrhh'],
        parametros={
            'año': '(Opcional) Filtrar por año',
            'estado': '(Opcional) Filtrar por estado',
        },
        ejemplo='Muéstrame los periodos de nómina',
        funcion=accion_ver_periodos
    )
    
    registrar_accion(
        nombre='registrar_incidencia',
        descripcion='Registra una incidencia (falta, hora extra, permiso)',
        permisos=['es_admin', 'es_rrhh', 'es_jefe'],
        parametros={
            'empleado_nombre': 'Nombre del empleado',
            'empleado_id': '(Opcional) ID del empleado',
            'tipo': 'Tipo: falta, hora_extra, permiso, incapacidad, vacaciones',
            'fecha': '(Opcional) Fecha YYYY-MM-DD, default: hoy',
            'cantidad': '(Opcional) Cantidad, default: 1',
            'descripcion': '(Opcional) Descripción',
        },
        ejemplo='Registra 2 horas extra para Juan Pérez hoy',
        funcion=accion_registrar_incidencia,
        confirmacion_requerida=True
    )
    
    registrar_accion(
        nombre='ver_incidencias',
        descripcion='Muestra las incidencias',
        permisos=['es_admin', 'es_rrhh', 'es_jefe', 'es_empleado'],
        parametros={
            'empleado_id': '(Opcional) ID del empleado',
            'mes': '(Opcional) Mes a consultar',
        },
        ejemplo='Muéstrame las incidencias del mes',
        funcion=accion_ver_incidencias
    )
    
    registrar_accion(
        nombre='calcular_nomina',
        descripcion='Calcula la nómina de un periodo',
        permisos=['es_admin', 'es_rrhh'],
        parametros={
            'periodo_id': '(Opcional) ID del periodo',
        },
        ejemplo='Calcula la nómina del periodo actual',
        funcion=accion_calcular_nomina,
        confirmacion_requerida=True
    )
    
    registrar_accion(
        nombre='ver_pre_nomina',
        descripcion='Muestra el resumen de la nómina',
        permisos=['es_admin', 'es_rrhh'],
        parametros={
            'periodo_id': '(Opcional) ID del periodo',
        },
        ejemplo='Muéstrame la pre-nómina',
        funcion=accion_ver_pre_nomina
    )
    
    registrar_accion(
        nombre='ver_mi_recibo',
        descripcion='Muestra el recibo de nómina del empleado',
        permisos=['es_empleado', 'es_jefe', 'es_rrhh', 'es_admin'],
        parametros={
            'periodo_id': '(Opcional) ID del periodo',
        },
        ejemplo='Muéstrame mi recibo de nómina',
        funcion=accion_ver_mi_recibo
    )
    
    registrar_accion(
        nombre='autorizar_nomina',
        descripcion='Autoriza la nómina para pago',
        permisos=['es_admin', 'es_rrhh'],
        parametros={
            'periodo_id': 'ID del periodo',
        },
        ejemplo='Autoriza la nómina',
        funcion=accion_autorizar_nomina,
        confirmacion_requerida=True
    )
    
    registrar_accion(
        nombre='generar_dispersion',
        descripcion='Genera archivo de dispersión bancaria',
        permisos=['es_admin', 'es_rrhh'],
        parametros={
            'periodo_id': 'ID del periodo',
        },
        ejemplo='Genera la dispersión bancaria',
        funcion=accion_generar_dispersion,
        confirmacion_requerida=True
    )


# ============ FUNCIONES ============

def accion_crear_periodo(usuario, params: Dict, contexto: Dict) -> Dict:
    """Crea periodos de nómina"""
    from apps.nomina.models import PeriodoNomina
    from datetime import timedelta
    
    tipo = params.get('tipo', 'quincenal')
    año = int(params.get('año', date.today().year))
    empresa = contexto.get('empresa_contexto')
    
    if not empresa:
        return {'success': False, 'error': 'No hay empresa en contexto'}
    
    if tipo not in ['semanal', 'quincenal', 'mensual']:
        return {'success': False, 'error': 'Tipo debe ser: semanal, quincenal o mensual'}
    
    periodos_creados = []
    
    if tipo == 'quincenal':
        for num in range(1, 25):
            mes = (num + 1) // 2
            if num % 2 == 1:
                fecha_inicio = date(año, mes, 1)
                fecha_fin = date(año, mes, 15)
            else:
                fecha_inicio = date(año, mes, 16)
                if mes == 12:
                    fecha_fin = date(año, 12, 31)
                else:
                    fecha_fin = date(año, mes + 1, 1) - timedelta(days=1)
            
            periodo, created = PeriodoNomina.objects.get_or_create(
                empresa=empresa,
                tipo_periodo=tipo,
                año=año,
                numero_periodo=num,
                defaults={
                    'fecha_inicio': fecha_inicio,
                    'fecha_fin': fecha_fin,
                    'fecha_pago': fecha_fin,
                    'estado': 'abierto',
                }
            )
            if created:
                periodos_creados.append(num)
    
    elif tipo == 'mensual':
        for mes in range(1, 13):
            fecha_inicio = date(año, mes, 1)
            if mes == 12:
                fecha_fin = date(año, 12, 31)
            else:
                fecha_fin = date(año, mes + 1, 1) - timedelta(days=1)
            
            periodo, created = PeriodoNomina.objects.get_or_create(
                empresa=empresa,
                tipo_periodo=tipo,
                año=año,
                numero_periodo=mes,
                defaults={
                    'fecha_inicio': fecha_inicio,
                    'fecha_fin': fecha_fin,
                    'fecha_pago': fecha_fin,
                    'estado': 'abierto',
                }
            )
            if created:
                periodos_creados.append(mes)
    
    return {
        'success': True,
        'mensaje': f'Se crearon {len(periodos_creados)} periodos {tipo}es para {año}',
        'periodos_creados': len(periodos_creados),
    }


def accion_ver_periodos(usuario, params: Dict, contexto: Dict) -> Dict:
    """Lista periodos de nómina"""
    from apps.nomina.models import PeriodoNomina
    
    empresa = contexto.get('empresa_contexto')
    año = params.get('año')
    estado = params.get('estado')
    
    periodos = PeriodoNomina.objects.all()
    
    if empresa:
        periodos = periodos.filter(empresa=empresa)
    
    if año:
        periodos = periodos.filter(año=int(año))
    
    if estado:
        periodos = periodos.filter(estado=estado)
    
    periodos = periodos.order_by('-año', '-numero_periodo')[:20]
    
    lista = [{
        'id': str(p.id),
        'nombre': f"{p.tipo_periodo.capitalize()} {p.numero_periodo}/{p.año}",
        'tipo': p.tipo_periodo,
        'fecha_inicio': p.fecha_inicio.strftime('%d/%m/%Y'),
        'fecha_fin': p.fecha_fin.strftime('%d/%m/%Y'),
        'estado': p.estado,
        'total_neto': float(p.total_neto or 0),
        'empleados': p.total_empleados or 0,
    } for p in periodos]
    
    return {
        'success': True,
        'mensaje': f'Se encontraron {len(lista)} periodos',
        'periodos': lista,
    }


def accion_registrar_incidencia(usuario, params: Dict, contexto: Dict) -> Dict:
    """Registra una incidencia"""
    from apps.empleados.models import Empleado
    from apps.nomina.models import IncidenciaNomina
    from django.db.models import Q
    
    empleado_id = params.get('empleado_id')
    empleado_nombre = params.get('empleado_nombre') or params.get('nombre') or params.get('empleado')
    tipo = params.get('tipo')
    fecha_str = params.get('fecha', date.today().isoformat())
    cantidad = params.get('cantidad', 1)
    descripcion = params.get('descripcion', '')
    empresa = contexto.get('empresa_contexto')
    
    if not tipo:
        return {'success': False, 'error': 'Se requiere el tipo de incidencia'}
    
    # Buscar empleado por ID o por nombre
    empleado = None
    
    if empleado_id:
        try:
            empleado = Empleado.objects.get(pk=empleado_id)
        except (Empleado.DoesNotExist, ValueError):
            pass
    
    if not empleado and empleado_nombre:
        # Buscar por nombre
        query = Q()
        for palabra in empleado_nombre.split():
            query |= Q(nombre__icontains=palabra)
            query |= Q(apellido_paterno__icontains=palabra)
            query |= Q(apellido_materno__icontains=palabra)
        
        empleados = Empleado.objects.filter(query)
        
        if empresa:
            empleados = empleados.filter(empresa=empresa)
        
        if empleados.count() == 1:
            empleado = empleados.first()
        elif empleados.count() > 1:
            nombres = [e.nombre_completo for e in empleados[:5]]
            return {
                'success': False, 
                'error': f'Se encontraron varios empleados: {", ".join(nombres)}. Sé más específico.'
            }
        else:
            return {'success': False, 'error': f'No se encontró empleado "{empleado_nombre}"'}
    
    if not empleado:
        return {'success': False, 'error': 'Especifica el empleado (nombre o ID)'}
    
    # Parsear fecha
    if isinstance(fecha_str, str):
        try:
            fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
        except ValueError:
            fecha = date.today()
    else:
        fecha = fecha_str
    
    # Normalizar tipo
    tipo_lower = tipo.lower().replace(' ', '_')
    tipos_validos = ['falta', 'hora_extra', 'permiso', 'incapacidad', 'vacaciones', 'prima_dominical', 'festivo']
    
    if tipo_lower not in tipos_validos:
        # Intentar mapear
        if 'extra' in tipo_lower:
            tipo_lower = 'hora_extra'
        elif 'falta' in tipo_lower or 'ausencia' in tipo_lower:
            tipo_lower = 'falta'
        elif 'permiso' in tipo_lower:
            tipo_lower = 'permiso'
        elif 'incapacidad' in tipo_lower or 'enferm' in tipo_lower:
            tipo_lower = 'incapacidad'
        elif 'vacacion' in tipo_lower:
            tipo_lower = 'vacaciones'
        else:
            return {'success': False, 'error': f'Tipo inválido. Usa: {", ".join(tipos_validos)}'}
    
    incidencia = IncidenciaNomina.objects.create(
        empleado=empleado,
        tipo=tipo_lower,
        fecha_inicio=fecha,
        fecha_fin=fecha,
        cantidad=Decimal(str(cantidad)),
        descripcion=descripcion,
        aplicado=False,
    )
    
    return {
        'success': True,
        'mensaje': f'Incidencia "{tipo_lower}" registrada para {empleado.nombre_completo} ({fecha.strftime("%d/%m/%Y")})',
        'incidencia_id': str(incidencia.id),
        'empleado': empleado.nombre_completo,
    }


def accion_ver_incidencias(usuario, params: Dict, contexto: Dict) -> Dict:
    """Muestra incidencias"""
    from apps.nomina.models import IncidenciaNomina
    
    empleado_id = params.get('empleado_id')
    mes = params.get('mes')
    empresa = contexto.get('empresa_contexto')
    
    hoy = date.today()
    mes_num = int(mes) if mes else hoy.month
    año = hoy.year
    
    incidencias = IncidenciaNomina.objects.filter(
        fecha_inicio__month=mes_num,
        fecha_inicio__year=año
    )
    
    if empleado_id:
        incidencias = incidencias.filter(empleado_id=empleado_id)
    elif empresa:
        incidencias = incidencias.filter(empleado__empresa=empresa)
    
    incidencias = incidencias.order_by('-fecha_inicio')[:30]
    
    lista = [{
        'id': str(i.id),
        'empleado': i.empleado.nombre_completo,
        'tipo': i.tipo,
        'fecha': i.fecha_inicio.strftime('%d/%m/%Y'),
        'cantidad': float(i.cantidad or 1),
        'aplicado': 'Sí' if i.aplicado else 'No',
    } for i in incidencias]
    
    return {
        'success': True,
        'mensaje': f'Se encontraron {len(lista)} incidencias en {mes_num}/{año}',
        'incidencias': lista,
    }


def accion_calcular_nomina(usuario, params: Dict, contexto: Dict) -> Dict:
    """Calcula la nómina de un periodo"""
    from apps.nomina.models import PeriodoNomina, ReciboNomina
    from apps.empleados.models import Empleado
    from django.utils import timezone
    
    periodo_id = params.get('periodo_id')
    empresa = contexto.get('empresa_contexto')
    
    if not periodo_id:
        periodo = PeriodoNomina.objects.filter(
            empresa=empresa
        ).order_by('-fecha_inicio').first()
        
        if not periodo:
            return {'success': False, 'error': 'No hay periodos disponibles'}
    else:
        try:
            periodo = PeriodoNomina.objects.get(pk=periodo_id)
        except PeriodoNomina.DoesNotExist:
            return {'success': False, 'error': 'Periodo no encontrado'}
    
    empleados = Empleado.objects.filter(empresa=periodo.empresa, estado='activo')
    
    if not empleados.exists():
        return {'success': False, 'error': 'No hay empleados activos'}
    
    total_neto = Decimal('0')
    total_percepciones = Decimal('0')
    total_deducciones = Decimal('0')
    recibos_creados = 0
    
    for emp in empleados:
        salario_diario = emp.salario_diario or Decimal('0')
        
        # Días como entero
        if periodo.tipo_periodo == 'quincenal':
            dias = 15
        elif periodo.tipo_periodo == 'semanal':
            dias = 7
        else:
            dias = 30
        
        sueldo_bruto = salario_diario * dias
        sdi = salario_diario * Decimal('1.0493')
        isr = (sueldo_bruto * Decimal('0.10')).quantize(Decimal('0.01'))
        imss = (sueldo_bruto * Decimal('0.02125')).quantize(Decimal('0.01'))
        deducciones_total = isr + imss
        neto = sueldo_bruto - deducciones_total
        
        recibo, created = ReciboNomina.objects.update_or_create(
            periodo=periodo,
            empleado=emp,
            defaults={
                'estado': 'calculado',
                'salario_diario': salario_diario,
                'salario_base_cotizacion': sdi,
                'dias_trabajados': dias,  # Integer
                'dias_pagados': dias,     # Integer
                'total_percepciones': sueldo_bruto,
                'total_percepciones_gravadas': sueldo_bruto,
                'total_percepciones_exentas': Decimal('0'),
                'total_deducciones': deducciones_total,
                'total_otros_pagos': Decimal('0'),
                'neto_a_pagar': neto,
                'base_gravable_isr': sueldo_bruto,
                'isr_antes_subsidio': isr,
                'subsidio_aplicado': Decimal('0'),
                'isr_retenido': isr,
                'cuota_imss_obrera': imss,
                'uuid_cfdi': '',
                'xml_cfdi': '',
                'pdf_cfdi': '',
                'referencia_pago': '',
            }
        )
        
        if created:
            recibos_creados += 1
        total_neto += neto
        total_percepciones += sueldo_bruto
        total_deducciones += deducciones_total
    
    periodo.total_empleados = empleados.count()
    periodo.total_percepciones = total_percepciones
    periodo.total_deducciones = total_deducciones
    periodo.total_neto = total_neto
    periodo.estado = 'calculado'
    periodo.fecha_calculo = timezone.now()
    periodo.save()
    
    return {
        'success': True,
        'mensaje': f'Nómina calculada: {empleados.count()} empleados, neto ${float(total_neto):,.2f}',
        'empleados': empleados.count(),
        'total_percepciones': float(total_percepciones),
        'total_deducciones': float(total_deducciones),
        'total_neto': float(total_neto),
    }


def accion_ver_pre_nomina(usuario, params: Dict, contexto: Dict) -> Dict:
    """Muestra resumen de nómina"""
    from apps.nomina.models import PeriodoNomina, ReciboNomina
    
    periodo_id = params.get('periodo_id')
    empresa = contexto.get('empresa_contexto')
    
    if not periodo_id:
        periodo = PeriodoNomina.objects.filter(
            empresa=empresa
        ).order_by('-fecha_inicio').first()
        
        if not periodo:
            return {'success': False, 'error': 'No hay periodos'}
    else:
        try:
            periodo = PeriodoNomina.objects.get(pk=periodo_id)
        except PeriodoNomina.DoesNotExist:
            return {'success': False, 'error': 'Periodo no encontrado'}
    
    recibos = ReciboNomina.objects.filter(periodo=periodo).order_by('empleado__apellido_paterno')
    
    lista = [{
        'empleado': r.empleado.nombre_completo,
        'dias': float(r.dias_trabajados or 0),
        'percepciones': float(r.total_percepciones or 0),
        'deducciones': float(r.total_deducciones or 0),
        'neto': float(r.neto_a_pagar or 0),
    } for r in recibos]
    
    return {
        'success': True,
        'mensaje': f'Nómina {periodo.tipo_periodo} {periodo.numero_periodo}/{periodo.año}: {len(lista)} empleados',
        'periodo': f"{periodo.tipo_periodo.capitalize()} {periodo.numero_periodo}/{periodo.año}",
        'estado': periodo.estado,
        'totales': {
            'percepciones': float(periodo.total_percepciones or 0),
            'deducciones': float(periodo.total_deducciones or 0),
            'neto': float(periodo.total_neto or 0),
        },
        'recibos': lista,
    }


def accion_ver_mi_recibo(usuario, params: Dict, contexto: Dict) -> Dict:
    """Muestra recibo del empleado"""
    from apps.nomina.models import ReciboNomina
    
    if not hasattr(usuario, 'empleado') or not usuario.empleado:
        return {'success': False, 'error': 'No tienes perfil de empleado'}
    
    empleado = usuario.empleado
    periodo_id = params.get('periodo_id')
    
    if periodo_id:
        try:
            recibo = ReciboNomina.objects.get(periodo_id=periodo_id, empleado=empleado)
        except ReciboNomina.DoesNotExist:
            return {'success': False, 'error': 'No hay recibo para este periodo'}
    else:
        recibo = ReciboNomina.objects.filter(empleado=empleado).order_by('-periodo__fecha_fin').first()
        if not recibo:
            return {'success': False, 'error': 'No tienes recibos'}
    
    return {
        'success': True,
        'mensaje': f'Recibo {recibo.periodo.tipo_periodo} {recibo.periodo.numero_periodo}/{recibo.periodo.año}',
        'recibo': {
            'periodo': f"{recibo.periodo.tipo_periodo.capitalize()} {recibo.periodo.numero_periodo}/{recibo.periodo.año}",
            'empleado': empleado.nombre_completo,
            'dias': float(recibo.dias_trabajados or 0),
            'percepciones': float(recibo.total_percepciones or 0),
            'deducciones': float(recibo.total_deducciones or 0),
            'neto': float(recibo.neto_a_pagar or 0),
        }
    }


def accion_autorizar_nomina(usuario, params: Dict, contexto: Dict) -> Dict:
    """Autoriza la nómina y notifica a empleados"""
    from apps.nomina.models import PeriodoNomina, ReciboNomina
    from django.utils import timezone

    periodo_id = params.get('periodo_id')

    if not periodo_id:
        return {'success': False, 'error': 'Especifica periodo_id'}

    try:
        periodo = PeriodoNomina.objects.get(pk=periodo_id)
    except PeriodoNomina.DoesNotExist:
        return {'success': False, 'error': 'Periodo no encontrado'}

    periodo.estado = 'autorizado'
    periodo.autorizado_por = usuario.empleado if hasattr(usuario, 'empleado') else None
    periodo.fecha_autorizacion = timezone.now()
    periodo.save()

    # Notificar a empleados que su recibo esta disponible
    notificados = 0
    try:
        from apps.notificaciones.services import NotificacionService
        recibos = ReciboNomina.objects.filter(periodo=periodo).select_related('empleado')
        for recibo in recibos:
            if recibo.empleado:
                notif = NotificacionService.notificar_recibo_nomina(recibo.empleado, recibo)
                if notif:
                    notificados += 1
    except Exception:
        pass  # Notificaciones opcionales

    return {
        'success': True,
        'mensaje': f'Nomina autorizada: ${periodo.total_neto:,.2f}. {notificados} empleados notificados.',
        'total_neto': float(periodo.total_neto or 0),
        'notificados': notificados,
    }


def accion_generar_dispersion(usuario, params: Dict, contexto: Dict) -> Dict:
    """Genera dispersión bancaria"""
    from apps.nomina.models import PeriodoNomina, ReciboNomina
    
    periodo_id = params.get('periodo_id')
    
    if not periodo_id:
        return {'success': False, 'error': 'Especifica periodo_id'}
    
    try:
        periodo = PeriodoNomina.objects.get(pk=periodo_id)
    except PeriodoNomina.DoesNotExist:
        return {'success': False, 'error': 'Periodo no encontrado'}
    
    if periodo.estado != 'autorizado':
        return {'success': False, 'error': 'La nómina debe estar autorizada'}
    
    recibos = ReciboNomina.objects.filter(periodo=periodo, neto_a_pagar__gt=0)
    total = sum(r.neto_a_pagar or Decimal('0') for r in recibos)
    
    periodo.estado = 'pagado'
    periodo.save()
    
    return {
        'success': True,
        'mensaje': f'Dispersión generada: {recibos.count()} movimientos por ${total:,.2f}',
        'movimientos': recibos.count(),
        'total': float(total),
    }