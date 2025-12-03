"""
Servicios para gestión de KPIs y Evaluaciones
"""
from datetime import date, timedelta
from decimal import Decimal
from typing import Dict, List, Optional
from django.db.models import Avg, Sum, Count
from django.utils import timezone


class GestorKPIs:
    """Gestiona la asignación y seguimiento de KPIs"""
    
    def __init__(self, empleado):
        self.empleado = empleado
    
    def obtener_kpis_activos(self) -> List[Dict]:
        """Obtiene los KPIs activos del empleado"""
        from .models import AsignacionKPI
        
        kpis = AsignacionKPI.objects.filter(
            empleado=self.empleado,
            estado__in=['activo', 'pendiente']
        ).select_related('kpi_catalogo')
        
        return [{
            'id': str(kpi.id),
            'nombre': kpi.nombre_kpi,
            'periodo': kpi.periodo,
            'meta': float(kpi.meta),
            'valor_logrado': float(kpi.valor_logrado) if kpi.valor_logrado else None,
            'porcentaje': float(kpi.porcentaje_cumplimiento) if kpi.porcentaje_cumplimiento else None,
            'peso': float(kpi.peso),
            'estado': kpi.estado,
            'tiene_cambios_pendientes': kpi.cambios_pendientes is not None,
            'fecha_inicio': kpi.fecha_inicio.isoformat(),
            'fecha_fin': kpi.fecha_fin.isoformat(),
        } for kpi in kpis]
    
    def obtener_resumen_desempeno(self, periodo: str = None) -> Dict:
        """Obtiene resumen de desempeño del empleado"""
        from .models import AsignacionKPI, Evaluacion
        
        if not periodo:
            # Periodo actual (año-mes)
            periodo = date.today().strftime('%Y-%m')
        
        kpis = AsignacionKPI.objects.filter(
            empleado=self.empleado,
            periodo__startswith=periodo[:4]  # Filtrar por año
        )
        
        kpis_activos = kpis.filter(estado__in=['activo', 'evaluado'])
        
        promedio = kpis_activos.aggregate(
            promedio=Avg('porcentaje_cumplimiento')
        )['promedio']
        
        return {
            'empleado': {
                'id': str(self.empleado.id),
                'nombre': self.empleado.nombre_completo,
                'puesto': self.empleado.puesto,
            },
            'periodo': periodo,
            'kpis': {
                'total': kpis.count(),
                'activos': kpis_activos.count(),
                'pendientes_aprobacion': kpis.filter(estado='pendiente').count(),
                'promedio_cumplimiento': round(promedio, 2) if promedio else None,
            },
            'evaluaciones': self._obtener_evaluaciones_recientes(),
        }
    
    def _obtener_evaluaciones_recientes(self) -> List[Dict]:
        """Obtiene las últimas evaluaciones"""
        from .models import Evaluacion
        
        evaluaciones = Evaluacion.objects.filter(
            empleado=self.empleado
        ).order_by('-fecha_fin')[:5]
        
        return [{
            'id': str(e.id),
            'periodo': e.periodo,
            'tipo': e.tipo,
            'puntuacion_final': float(e.puntuacion_final) if e.puntuacion_final else None,
            'estado': e.estado,
        } for e in evaluaciones]


