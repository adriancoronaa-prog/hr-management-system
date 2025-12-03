"""
Servicios de reportes y métricas para dashboards
"""
from decimal import Decimal
from datetime import date, timedelta
from typing import Dict, List, Optional
from django.db.models import Sum, Count, Avg, Q
from django.db.models.functions import Coalesce

from apps.empresas.models import Empresa
from apps.empleados.models import Empleado
from apps.empleados.services import (
    calcular_antiguedad, 
    obtener_dias_vacaciones_ley,
    calcular_aguinaldo,
    calcular_prima_vacacional
)
from apps.vacaciones.models import SolicitudVacaciones, PeriodoVacacional
from apps.nomina.models import PeriodoNomina, ReciboNomina


class MetricasEmpresa:
    """Calcula métricas de dashboard para una empresa"""
    
    def __init__(self, empresa: Empresa):
        self.empresa = empresa
        self.hoy = date.today()
    
    def obtener_resumen_completo(self) -> Dict:
        """Obtiene todas las métricas de la empresa"""
        return {
            'empresa': self._info_empresa(),
            'empleados': self._metricas_empleados(),
            'nomina': self._metricas_nomina(),
            'vacaciones': self._metricas_vacaciones(),
            'costos_proyectados': self._costos_proyectados(),
            'alertas': self._generar_alertas(),
            'fecha_generacion': self.hoy.isoformat()
        }
    
    def _info_empresa(self) -> Dict:
        return {
            'id': self.empresa.id,
            'razon_social': self.empresa.razon_social,
            'nombre_comercial': self.empresa.nombre_comercial or self.empresa.razon_social,
            'rfc': self.empresa.rfc,
            'regimen_fiscal': self.empresa.regimen_fiscal,
        }
    
    def _metricas_empleados(self) -> Dict:
        empleados = Empleado.objects.filter(empresa=self.empresa)
        activos = empleados.filter(estado='activo')
        
        # Antigüedad promedio
        antiguedades = []
        for emp in activos:
            ant = calcular_antiguedad(emp.fecha_ingreso)
            antiguedades.append(ant['total_dias'])
        
        antiguedad_promedio_dias = sum(antiguedades) / len(antiguedades) if antiguedades else 0
        antiguedad_promedio_anos = antiguedad_promedio_dias / 365
        
        # Salario promedio
        salarios = activos.exclude(salario_diario__isnull=True).values_list('salario_diario', flat=True)
        salario_promedio = sum(salarios) / len(salarios) if salarios else Decimal('0')
        
        # Por departamento
        por_departamento = activos.values('departamento').annotate(
            total=Count('id')
        ).order_by('-total')[:5]
        
        return {
            'total': empleados.count(),
            'activos': activos.count(),
            'inactivos': empleados.filter(estado='inactivo').count(),
            'bajas': empleados.filter(estado='baja').count(),
            'antiguedad_promedio_anos': round(antiguedad_promedio_anos, 1),
            'salario_diario_promedio': round(salario_promedio, 2),
            'salario_mensual_promedio': round(salario_promedio * 30, 2),
            'nomina_mensual_estimada': round(salario_promedio * 30 * activos.count(), 2),
            'por_departamento': list(por_departamento),
        }
    
    def _metricas_nomina(self) -> Dict:
        periodos = PeriodoNomina.objects.filter(empresa=self.empresa)
        ultimo_periodo = periodos.order_by('-fecha_fin').first()
        
        inicio_ano = date(self.hoy.year, 1, 1)
        periodos_ano = periodos.filter(fecha_inicio__gte=inicio_ano, estado='pagado')
        
        totales_ano = periodos_ano.aggregate(
            total_percepciones=Coalesce(Sum('total_percepciones'), Decimal('0')),
            total_deducciones=Coalesce(Sum('total_deducciones'), Decimal('0')),
            total_neto=Coalesce(Sum('total_neto'), Decimal('0')),
        )
        
        return {
            'periodos_procesados_ano': periodos_ano.count(),
            'total_percepciones_ano': totales_ano['total_percepciones'],
            'total_deducciones_ano': totales_ano['total_deducciones'],
            'total_neto_pagado_ano': totales_ano['total_neto'],
            'ultimo_periodo': {
                'fecha_pago': ultimo_periodo.fecha_pago.isoformat() if ultimo_periodo else None,
                'total_neto': ultimo_periodo.total_neto if ultimo_periodo else 0,
                'empleados': ultimo_periodo.total_empleados if ultimo_periodo else 0,
            } if ultimo_periodo else None
        }
    
    def _metricas_vacaciones(self) -> Dict:
        empleados_activos = Empleado.objects.filter(empresa=self.empresa, estado='activo')
        
        total_dias_pendientes = 0
        total_dias_tomados_ano = 0
        
        for emp in empleados_activos:
            periodos = PeriodoVacacional.objects.filter(
                empleado=emp,
                fecha_vencimiento__gte=self.hoy
            )
            for p in periodos:
                total_dias_pendientes += (p.dias_correspondientes - p.dias_tomados)
            
            solicitudes = SolicitudVacaciones.objects.filter(
                empleado=emp,
                estado='aprobada',
                fecha_inicio__year=self.hoy.year
            )
            for s in solicitudes:
                total_dias_tomados_ano += s.dias_solicitados
        
        return {
            'dias_pendientes_total': total_dias_pendientes,
            'dias_tomados_ano': total_dias_tomados_ano,
            'pasivo_vacaciones': round(total_dias_pendientes * self._salario_promedio_diario(), 2),
        }
    
    def _costos_proyectados(self) -> Dict:
        empleados_activos = Empleado.objects.filter(empresa=self.empresa, estado='activo')
        
        total_aguinaldo = Decimal('0')
        total_prima = Decimal('0')
        
        for emp in empleados_activos:
            if emp.salario_diario:
                ag = calcular_aguinaldo(emp.salario_diario, 15, emp.fecha_ingreso)
                total_aguinaldo += ag['monto_bruto']
                
                ant = calcular_antiguedad(emp.fecha_ingreso)
                dias_vac = obtener_dias_vacaciones_ley(ant['anos'])
                prima = calcular_prima_vacacional(dias_vac, emp.salario_diario)
                total_prima += prima
        
        nomina_mensual = self._metricas_empleados()['nomina_mensual_estimada']
        
        return {
            'aguinaldo_proyectado': round(total_aguinaldo, 2),
            'prima_vacacional_proyectada': round(total_prima, 2),
            'nomina_mensual': nomina_mensual,
            'costo_anual_estimado': round(nomina_mensual * 12 + total_aguinaldo + total_prima, 2),
        }
    
    def _generar_alertas(self) -> List[Dict]:
        alertas = []
        empleados = Empleado.objects.filter(empresa=self.empresa, estado='activo')
        
        for emp in empleados:
            periodos = PeriodoVacacional.objects.filter(
                empleado=emp,
                fecha_vencimiento__lte=self.hoy + timedelta(days=60),
                fecha_vencimiento__gt=self.hoy
            )
            for p in periodos:
                dias_restantes = p.dias_correspondientes - p.dias_tomados
                if dias_restantes > 0:
                    alertas.append({
                        'tipo': 'vacaciones_por_vencer',
                        'nivel': 'warning',
                        'empleado': emp.nombre_completo,
                        'mensaje': f'{dias_restantes} días de vacaciones vencen el {p.fecha_vencimiento}',
                    })
        
        return alertas[:10]
    
    def _salario_promedio_diario(self) -> Decimal:
        empleados = Empleado.objects.filter(empresa=self.empresa, estado='activo')
        salarios = empleados.exclude(salario_diario__isnull=True).values_list('salario_diario', flat=True)
        return sum(salarios) / len(salarios) if salarios else Decimal('0')


