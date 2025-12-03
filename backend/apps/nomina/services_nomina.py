"""
Servicios para procesamiento completo de nómina
"""
from datetime import date, datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List, Optional, Tuple
from django.db import transaction
from django.db.models import Sum, Count, Q
from django.utils import timezone


class GeneradorPeriodos:
    """Genera periodos de nómina automáticamente"""
    
    @staticmethod
    def generar_periodos_año(empresa, tipo: str, año: int) -> List[Dict]:
        """Genera todos los periodos de un año"""
        from .models import PeriodoNomina
        
        periodos_creados = []
        
        if tipo == 'semanal':
            # 52 periodos semanales
            fecha_inicio = date(año, 1, 1)
            # Ajustar al lunes más cercano
            while fecha_inicio.weekday() != 0:
                fecha_inicio += timedelta(days=1)
            
            for num in range(1, 53):
                fecha_fin = fecha_inicio + timedelta(days=6)
                fecha_pago = fecha_fin + timedelta(days=3)  # Miércoles siguiente
                
                periodo, created = PeriodoNomina.objects.get_or_create(
                    empresa=empresa,
                    tipo=tipo,
                    año=año,
                    numero_periodo=num,
                    defaults={
                        'fecha_inicio': fecha_inicio,
                        'fecha_fin': fecha_fin,
                        'fecha_pago': fecha_pago,
                        'dias_periodo': 7,
                    }
                )
                if created:
                    periodos_creados.append(periodo)
                fecha_inicio = fecha_fin + timedelta(days=1)
                
        elif tipo == 'quincenal':
            # 24 periodos quincenales
            for num in range(1, 25):
                mes = (num + 1) // 2
                if num % 2 == 1:  # Primera quincena
                    fecha_inicio = date(año, mes, 1)
                    fecha_fin = date(año, mes, 15)
                    fecha_pago = date(año, mes, 15)
                else:  # Segunda quincena
                    fecha_inicio = date(año, mes, 16)
                    # Último día del mes
                    if mes == 12:
                        fecha_fin = date(año, 12, 31)
                    else:
                        fecha_fin = date(año, mes + 1, 1) - timedelta(days=1)
                    fecha_pago = fecha_fin
                
                periodo, created = PeriodoNomina.objects.get_or_create(
                    empresa=empresa,
                    tipo=tipo,
                    año=año,
                    numero_periodo=num,
                    defaults={
                        'fecha_inicio': fecha_inicio,
                        'fecha_fin': fecha_fin,
                        'fecha_pago': fecha_pago,
                        'dias_periodo': 15,
                    }
                )
                if created:
                    periodos_creados.append(periodo)
                    
        elif tipo == 'mensual':
            # 12 periodos mensuales
            for mes in range(1, 13):
                fecha_inicio = date(año, mes, 1)
                if mes == 12:
                    fecha_fin = date(año, 12, 31)
                else:
                    fecha_fin = date(año, mes + 1, 1) - timedelta(days=1)
                fecha_pago = fecha_fin
                
                periodo, created = PeriodoNomina.objects.get_or_create(
                    empresa=empresa,
                    tipo=tipo,
                    año=año,
                    numero_periodo=mes,
                    defaults={
                        'fecha_inicio': fecha_inicio,
                        'fecha_fin': fecha_fin,
                        'fecha_pago': fecha_pago,
                        'dias_periodo': 30,
                    }
                )
                if created:
                    periodos_creados.append(periodo)
        
        return periodos_creados