class GestorKPIsJefe:
    """Gestiona KPIs del equipo (para jefes)"""
    
    def __init__(self, jefe):
        self.jefe = jefe
    
    def obtener_kpis_equipo(self, periodo: str = None) -> List[Dict]:
        """Obtiene los KPIs de todos los subordinados"""
        from .models import AsignacionKPI
        
        subordinados = self.jefe.subordinados.filter(estado='activo')
        
        kpis = AsignacionKPI.objects.filter(
            empleado__in=subordinados,
            estado__in=['activo', 'pendiente', 'evaluado']
        ).select_related('empleado', 'kpi_catalogo')
        
        if periodo:
            kpis = kpis.filter(periodo=periodo)
        
        return [{
            'id': str(kpi.id),
            'empleado': kpi.empleado.nombre_completo,
            'empleado_id': str(kpi.empleado.id),
            'nombre_kpi': kpi.nombre_kpi,
            'periodo': kpi.periodo,
            'meta': float(kpi.meta),
            'valor_logrado': float(kpi.valor_logrado) if kpi.valor_logrado else None,
            'porcentaje': float(kpi.porcentaje_cumplimiento) if kpi.porcentaje_cumplimiento else None,
            'estado': kpi.estado,
            'requiere_aprobacion': kpi.estado == 'pendiente',
        } for kpi in kpis]
    
    def obtener_solicitudes_pendientes(self) -> List[Dict]:
        """Obtiene las solicitudes de cambio pendientes de aprobación"""
        from .models import AsignacionKPI
        
        subordinados = self.jefe.subordinados.filter(estado='activo')
        
        pendientes = AsignacionKPI.objects.filter(
            empleado__in=subordinados,
            estado='pendiente'
        ).select_related('empleado')
        
        return [{
            'id': str(kpi.id),
            'empleado': kpi.empleado.nombre_completo,
            'nombre_kpi': kpi.nombre_kpi,
            'cambios_propuestos': kpi.cambios_pendientes,
            'motivo': kpi.motivo_cambio,
            'fecha_solicitud': kpi.fecha_solicitud_cambio.isoformat() if kpi.fecha_solicitud_cambio else None,
        } for kpi in pendientes]
    
    def obtener_resumen_equipo(self) -> Dict:
        """Obtiene resumen de desempeño del equipo"""
        from .models import AsignacionKPI
        
        subordinados = self.jefe.subordinados.filter(estado='activo')
        
        resumen_empleados = []
        for emp in subordinados:
            kpis = AsignacionKPI.objects.filter(
                empleado=emp,
                estado__in=['activo', 'evaluado']
            )
            promedio = kpis.aggregate(avg=Avg('porcentaje_cumplimiento'))['avg']
            
            resumen_empleados.append({
                'id': str(emp.id),
                'nombre': emp.nombre_completo,
                'puesto': emp.puesto,
                'kpis_activos': kpis.count(),
                'promedio_cumplimiento': round(promedio, 2) if promedio else None,
            })
        
        # Ordenar por promedio descendente
        resumen_empleados.sort(
            key=lambda x: x['promedio_cumplimiento'] or 0, 
            reverse=True
        )
        
        return {
            'jefe': self.jefe.nombre_completo,
            'total_subordinados': subordinados.count(),
            'solicitudes_pendientes': AsignacionKPI.objects.filter(
                empleado__in=subordinados,
                estado='pendiente'
            ).count(),
            'empleados': resumen_empleados,
        }


def asignar_kpi(
    empleado,
    asignado_por,
    periodo: str,
    meta: Decimal,
    fecha_inicio: date,
    fecha_fin: date,
    kpi_catalogo=None,
    nombre_personalizado: str = '',
    descripcion: str = '',
    tipo_medicion: str = 'numero',
    peso: Decimal = Decimal('100'),
    es_mayor_mejor: bool = True,
) -> Dict:
    """Asigna un KPI a un empleado"""
    from .models import AsignacionKPI
    
    # Validar que asignado_por sea jefe del empleado o admin
    es_jefe = asignado_por and asignado_por.es_jefe_de(empleado)
    es_mismo = asignado_por and asignado_por.id == empleado.id
    
    if not es_jefe and not es_mismo:
        return {'success': False, 'error': 'Solo el jefe o el empleado pueden asignar KPIs'}
    
    try:
        asignacion = AsignacionKPI.objects.create(
            empleado=empleado,
            asignado_por=asignado_por,
            kpi_catalogo=kpi_catalogo,
            nombre_personalizado=nombre_personalizado,
            descripcion_personalizada=descripcion,
            tipo_medicion=tipo_medicion if not kpi_catalogo else '',
            periodo=periodo,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            meta=meta,
            peso=peso,
            es_mayor_mejor=es_mayor_mejor,
            estado='activo' if es_jefe else 'pendiente',  # Si lo crea empleado, requiere aprobación
        )
        
        estado_msg = 'activo' if es_jefe else 'pendiente de aprobación por el jefe'
        
        return {
            'success': True,
            'mensaje': f'KPI "{asignacion.nombre_kpi}" asignado a {empleado.nombre_completo} ({estado_msg})',
            'kpi_id': str(asignacion.id),
            'estado': asignacion.estado,
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}


