"""
Servicio de cálculos de nómina mexicana
Implementa cálculos según LFT, LISR y LSS
"""
from decimal import Decimal, ROUND_HALF_UP
from datetime import date, timedelta
from typing import Dict, Optional, Tuple
from django.db.models import Sum


class CalculadoraNomina:
    """
    Calculadora de nómina mexicana
    Implementa ISR Art. 96, cuotas IMSS, y prestaciones de ley
    """
    
    def __init__(self, año: int = None, periodicidad: str = 'quincenal'):
        from .models import TablaISR, TablaSubsidio, ParametrosIMSS
        
        self.año = año or date.today().year
        self.periodicidad = periodicidad
        
        # Cargar tablas vigentes
        self.tablas_isr = TablaISR.objects.filter(
            año=self.año, 
            periodicidad=periodicidad
        ).order_by('limite_inferior')
        
        self.tablas_subsidio = TablaSubsidio.objects.filter(
            año=self.año,
            periodicidad=periodicidad
        ).order_by('limite_inferior')
        
        try:
            self.params_imss = ParametrosIMSS.objects.get(vigente=True)
        except ParametrosIMSS.DoesNotExist:
            self.params_imss = None
    
    # ============ CÁLCULO DE ISR ============
    
    def calcular_isr(self, ingreso_gravable: Decimal) -> Dict:
        """
        Calcula ISR según Art. 96 LISR
        Retorna diccionario con desglose del cálculo
        """
        ingreso = Decimal(str(ingreso_gravable))
        
        if not self.tablas_isr.exists():
            return {
                'error': f'No hay tablas ISR para {self.año} {self.periodicidad}',
                'isr': Decimal('0'),
                'subsidio': Decimal('0'),
                'isr_neto': Decimal('0')
            }
        
        # Encontrar rango en tabla ISR
        rango_isr = None
        for rango in self.tablas_isr:
            if rango.limite_inferior <= ingreso <= rango.limite_superior:
                rango_isr = rango
                break
        
        if not rango_isr:
            # Si excede el último rango, usar el último
            rango_isr = self.tablas_isr.last()
        
        # Cálculo de ISR
        excedente = ingreso - rango_isr.limite_inferior
        impuesto_marginal = excedente * (rango_isr.porcentaje_excedente / 100)
        isr_antes_subsidio = rango_isr.cuota_fija + impuesto_marginal
        
        # Calcular subsidio al empleo
        subsidio = self._calcular_subsidio(ingreso)
        
        # ISR neto (puede ser negativo si subsidio > ISR)
        isr_neto = max(isr_antes_subsidio - subsidio, Decimal('0'))
        
        return {
            'ingreso_gravable': ingreso.quantize(Decimal('0.01')),
            'limite_inferior': rango_isr.limite_inferior,
            'excedente': excedente.quantize(Decimal('0.01')),
            'porcentaje': rango_isr.porcentaje_excedente,
            'impuesto_marginal': impuesto_marginal.quantize(Decimal('0.01')),
            'cuota_fija': rango_isr.cuota_fija,
            'isr_antes_subsidio': isr_antes_subsidio.quantize(Decimal('0.01')),
            'subsidio': subsidio.quantize(Decimal('0.01')),
            'isr_neto': isr_neto.quantize(Decimal('0.01'))
        }
    
    def _calcular_subsidio(self, ingreso: Decimal) -> Decimal:
        """Calcula subsidio al empleo según tabla"""
        if not self.tablas_subsidio.exists():
            return Decimal('0')
        
        for rango in self.tablas_subsidio:
            if rango.limite_inferior <= ingreso <= rango.limite_superior:
                return rango.subsidio
        
        return Decimal('0')
    
    # ============ CÁLCULO DE IMSS (CUOTA OBRERA) ============
    
    def calcular_imss_obrero(self, sbc: Decimal, dias: int = 15) -> Dict:
        """
        Calcula cuotas IMSS que paga el trabajador
        SBC = Salario Base de Cotización
        """
        if not self.params_imss:
            return {
                'error': 'No hay parámetros IMSS configurados',
                'total': Decimal('0')
            }
        
        sbc = Decimal(str(sbc))
        
        # Aplicar tope de SBC
        tope = self.params_imss.tope_sbc
        sbc_topado = min(sbc, tope)
        
        # Base para cálculo
        base = sbc_topado * dias
        
        # Cuotas obreras
        enf_mat = base * self.params_imss.porc_enf_mat_obrera
        invalidez_vida = base * self.params_imss.porc_invalidez_vida_obrera
        cesantia_vejez = base * self.params_imss.porc_cesantia_vejez_obrera
        
        total = enf_mat + invalidez_vida + cesantia_vejez
        
        return {
            'sbc_original': sbc,
            'sbc_topado': sbc_topado,
            'dias': dias,
            'base': base.quantize(Decimal('0.01')),
            'enfermedad_maternidad': enf_mat.quantize(Decimal('0.01')),
            'invalidez_vida': invalidez_vida.quantize(Decimal('0.01')),
            'cesantia_vejez': cesantia_vejez.quantize(Decimal('0.01')),
            'total': total.quantize(Decimal('0.01'))
        }
    
    def calcular_imss_patronal(self, sbc: Decimal, dias: int = 15) -> Dict:
        """
        Calcula cuotas IMSS que paga el patrón
        Útil para costeo y presupuestos
        """
        if not self.params_imss:
            return {'error': 'No hay parámetros IMSS configurados', 'total': Decimal('0')}
        
        sbc = Decimal(str(sbc))
        tope = self.params_imss.tope_sbc
        sbc_topado = min(sbc, tope)
        base = sbc_topado * dias
        
        # Calcular diferencia con 3 SMG para enfermedad y maternidad
        tres_smg = self.params_imss.salario_minimo_general * 3
        excedente_enf_mat = max(sbc_topado - tres_smg, Decimal('0')) * dias
        
        # Cuota fija enfermedad y maternidad (sobre SMG)
        cuota_fija_enf_mat = (self.params_imss.salario_minimo_general * dias * 
                              self.params_imss.cuota_fija_enf_mat)
        
        # Cuotas patronales
        riesgo_trabajo = base * self.params_imss.porc_riesgo_trabajo
        enf_mat_excedente = excedente_enf_mat * self.params_imss.porc_enf_mat_patronal
        invalidez_vida = base * self.params_imss.porc_invalidez_vida_patronal
        cesantia_vejez = base * self.params_imss.porc_cesantia_vejez_patronal
        guarderias = base * self.params_imss.porc_guarderias
        infonavit = base * self.params_imss.porc_infonavit
        
        total = (cuota_fija_enf_mat + riesgo_trabajo + enf_mat_excedente + 
                 invalidez_vida + cesantia_vejez + guarderias + infonavit)
        
        return {
            'cuota_fija_enf_mat': cuota_fija_enf_mat.quantize(Decimal('0.01')),
            'riesgo_trabajo': riesgo_trabajo.quantize(Decimal('0.01')),
            'enf_mat_excedente': enf_mat_excedente.quantize(Decimal('0.01')),
            'invalidez_vida': invalidez_vida.quantize(Decimal('0.01')),
            'cesantia_vejez': cesantia_vejez.quantize(Decimal('0.01')),
            'guarderias': guarderias.quantize(Decimal('0.01')),
            'infonavit': infonavit.quantize(Decimal('0.01')),
            'total': total.quantize(Decimal('0.01'))
        }
    
    # ============ SALARIO BASE DE COTIZACIÓN ============
    
    def calcular_sbc(self, salario_diario: Decimal, factor_integracion: Decimal = None) -> Decimal:
        """
        Calcula el Salario Base de Cotización
        Factor de integración por defecto: 1.0493 (mínimo de ley)
        """
        salario = Decimal(str(salario_diario))
        
        # Factor de integración mínimo según ley
        # 365 + 15 aguinaldo + (6 vacaciones * 25% prima) = 365 + 15 + 1.5 = 381.5
        # 381.5 / 365 = 1.0452 (primer año)
        # Con prestaciones superiores el factor aumenta
        
        if factor_integracion is None:
            # Factor mínimo para primer año
            factor_integracion = Decimal('1.0493')
        
        sbc = salario * factor_integracion
        
        # Aplicar tope
        if self.params_imss:
            tope = self.params_imss.tope_sbc
            sbc = min(sbc, tope)
        
        return sbc.quantize(Decimal('0.01'))
    
    def calcular_factor_integracion(
        self, 
        dias_aguinaldo: int = 15,
        dias_vacaciones: int = 12,
        prima_vacacional_pct: Decimal = Decimal('25'),
        dias_fondo_ahorro: int = 0,
        vales_despensa_pct: Decimal = Decimal('0')
    ) -> Decimal:
        """
        Calcula el factor de integración personalizado
        según las prestaciones de la empresa
        """
        # Fórmula: (365 + aguinaldo + (vacaciones * prima/100) + otras) / 365
        
        prima_sobre_vacaciones = dias_vacaciones * (prima_vacacional_pct / 100)
        
        # Vales de despensa (solo integra lo que excede 40% SMG)
        # Simplificado aquí, en producción calcular exactamente
        
        total_dias = (Decimal('365') + 
                      Decimal(str(dias_aguinaldo)) + 
                      prima_sobre_vacaciones +
                      Decimal(str(dias_fondo_ahorro)))
        
        factor = total_dias / Decimal('365')
        
        return factor.quantize(Decimal('0.0001'))