class CalculadoraNomina:
    """Calcula la nómina de un empleado para un periodo"""
    
    # Salario mínimo 2024
    SALARIO_MINIMO = Decimal('248.93')
    UMA = Decimal('108.57')
    
    def __init__(self, empleado, periodo):
        self.empleado = empleado
        self.periodo = periodo
        self.salario_diario = empleado.salario_diario or Decimal('0')
        self.percepciones = []
        self.deducciones = []
    
    def calcular(self) -> Dict:
        """Ejecuta el cálculo completo de nómina"""
        # 1. Calcular días trabajados
        dias_info = self._calcular_dias()
        
        # 2. Calcular percepciones fijas
        self._calcular_sueldo_base(dias_info)
        
        # 3. Calcular horas extra
        self._calcular_horas_extra(dias_info)
        
        # 4. Agregar percepciones variables
        self._agregar_percepciones_variables()
        
        # 5. Calcular totales de percepciones
        total_gravado, total_exento = self._sumar_percepciones()
        
        # 6. Calcular ISR
        isr = self._calcular_isr(total_gravado)
        self.deducciones.append({
            'concepto': 'ISR',
            'clave': 'D001',
            'monto': isr,
            'tipo': 'isr'
        })
        
        # 7. Calcular IMSS empleado
        imss_emp = self._calcular_imss_empleado()
        self.deducciones.append({
            'concepto': 'IMSS Empleado',
            'clave': 'D002',
            'monto': imss_emp,
            'tipo': 'imss'
        })
        
        # 8. Agregar deducciones fijas/variables
        self._agregar_deducciones_fijas()
        
        # 9. Calcular totales
        total_percepciones = sum(p['monto'] for p in self.percepciones)
        total_deducciones = sum(d['monto'] for d in self.deducciones)
        neto = total_percepciones - total_deducciones
        
        # 10. Calcular costos patronales
        costos_patron = self._calcular_costos_patron()
        
        return {
            'empleado_id': str(self.empleado.id),
            'empleado_nombre': self.empleado.nombre_completo,
            'periodo_id': str(self.periodo.id),
            
            'salario_diario': float(self.salario_diario),
            'salario_diario_integrado': float(self._calcular_sdi()),
            
            'dias': dias_info,
            
            'percepciones': self.percepciones,
            'deducciones': self.deducciones,
            
            'total_percepciones': float(total_percepciones),
            'total_gravado': float(total_gravado),
            'total_exento': float(total_exento),
            'total_deducciones': float(total_deducciones),
            'neto_a_pagar': float(neto),
            
            'costos_patron': costos_patron,
            'costo_total_empresa': float(total_percepciones + sum(
                Decimal(str(v)) for v in costos_patron.values()
            )),
        }
    
    def _calcular_dias(self) -> Dict:
        """Calcula días trabajados, faltas, incapacidades, etc."""
        from .models import Incidencia
        
        dias_periodo = self.periodo.dias_periodo
        
        incidencias = Incidencia.objects.filter(
            empleado=self.empleado,
            fecha__gte=self.periodo.fecha_inicio,
            fecha__lte=self.periodo.fecha_fin,
            estado='aprobada'
        )
        
        dias_faltas = Decimal('0')
        dias_incapacidad = Decimal('0')
        dias_vacaciones = Decimal('0')
        horas_extra_dobles = Decimal('0')
        horas_extra_triples = Decimal('0')
        dias_festivos_laborados = Decimal('0')
        
        for inc in incidencias:
            cantidad = inc.cantidad or Decimal('1')
            
            if inc.tipo in ['falta_justificada', 'falta_injustificada']:
                dias_faltas += cantidad
            elif inc.tipo.startswith('incapacidad'):
                dias_incapacidad += cantidad
            elif inc.tipo == 'vacaciones':
                dias_vacaciones += cantidad
            elif inc.tipo == 'hora_extra_doble':
                horas_extra_dobles += cantidad
            elif inc.tipo == 'hora_extra_triple':
                horas_extra_triples += cantidad
            elif inc.tipo in ['festivo_laborado', 'descanso_laborado']:
                dias_festivos_laborados += cantidad
        
        dias_trabajados = Decimal(str(dias_periodo)) - dias_faltas - dias_incapacidad
        dias_pagados = dias_trabajados + dias_vacaciones
        
        return {
            'dias_periodo': dias_periodo,
            'dias_trabajados': float(dias_trabajados),
            'dias_pagados': float(dias_pagados),
            'dias_faltas': float(dias_faltas),
            'dias_incapacidad': float(dias_incapacidad),
            'dias_vacaciones': float(dias_vacaciones),
            'horas_extra_dobles': float(horas_extra_dobles),
            'horas_extra_triples': float(horas_extra_triples),
            'dias_festivos_laborados': float(dias_festivos_laborados),
        }
    
    def _calcular_sueldo_base(self, dias_info: Dict):
        """Calcula el sueldo base según días trabajados"""
        dias_pagados = Decimal(str(dias_info['dias_pagados']))
        sueldo = self.salario_diario * dias_pagados
        
        self.percepciones.append({
            'concepto': 'Sueldo',
            'clave': 'P001',
            'monto': float(sueldo),
            'gravado': float(sueldo),
            'exento': 0,
            'tipo': 'fijo'
        })
    
    def _calcular_horas_extra(self, dias_info: Dict):
        """Calcula pago de horas extra"""
        horas_dobles = Decimal(str(dias_info['horas_extra_dobles']))
        horas_triples = Decimal(str(dias_info['horas_extra_triples']))
        
        if horas_dobles > 0:
            valor_hora = self.salario_diario / Decimal('8')
            # Primeras 9 horas semanales: 50% exento
            pago = valor_hora * Decimal('2') * horas_dobles
            exento = min(pago * Decimal('0.5'), self.UMA * Decimal('5') * Decimal('7'))
            
            self.percepciones.append({
                'concepto': 'Horas Extra Dobles',
                'clave': 'P002',
                'monto': float(pago),
                'gravado': float(pago - exento),
                'exento': float(exento),
                'tipo': 'variable'
            })
        
        if horas_triples > 0:
            valor_hora = self.salario_diario / Decimal('8')
            pago = valor_hora * Decimal('3') * horas_triples
            
            self.percepciones.append({
                'concepto': 'Horas Extra Triples',
                'clave': 'P003',
                'monto': float(pago),
                'gravado': float(pago),  # 100% gravado
                'exento': 0,
                'tipo': 'variable'
            })
    
    def _agregar_percepciones_variables(self):
        """Agrega percepciones variables del periodo"""
        from .models import PercepcionVariable
        
        percepciones = PercepcionVariable.objects.filter(
            empleado=self.empleado,
            periodo=self.periodo
        )
        
        for p in percepciones:
            monto = float(p.monto)
            gravado = monto if p.es_gravable else 0
            exento = 0 if p.es_gravable else monto
            
            self.percepciones.append({
                'concepto': p.get_tipo_display(),
                'clave': f'P0{len(self.percepciones) + 1}',
                'monto': monto,
                'gravado': gravado,
                'exento': exento,
                'tipo': 'variable'
            })
    
    def _sumar_percepciones(self) -> Tuple[Decimal, Decimal]:
        """Suma percepciones gravadas y exentas"""
        total_gravado = sum(Decimal(str(p['gravado'])) for p in self.percepciones)
        total_exento = sum(Decimal(str(p['exento'])) for p in self.percepciones)
        return total_gravado, total_exento
    
    def _calcular_isr(self, base_gravable: Decimal) -> Decimal:
        """Calcula ISR según tablas"""
        from .models import TablaISR
        
        # Determinar periodicidad
        if self.periodo.tipo == 'semanal':
            periodicidad = 'semanal'
        elif self.periodo.tipo == 'quincenal':
            periodicidad = 'quincenal'
        else:
            periodicidad = 'mensual'
        
        try:
            rango = TablaISR.objects.filter(
                periodicidad=periodicidad,
                limite_inferior__lte=base_gravable,
                limite_superior__gte=base_gravable
            ).first()
            
            if rango:
                excedente = base_gravable - rango.limite_inferior
                isr_marginal = excedente * (rango.porcentaje / Decimal('100'))
                isr_total = rango.cuota_fija + isr_marginal
                
                # Aplicar subsidio si aplica (simplificado)
                # En producción, usar tabla de subsidio
                return isr_total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            
        except Exception:
            pass
        
        # Fallback: 10% aproximado
        return (base_gravable * Decimal('0.10')).quantize(Decimal('0.01'))
    
    def _calcular_imss_empleado(self) -> Decimal:
        """Calcula cuotas IMSS del empleado"""
        sdi = self._calcular_sdi()
        dias = Decimal(str(self.periodo.dias_periodo))
        
        # Cuotas simplificadas (en producción usar ParametrosIMSS)
        # Enfermedad y maternidad: 0.375%
        # Invalidez y vida: 0.625%
        # Cesantía y vejez: 1.125%
        
        tasa_total = Decimal('2.125') / Decimal('100')
        cuota = sdi * dias * tasa_total
        
        return cuota.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    def _calcular_sdi(self) -> Decimal:
        """Calcula Salario Diario Integrado"""
        # Factor de integración simplificado
        # Aguinaldo: 15 días / 365 = 0.0411
        # Vacaciones: 12 días * 25% / 365 = 0.0082
        # Total factor: 1.0493
        factor = Decimal('1.0493')
        return self.salario_diario * factor
    
    def _agregar_deducciones_fijas(self):
        """Agrega deducciones fijas del empleado"""
        from .models import DeduccionVariable
        
        deducciones = DeduccionVariable.objects.filter(
            empleado=self.empleado,
            activa=True,
            fecha_inicio__lte=self.periodo.fecha_fin
        ).filter(
            Q(fecha_fin__isnull=True) | Q(fecha_fin__gte=self.periodo.fecha_inicio)
        )
        
        for d in deducciones:
            monto = float(d.calcular_monto(self.salario_diario * self.periodo.dias_periodo))
            
            self.deducciones.append({
                'concepto': d.get_tipo_display(),
                'clave': f'D0{len(self.deducciones) + 1}',
                'monto': monto,
                'tipo': d.tipo
            })
    
    def _calcular_costos_patron(self) -> Dict:
        """Calcula costos patronales"""
        sdi = self._calcular_sdi()
        dias = Decimal(str(self.periodo.dias_periodo))
        base = sdi * dias
        
        # Tasas patronales simplificadas
        imss_patron = base * Decimal('0.13185')  # Aprox 13.185%
        rcv_patron = base * Decimal('0.0315')    # 3.15%
        infonavit = base * Decimal('0.05')       # 5%
        impuesto_nomina = base * Decimal('0.03') # 3% (varía por estado)
        
        return {
            'imss_patron': float(imss_patron.quantize(Decimal('0.01'))),
            'rcv_patron': float(rcv_patron.quantize(Decimal('0.01'))),
            'infonavit': float(infonavit.quantize(Decimal('0.01'))),
            'impuesto_nomina': float(impuesto_nomina.quantize(Decimal('0.01'))),
        }