def solicitar_cambio_kpi(
    asignacion_id,
    empleado,
    cambios: Dict,
    motivo: str = ''
) -> Dict:
    """Empleado solicita cambio en un KPI (requiere aprobación del jefe)"""
    from .models import AsignacionKPI
    
    try:
        kpi = AsignacionKPI.objects.get(pk=asignacion_id, empleado=empleado)
    except AsignacionKPI.DoesNotExist:
        return {'success': False, 'error': 'KPI no encontrado'}
    
    if kpi.estado not in ['activo', 'pendiente']:
        return {'success': False, 'error': 'El KPI no puede ser modificado en su estado actual'}
    
    # Guardar cambios pendientes
    kpi.cambios_pendientes = cambios
    kpi.motivo_cambio = motivo
    kpi.fecha_solicitud_cambio = timezone.now()
    kpi.estado = 'pendiente'
    kpi.save()
    
    return {
        'success': True,
        'mensaje': f'Solicitud de cambio enviada para aprobación del jefe',
        'cambios_propuestos': cambios,
    }


def aprobar_cambio_kpi(asignacion_id, jefe, aprobar: bool, comentario: str = '') -> Dict:
    """Jefe aprueba o rechaza cambios en un KPI"""
    from .models import AsignacionKPI
    
    try:
        kpi = AsignacionKPI.objects.get(pk=asignacion_id)
    except AsignacionKPI.DoesNotExist:
        return {'success': False, 'error': 'KPI no encontrado'}
    
    # Validar que es el jefe
    if not jefe.es_jefe_de(kpi.empleado):
        return {'success': False, 'error': 'Solo el jefe puede aprobar cambios'}
    
    if kpi.estado != 'pendiente' or not kpi.cambios_pendientes:
        return {'success': False, 'error': 'No hay cambios pendientes de aprobación'}
    
    if aprobar:
        # Aplicar los cambios
        cambios = kpi.cambios_pendientes
        if 'meta' in cambios:
            kpi.meta = Decimal(str(cambios['meta']))
        if 'nombre' in cambios:
            kpi.nombre_personalizado = cambios['nombre']
        if 'descripcion' in cambios:
            kpi.descripcion_personalizada = cambios['descripcion']
        if 'fecha_fin' in cambios:
            kpi.fecha_fin = cambios['fecha_fin']
        
        kpi.cambios_pendientes = None
        kpi.motivo_cambio = ''
        kpi.estado = 'activo'
        kpi.save()
        
        return {
            'success': True,
            'mensaje': f'Cambios aprobados para el KPI "{kpi.nombre_kpi}"',
        }
    else:
        # Rechazar cambios
        kpi.cambios_pendientes = None
        kpi.motivo_cambio = f'Rechazado: {comentario}' if comentario else 'Rechazado por el jefe'
        kpi.estado = 'activo'
        kpi.save()
        
        return {
            'success': True,
            'mensaje': f'Cambios rechazados para el KPI "{kpi.nombre_kpi}"',
        }


def registrar_avance_kpi(asignacion_id, empleado, valor, comentarios: str = '') -> Dict:
    """Registra un avance en el KPI"""
    from .models import AsignacionKPI, RegistroAvanceKPI
    
    try:
        kpi = AsignacionKPI.objects.get(pk=asignacion_id)
    except AsignacionKPI.DoesNotExist:
        return {'success': False, 'error': 'KPI no encontrado'}
    
    # Validar permisos (empleado dueño del KPI o su jefe)
    es_dueno = kpi.empleado.id == empleado.id
    es_jefe = empleado.es_jefe_de(kpi.empleado)
    
    if not es_dueno and not es_jefe:
        return {'success': False, 'error': 'No tienes permiso para registrar avances en este KPI'}
    
    valor_decimal = Decimal(str(valor))
    valor_anterior = kpi.valor_logrado
    
    # Crear registro de avance
    RegistroAvanceKPI.objects.create(
        asignacion=kpi,
        registrado_por=empleado,
        valor=valor_decimal,
        valor_anterior=valor_anterior,
        comentarios=comentarios,
    )
    
    # Actualizar valor en la asignación
    kpi.actualizar_valor(valor_decimal)
    
    return {
        'success': True,
        'mensaje': f'Avance registrado: {valor} ({kpi.porcentaje_cumplimiento:.1f}% de la meta)',
        'valor_anterior': float(valor_anterior) if valor_anterior else None,
        'valor_actual': float(valor_decimal),
        'porcentaje_cumplimiento': float(kpi.porcentaje_cumplimiento) if kpi.porcentaje_cumplimiento else None,
    }