class CalculadoraPrestaciones:
    """
    Calcula prestaciones de ley y superiores
    """
    
    # Tabla de vacaciones LFT 2023 (reforma)
    VACACIONES_LFT = {
        1: 12, 2: 14, 3: 16, 4: 18, 5: 20,
        6: 22, 7: 22, 8: 22, 9: 22, 10: 22,
        11: 24, 12: 24, 13: 24, 14: 24, 15: 24,
        16: 26, 17: 26, 18: 26, 19: 26, 20: 26,
        21: 28, 22: 28, 23: 28, 24: 28, 25: 28,
        # 26-30: 30, 31-35: 32, etc.
    }
    
    @classmethod
    def dias_vacaciones_por_antiguedad(cls, años: int) -> int:
        """Retorna días de vacaciones según años de antigüedad"""
        if años <= 0:
            return 0
        if años <= 25:
            return cls.VACACIONES_LFT.get(años, 12)
        # Después de 25 años: +2 días cada 5 años
        base = 28
        quinquenios_extra = (años - 25) // 5
        return base + (quinquenios_extra * 2)
    
    @classmethod
    def calcular_aguinaldo(
        cls,
        salario_diario: Decimal,
        dias_aguinaldo: int = 15,
        fecha_ingreso: date = None,
        fecha_corte: date = None
    ) -> Dict:
        """
        Calcula aguinaldo (mínimo 15 días según LFT)
        Proporcional si no cumplió el año
        """
        salario = Decimal(str(salario_diario))
        fecha_corte = fecha_corte or date(date.today().year, 12, 31)
        
        # Calcular días trabajados en el año
        inicio_año = date(fecha_corte.year, 1, 1)
        
        if fecha_ingreso and fecha_ingreso > inicio_año:
            dias_trabajados = (fecha_corte - fecha_ingreso).days + 1
        else:
            dias_trabajados = (fecha_corte - inicio_año).days + 1
        
        # Aguinaldo proporcional
        if dias_trabajados >= 365:
            dias_aguinaldo_proporcional = Decimal(str(dias_aguinaldo))
            es_proporcional = False
        else:
            dias_aguinaldo_proporcional = (Decimal(str(dias_aguinaldo)) * 
                                           Decimal(str(dias_trabajados)) / Decimal('365'))
            es_proporcional = True
        
        monto = salario * dias_aguinaldo_proporcional
        
        # Exención de ISR: 30 UMAs (aprox $3,300 en 2024)
        # Simplificado, en producción usar UMA vigente
        
        return {
            'salario_diario': salario,
            'dias_aguinaldo_plan': dias_aguinaldo,
            'dias_trabajados': dias_trabajados,
            'es_proporcional': es_proporcional,
            'dias_aguinaldo_proporcional': dias_aguinaldo_proporcional.quantize(Decimal('0.01')),
            'monto_bruto': monto.quantize(Decimal('0.01'))
        }
    
    @classmethod
    def calcular_prima_vacacional(
        cls,
        salario_diario: Decimal,
        dias_vacaciones: int,
        porcentaje_prima: Decimal = Decimal('25')
    ) -> Dict:
        """
        Calcula prima vacacional (mínimo 25% según LFT)
        """
        salario = Decimal(str(salario_diario))
        dias = Decimal(str(dias_vacaciones))
        pct = Decimal(str(porcentaje_prima)) / 100
        
        base = salario * dias
        prima = base * pct
        
        return {
            'salario_diario': salario,
            'dias_vacaciones': dias_vacaciones,
            'porcentaje': porcentaje_prima,
            'base': base.quantize(Decimal('0.01')),
            'prima_vacacional': prima.quantize(Decimal('0.01'))
        }
    
    @classmethod
    def calcular_finiquito(
        cls,
        salario_diario: Decimal,
        fecha_ingreso: date,
        fecha_baja: date,
        dias_aguinaldo: int = 15,
        prima_vacacional_pct: Decimal = Decimal('25'),
        es_despido_injustificado: bool = False
    ) -> Dict:
        """
        Calcula finiquito completo
        """
        salario = Decimal(str(salario_diario))
        
        # Antigüedad en años
        dias_antiguedad = (fecha_baja - fecha_ingreso).days
        años = dias_antiguedad // 365
        
        # Días de vacaciones según antigüedad
        dias_vacaciones = cls.dias_vacaciones_por_antiguedad(años + 1)
        
        # Partes proporcionales
        aguinaldo = cls.calcular_aguinaldo(
            salario, dias_aguinaldo, fecha_ingreso, fecha_baja
        )
        
        # Vacaciones proporcionales del periodo actual
        # Simplificado: proporción del año actual
        dias_año_actual = (fecha_baja - date(fecha_baja.year, fecha_ingreso.month, fecha_ingreso.day)).days
        if dias_año_actual < 0:
            dias_año_actual = 365 + dias_año_actual
        
        vacaciones_proporcionales = Decimal(str(dias_vacaciones)) * Decimal(str(dias_año_actual)) / Decimal('365')
        pago_vacaciones = salario * vacaciones_proporcionales
        
        prima_vacacional = cls.calcular_prima_vacacional(
            salario, int(vacaciones_proporcionales), prima_vacacional_pct
        )
        
        # Totales
        subtotal = (aguinaldo['monto_bruto'] + 
                   pago_vacaciones + 
                   prima_vacacional['prima_vacacional'])
        
        # Si es despido injustificado, agregar indemnización
        indemnizacion_90_dias = Decimal('0')
        indemnizacion_20_dias_año = Decimal('0')
        prima_antiguedad = Decimal('0')
        
        if es_despido_injustificado:
            # 90 días de salario (Art. 48 LFT)
            indemnizacion_90_dias = salario * 90
            
            # 20 días por año (Art. 50 LFT)
            salario_integrado = salario * Decimal('1.0493')  # Mínimo
            indemnizacion_20_dias_año = salario_integrado * 20 * años
            
            # Prima de antigüedad: 12 días por año, tope doble SMG
            # Simplificado
            prima_antiguedad = salario * 12 * años
        
        total = subtotal + indemnizacion_90_dias + indemnizacion_20_dias_año + prima_antiguedad
        
        return {
            'fecha_ingreso': fecha_ingreso,
            'fecha_baja': fecha_baja,
            'dias_antiguedad': dias_antiguedad,
            'años_antiguedad': años,
            'salario_diario': salario,
            'aguinaldo_proporcional': aguinaldo['monto_bruto'],
            'vacaciones_proporcionales_dias': vacaciones_proporcionales.quantize(Decimal('0.01')),
            'vacaciones_proporcionales_pago': pago_vacaciones.quantize(Decimal('0.01')),
            'prima_vacacional': prima_vacacional['prima_vacacional'],
            'subtotal_finiquito': subtotal.quantize(Decimal('0.01')),
            'es_despido_injustificado': es_despido_injustificado,
            'indemnizacion_90_dias': indemnizacion_90_dias.quantize(Decimal('0.01')),
            'indemnizacion_20_dias_año': indemnizacion_20_dias_año.quantize(Decimal('0.01')),
            'prima_antiguedad': prima_antiguedad.quantize(Decimal('0.01')),
            'total': total.quantize(Decimal('0.01'))
        }