class ProcesadorNomina:
    """Procesa nómina completa de un periodo"""
    
    def __init__(self, periodo):
        self.periodo = periodo
    
    @transaction.atomic
    def generar_pre_nomina(self) -> Dict:
        """Genera pre-nómina para todos los empleados activos"""
        from apps.empleados.models import Empleado
        from .models import PreNomina
        
        empleados = Empleado.objects.filter(
            empresa=self.periodo.empresa,
            estado='activo'
        )
        
        resultados = []
        errores = []
        
        for empleado in empleados:
            try:
                calculadora = CalculadoraNomina(empleado, self.periodo)
                calculo = calculadora.calcular()
                
                # Crear o actualizar pre-nómina
                pre_nomina, created = PreNomina.objects.update_or_create(
                    periodo=self.periodo,
                    empleado=empleado,
                    defaults={
                        'salario_diario': calculo['salario_diario'],
                        'salario_diario_integrado': calculo['salario_diario_integrado'],
                        'dias_trabajados': calculo['dias']['dias_trabajados'],
                        'dias_pagados': calculo['dias']['dias_pagados'],
                        'dias_incapacidad': calculo['dias']['dias_incapacidad'],
                        'dias_faltas': calculo['dias']['dias_faltas'],
                        'dias_vacaciones': calculo['dias']['dias_vacaciones'],
                        'horas_extra_dobles': calculo['dias']['horas_extra_dobles'],
                        'horas_extra_triples': calculo['dias']['horas_extra_triples'],
                        'total_percepciones': calculo['total_percepciones'],
                        'total_percepciones_gravadas': calculo['total_gravado'],
                        'total_percepciones_exentas': calculo['total_exento'],
                        'total_deducciones': calculo['total_deducciones'],
                        'isr_retenido': next((d['monto'] for d in calculo['deducciones'] if d['tipo'] == 'isr'), 0),
                        'imss_empleado': next((d['monto'] for d in calculo['deducciones'] if d['tipo'] == 'imss'), 0),
                        'neto_a_pagar': calculo['neto_a_pagar'],
                        'imss_patron': calculo['costos_patron']['imss_patron'],
                        'rcv_patron': calculo['costos_patron']['rcv_patron'],
                        'infonavit_patron': calculo['costos_patron']['infonavit'],
                        'impuesto_nomina': calculo['costos_patron']['impuesto_nomina'],
                        'costo_total_empresa': calculo['costo_total_empresa'],
                        'detalle_percepciones': calculo['percepciones'],
                        'detalle_deducciones': calculo['deducciones'],
                    }
                )
                
                resultados.append({
                    'empleado': empleado.nombre_completo,
                    'neto': calculo['neto_a_pagar'],
                    'status': 'creado' if created else 'actualizado'
                })
                
            except Exception as e:
                errores.append({
                    'empleado': empleado.nombre_completo,
                    'error': str(e)
                })
        
        # Actualizar totales del periodo
        self._actualizar_totales_periodo()
        
        # Cambiar estado
        self.periodo.estado = 'calculado'
        self.periodo.save()
        
        return {
            'success': True,
            'periodo': self.periodo.nombre_periodo,
            'empleados_procesados': len(resultados),
            'errores': len(errores),
            'resultados': resultados,
            'detalle_errores': errores,
        }
    
    def _actualizar_totales_periodo(self):
        """Actualiza totales del periodo desde pre-nóminas"""
        from .models import PreNomina
        from django.db.models import Sum, Count
        
        totales = PreNomina.objects.filter(periodo=self.periodo).aggregate(
            total_percepciones=Sum('total_percepciones'),
            total_deducciones=Sum('total_deducciones'),
            total_neto=Sum('neto_a_pagar'),
            total_empleados=Count('id')
        )
        
        self.periodo.total_percepciones = totales['total_percepciones'] or 0
        self.periodo.total_deducciones = totales['total_deducciones'] or 0
        self.periodo.total_neto = totales['total_neto'] or 0
        self.periodo.total_empleados = totales['total_empleados'] or 0
        self.periodo.save()
    
    @transaction.atomic
    def autorizar_nomina(self, autorizado_por) -> Dict:
        """Autoriza la nómina para pago"""
        if self.periodo.estado not in ['calculado', 'en_proceso']:
            return {'success': False, 'error': f'El periodo está en estado {self.periodo.estado}'}
        
        self.periodo.estado = 'autorizado'
        self.periodo.autorizado_por = autorizado_por
        self.periodo.fecha_autorizacion = timezone.now()
        self.periodo.save()
        
        return {
            'success': True,
            'mensaje': f'Nómina {self.periodo.nombre_periodo} autorizada',
            'total_neto': float(self.periodo.total_neto),
            'empleados': self.periodo.total_empleados,
        }
    
    @transaction.atomic
    def generar_dispersion(self) -> Dict:
        """Genera archivo de dispersión bancaria"""
        from .models import PreNomina, MovimientoBancario
        
        if self.periodo.estado != 'autorizado':
            return {'success': False, 'error': 'La nómina debe estar autorizada'}
        
        pre_nominas = PreNomina.objects.filter(
            periodo=self.periodo,
            neto_a_pagar__gt=0
        ).select_related('empleado')
        
        movimientos = []
        lineas_archivo = []
        
        for pn in pre_nominas:
            emp = pn.empleado
            
            # Crear movimiento bancario
            mov = MovimientoBancario.objects.create(
                periodo=self.periodo,
                empleado=emp,
                banco=emp.banco or 'SIN BANCO',
                clabe=emp.clabe or '000000000000000000',
                monto=pn.neto_a_pagar,
                referencia=f'NOM{self.periodo.año}{self.periodo.numero_periodo:02d}',
                concepto=f'NOMINA {self.periodo.nombre_periodo}',
            )
            movimientos.append(mov)
            
            # Línea para archivo (formato genérico)
            lineas_archivo.append(
                f"{emp.clabe},{pn.neto_a_pagar:.2f},{emp.nombre_completo},NOMINA"
            )
        
        # Guardar archivo
        contenido = "CLABE,MONTO,BENEFICIARIO,CONCEPTO\n" + "\n".join(lineas_archivo)
        
        from django.core.files.base import ContentFile
        nombre_archivo = f"dispersion_{self.periodo.empresa.rfc}_{self.periodo.año}_{self.periodo.numero_periodo:02d}.csv"
        self.periodo.archivo_dispersion.save(nombre_archivo, ContentFile(contenido.encode('utf-8')))
        self.periodo.fecha_dispersion = timezone.now()
        self.periodo.estado = 'pagado'
        self.periodo.save()
        
        return {
            'success': True,
            'mensaje': f'Dispersión generada con {len(movimientos)} movimientos',
            'archivo': self.periodo.archivo_dispersion.url if self.periodo.archivo_dispersion else None,
            'total': float(sum(m.monto for m in movimientos)),
            'movimientos': len(movimientos),
        }