class MetricasEmpleado:
    """Calcula métricas de dashboard para un empleado"""
    
    def __init__(self, empleado: Empleado):
        self.empleado = empleado
        self.hoy = date.today()
        self.antiguedad = calcular_antiguedad(empleado.fecha_ingreso)
    
    def obtener_resumen_completo(self, incluir_liquidacion: bool = False) -> Dict:
        resumen = {
            'empleado': self._info_empleado(),
            'antiguedad': self._info_antiguedad(),
            'salario': self._info_salario(),
            'vacaciones': self._info_vacaciones(),
            'prestaciones': self._info_prestaciones(),
            'historial_nomina': self._historial_nomina(),
            'fecha_generacion': self.hoy.isoformat()
        }
        
        if incluir_liquidacion:
            resumen['liquidacion'] = self.calcular_liquidacion()
        
        return resumen
    
    def _info_empleado(self) -> Dict:
        return {
            'id': self.empleado.id,
            'nombre_completo': self.empleado.nombre_completo,
            'curp': self.empleado.curp,
            'rfc': self.empleado.rfc,
            'nss': self.empleado.nss_imss,
            'fecha_ingreso': self.empleado.fecha_ingreso.isoformat(),
            'puesto': self.empleado.puesto,
            'departamento': self.empleado.departamento,
            'tipo_contrato': self.empleado.tipo_contrato,
            'estado': self.empleado.estado,
            'empresa': self.empleado.empresa.razon_social if self.empleado.empresa else None,
        }
    
    def _info_antiguedad(self) -> Dict:
        return {
            'anos': self.antiguedad['anos'],
            'meses': self.antiguedad['meses'],
            'dias': self.antiguedad['dias'],
            'total_dias': self.antiguedad['total_dias'],
            'descripcion': f"{self.antiguedad['anos']} años, {self.antiguedad['meses']} meses, {self.antiguedad['dias']} días"
        }
    
    def _info_salario(self) -> Dict:
        sd = self.empleado.salario_diario or Decimal('0')
        return {
            'salario_diario': sd,
            'salario_semanal': round(sd * 7, 2),
            'salario_quincenal': round(sd * 15, 2),
            'salario_mensual': round(sd * 30, 2),
            'salario_anual': round(sd * 365, 2),
        }
    
    def _info_vacaciones(self) -> Dict:
        dias_ley = obtener_dias_vacaciones_ley(self.antiguedad['anos'])
        
        solicitudes = SolicitudVacaciones.objects.filter(
            empleado=self.empleado,
            estado='aprobada',
            fecha_inicio__year=self.hoy.year
        )
        dias_tomados = sum(s.dias_solicitados for s in solicitudes)
        
        periodos = PeriodoVacacional.objects.filter(
            empleado=self.empleado,
            fecha_vencimiento__gte=self.hoy
        )
        dias_pendientes = sum(p.dias_correspondientes - p.dias_tomados for p in periodos)
        
        sd = self.empleado.salario_diario or Decimal('0')
        prima = calcular_prima_vacacional(dias_ley, sd)
        
        return {
            'dias_por_ley': dias_ley,
            'dias_tomados_ano': dias_tomados,
            'dias_pendientes': max(dias_pendientes, 0),
            'prima_vacacional_porcentaje': 25,
            'prima_vacacional_monto': round(prima, 2),
            'proximo_aniversario': self._proximo_aniversario(),
        }
    
    def _info_prestaciones(self) -> Dict:
        sd = self.empleado.salario_diario or Decimal('0')
        
        aguinaldo = calcular_aguinaldo(sd, 15, self.empleado.fecha_ingreso)
        
        dias_vac = obtener_dias_vacaciones_ley(self.antiguedad['anos'])
        prima_vac = calcular_prima_vacacional(dias_vac, sd)
        
        return {
            'aguinaldo': {
                'dias': 15,
                'monto': round(aguinaldo['monto_bruto'], 2),
                'es_proporcional': aguinaldo['es_proporcional'],
                'dias_trabajados': aguinaldo['dias_trabajados_ano'],
            },
            'prima_vacacional': {
                'dias_vacaciones': dias_vac,
                'porcentaje': 25,
                'monto': round(prima_vac, 2),
            },
        }
    
    def _historial_nomina(self) -> Dict:
        recibos = ReciboNomina.objects.filter(
            empleado=self.empleado
        ).order_by('-periodo__fecha_fin')[:12]
        
        total_percepciones = sum(r.total_percepciones or 0 for r in recibos)
        total_deducciones = sum(r.total_deducciones or 0 for r in recibos)
        
        return {
            'recibos_count': recibos.count(),
            'total_percepciones_12m': round(total_percepciones, 2),
            'total_deducciones_12m': round(total_deducciones, 2),
            'promedio_neto_mensual': round((total_percepciones - total_deducciones) / 12, 2) if recibos.count() > 0 else 0,
        }
    
    def _proximo_aniversario(self) -> str:
        fecha_ingreso = self.empleado.fecha_ingreso
        proximo = date(self.hoy.year, fecha_ingreso.month, fecha_ingreso.day)
        if proximo <= self.hoy:
            proximo = date(self.hoy.year + 1, fecha_ingreso.month, fecha_ingreso.day)
        return proximo.isoformat()
    
    def calcular_liquidacion(self, fecha_baja: date = None, es_despido_injustificado: bool = True) -> Dict:
        """
        Calcula liquidación/finiquito según LFT
        
        Finiquito (renuncia voluntaria o despido justificado):
        - Salarios pendientes
        - Aguinaldo proporcional
        - Vacaciones no disfrutadas + prima vacacional
        
        Liquidación (despido injustificado) = Finiquito +:
        - 3 meses de salario (indemnización constitucional)
        - 20 días por año trabajado (indemnización Art. 50 LFT)
        - Prima de antigüedad (12 días por año, tope 2 salarios mínimos)
        """
        if fecha_baja is None:
            fecha_baja = self.hoy
        
        sd = self.empleado.salario_diario or Decimal('0')
        sdi = sd * Decimal('1.0493')  # Factor de integración aproximado
        
        ant = calcular_antiguedad(self.empleado.fecha_ingreso, fecha_baja)
        anos_completos = ant['anos']
        
        # === FINIQUITO (siempre aplica) ===
        aguinaldo = calcular_aguinaldo(sd, 15, self.empleado.fecha_ingreso, fecha_baja)
        
        dias_vac_ley = obtener_dias_vacaciones_ley(anos_completos)
        dias_del_ano = (fecha_baja - date(fecha_baja.year, 1, 1)).days + 1
        
        dias_vac_proporcional = dias_vac_ley * Decimal(dias_del_ano) / Decimal('365')
        vacaciones_monto = round(sd * dias_vac_proporcional, 2)
        prima_vac = round(vacaciones_monto * Decimal('0.25'), 2)
        
        finiquito = {
            'aguinaldo_proporcional': round(aguinaldo['monto_bruto'], 2),
            'vacaciones_proporcionales_dias': round(dias_vac_proporcional, 2),
            'vacaciones_proporcionales_monto': vacaciones_monto,
            'prima_vacacional': prima_vac,
            'subtotal_finiquito': round(
                aguinaldo['monto_bruto'] + vacaciones_monto + prima_vac, 2
            ),
        }
        
        # === LIQUIDACIÓN (solo despido injustificado) ===
        liquidacion = {
            'aplica': es_despido_injustificado,
            'indemnizacion_3_meses': Decimal('0'),
            'indemnizacion_20_dias_ano': Decimal('0'),
            'prima_antiguedad': Decimal('0'),
            'subtotal_liquidacion': Decimal('0'),
        }
        
        if es_despido_injustificado:
            indem_3_meses = round(sdi * 90, 2)
            indem_20_dias = round(sdi * 20 * anos_completos, 2)
            
            salario_minimo = Decimal('248.93')  # 2024
            tope_prima = salario_minimo * 2
            salario_prima = min(sd, tope_prima)
            prima_antiguedad = round(salario_prima * 12 * anos_completos, 2)
            
            liquidacion = {
                'aplica': True,
                'indemnizacion_3_meses': indem_3_meses,
                'indemnizacion_20_dias_ano': indem_20_dias,
                'anos_para_calculo': anos_completos,
                'prima_antiguedad': prima_antiguedad,
                'subtotal_liquidacion': round(
                    indem_3_meses + indem_20_dias + prima_antiguedad, 2
                ),
            }
        
        total = finiquito['subtotal_finiquito'] + liquidacion['subtotal_liquidacion']
        
        return {
            'fecha_baja': fecha_baja.isoformat(),
            'tipo': 'Liquidación (Despido Injustificado)' if es_despido_injustificado else 'Finiquito (Renuncia/Despido Justificado)',
            'salario_diario': sd,
            'salario_diario_integrado': round(sdi, 2),
            'antiguedad': ant,
            'finiquito': finiquito,
            'liquidacion': liquidacion,
            'total_a_pagar': round(total, 2),
            'desglose': {'concepto': []},
        }