def procesar_nomina_periodo(periodo_id: int, usuario_id: int) -> Dict:
    """
    Procesa la nómina completa de un periodo
    Crea recibos para todos los empleados activos
    """
    from .models import PeriodoNomina, ReciboNomina, DetalleReciboNomina, ConceptoNomina
    from apps.empleados.models import Empleado
    from django.utils import timezone
    
    periodo = PeriodoNomina.objects.get(pk=periodo_id)
    
    # Validar estado
    if periodo.estado not in ['borrador', 'calculado']:
        return {'error': 'El periodo no puede ser procesado en este estado'}
    
    # Obtener empleados activos de la empresa
    empleados = Empleado.objects.filter(
        empresa=periodo.empresa,
        estado='activo'
    )
    
    # Obtener conceptos fijos
    concepto_sueldo = ConceptoNomina.objects.filter(codigo_interno='P001').first()
    concepto_isr = ConceptoNomina.objects.filter(codigo_interno='D001').first()
    concepto_imss = ConceptoNomina.objects.filter(codigo_interno='D002').first()
    
    # Días del periodo
    if periodo.tipo_periodo == 'quincenal':
        dias_periodo = 15
    elif periodo.tipo_periodo == 'semanal':
        dias_periodo = 7
    else:
        dias_periodo = 30
    
    calculadora = CalculadoraNomina(periodo.año, periodo.tipo_periodo)
    
    resultados = []
    total_percepciones = Decimal('0')
    total_deducciones = Decimal('0')
    total_neto = Decimal('0')
    
    for empleado in empleados:
        # Crear o actualizar recibo
        recibo, created = ReciboNomina.objects.update_or_create(
            periodo=periodo,
            empleado=empleado,
            defaults={
                'salario_diario': empleado.salario_diario or Decimal('0'),
                'dias_trabajados': dias_periodo,
                'dias_pagados': dias_periodo,
                'estado': 'calculado'
            }
        )
        
        if not empleado.salario_diario:
            resultados.append({
                'empleado': str(empleado),
                'error': 'Sin salario configurado'
            })
            continue
        
        # Calcular SBC
        sbc = calculadora.calcular_sbc(empleado.salario_diario)
        recibo.salario_base_cotizacion = sbc
        
        # Calcular sueldo del periodo
        sueldo_periodo = empleado.salario_diario * dias_periodo
        
        # Calcular ISR
        resultado_isr = calculadora.calcular_isr(sueldo_periodo)
        isr = resultado_isr.get('isr_neto', Decimal('0'))
        subsidio = resultado_isr.get('subsidio', Decimal('0'))
        
        # Calcular IMSS
        resultado_imss = calculadora.calcular_imss_obrero(sbc, dias_periodo)
        imss = resultado_imss.get('total', Decimal('0'))
        
        # Actualizar recibo
        recibo.total_percepciones = sueldo_periodo
        recibo.total_percepciones_gravadas = sueldo_periodo
        recibo.total_deducciones = isr + imss
        recibo.base_gravable_isr = sueldo_periodo
        recibo.isr_antes_subsidio = resultado_isr.get('isr_antes_subsidio', Decimal('0'))
        recibo.subsidio_aplicado = subsidio
        recibo.isr_retenido = isr
        recibo.cuota_imss_obrera = imss
        recibo.neto_a_pagar = sueldo_periodo - isr - imss
        recibo.save()
        
        # Crear detalles
        if concepto_sueldo:
            DetalleReciboNomina.objects.update_or_create(
                recibo=recibo,
                concepto=concepto_sueldo,
                defaults={
                    'cantidad': dias_periodo,
                    'valor_unitario': empleado.salario_diario,
                    'importe_gravado': sueldo_periodo,
                    'importe_total': sueldo_periodo
                }
            )
        
        if concepto_isr and isr > 0:
            DetalleReciboNomina.objects.update_or_create(
                recibo=recibo,
                concepto=concepto_isr,
                defaults={
                    'importe_total': isr
                }
            )
        
        if concepto_imss and imss > 0:
            DetalleReciboNomina.objects.update_or_create(
                recibo=recibo,
                concepto=concepto_imss,
                defaults={
                    'importe_total': imss
                }
            )
        
        # Acumular totales
        total_percepciones += sueldo_periodo
        total_deducciones += (isr + imss)
        total_neto += recibo.neto_a_pagar
        
        resultados.append({
            'empleado': str(empleado),
            'sueldo': float(sueldo_periodo),
            'isr': float(isr),
            'imss': float(imss),
            'neto': float(recibo.neto_a_pagar)
        })
    
    # Actualizar periodo
    periodo.total_percepciones = total_percepciones
    periodo.total_deducciones = total_deducciones
    periodo.total_neto = total_neto
    periodo.total_empleados = len(resultados)
    periodo.estado = 'calculado'
    periodo.fecha_calculo = timezone.now()
    periodo.calculado_por_id = usuario_id
    periodo.save()
    
    return {
        'periodo': str(periodo),
        'total_empleados': len(resultados),
        'total_percepciones': float(total_percepciones),
        'total_deducciones': float(total_deducciones),
        'total_neto': float(total_neto),
        'recibos': resultados
    }
