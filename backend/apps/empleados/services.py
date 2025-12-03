"""
Servicio para cálculo de vacaciones según LFT México y plan de prestaciones.
"""
from datetime import date
from dateutil.relativedelta import relativedelta
from typing import Dict, List, Optional
from decimal import Decimal


# Tabla de vacaciones LFT (reforma 2023)
VACACIONES_LFT = {
    1: 12, 2: 14, 3: 16, 4: 18, 5: 20,
    6: 22, 11: 24, 16: 26, 21: 28, 26: 30, 31: 32
}


def obtener_dias_vacaciones_ley(ano_antiguedad: int) -> int:
    """Obtiene días de vacaciones según LFT para un año de antigüedad"""
    if ano_antiguedad < 1:
        return 0
    
    dias = 12  # mínimo
    for ano_limite, dias_correspondientes in sorted(VACACIONES_LFT.items()):
        if ano_antiguedad >= ano_limite:
            dias = dias_correspondientes
    return dias


def calcular_antiguedad(fecha_ingreso: date, fecha_referencia: date = None) -> Dict:
    """Calcula antigüedad entre dos fechas"""
    if fecha_referencia is None:
        fecha_referencia = date.today()
    
    delta = relativedelta(fecha_referencia, fecha_ingreso)
    total_dias = (fecha_referencia - fecha_ingreso).days
    
    return {
        'anos': delta.years,
        'meses': delta.months,
        'dias': delta.days,
        'total_dias': total_dias,
        'anos_completos': delta.years
    }


def generar_periodos_vacacionales(
    fecha_ingreso: date,
    fecha_hasta: date = None,
    dias_extra_plan: int = 0
) -> List[Dict]:
    """
    Genera todos los periodos vacacionales desde el ingreso hasta la fecha indicada.
    
    Args:
        fecha_ingreso: Fecha de ingreso del empleado
        fecha_hasta: Fecha hasta la cual generar (default: hoy)
        dias_extra_plan: Días adicionales del plan sobre la ley (ej: 3 si plan es ley+3)
    
    Returns:
        Lista de periodos con: numero, fecha_inicio, fecha_fin, dias_derecho, dias_ley
    """
    if fecha_hasta is None:
        fecha_hasta = date.today()
    
    periodos = []
    antiguedad = calcular_antiguedad(fecha_ingreso, fecha_hasta)
    anos_completos = antiguedad['anos_completos']
    
    # Si aún no cumple 1 año pero ya pasó la fecha de ingreso
    # consideramos que está en su primer año laboral
    anos_a_generar = anos_completos + 1 if fecha_ingreso <= fecha_hasta else 0
    
    for ano in range(1, anos_a_generar + 1):
        fecha_inicio_periodo = fecha_ingreso + relativedelta(years=ano - 1)
        fecha_fin_periodo = fecha_ingreso + relativedelta(years=ano) - relativedelta(days=1)
        
        # Solo incluir si el periodo ya inició
        if fecha_inicio_periodo > fecha_hasta:
            continue
        
        dias_ley = obtener_dias_vacaciones_ley(ano)
        dias_derecho = dias_ley + dias_extra_plan
        
        # Fecha de vencimiento: 6 meses después del aniversario (Art. 81 LFT)
        fecha_vencimiento = fecha_inicio_periodo + relativedelta(years=1) + relativedelta(months=6)
        
        periodos.append({
            'numero_periodo': ano,
            'fecha_inicio': fecha_inicio_periodo,
            'fecha_fin': fecha_fin_periodo,
            'dias_ley': dias_ley,
            'dias_derecho': dias_derecho,
            'fecha_vencimiento': fecha_vencimiento,
            'periodo_completo': fecha_fin_periodo <= fecha_hasta
        })
    
    return periodos


def calcular_resumen_vacaciones(
    fecha_ingreso: date,
    dias_tomados_por_periodo: Dict[int, int] = None,
    dias_extra_plan: int = 0,
    fecha_referencia: date = None
) -> Dict:
    """
    Calcula resumen completo de vacaciones de un empleado.
    
    Args:
        fecha_ingreso: Fecha de ingreso
        dias_tomados_por_periodo: Dict {numero_periodo: dias_tomados}
        dias_extra_plan: Días adicionales del plan
        fecha_referencia: Fecha de referencia para cálculos
    
    Returns:
        Resumen con totales y detalle por periodo
    """
    if dias_tomados_por_periodo is None:
        dias_tomados_por_periodo = {}
    
    if fecha_referencia is None:
        fecha_referencia = date.today()
    
    periodos = generar_periodos_vacacionales(
        fecha_ingreso, fecha_referencia, dias_extra_plan
    )
    
    total_derecho = 0
    total_tomados = 0
    periodos_detalle = []
    
    for p in periodos:
        num = p['numero_periodo']
        dias_tomados = dias_tomados_por_periodo.get(num, 0)
        dias_pendientes = p['dias_derecho'] - dias_tomados
        
        total_derecho += p['dias_derecho']
        total_tomados += dias_tomados
        
        periodos_detalle.append({
            **p,
            'dias_tomados': dias_tomados,
            'dias_pendientes': dias_pendientes,
            'vencido': p['fecha_vencimiento'] < fecha_referencia and dias_pendientes > 0
        })
    
    return {
        'antiguedad': calcular_antiguedad(fecha_ingreso, fecha_referencia),
        'total_dias_derecho': total_derecho,
        'total_dias_tomados': total_tomados,
        'saldo_disponible': total_derecho - total_tomados,
        'periodos': periodos_detalle
    }


def calcular_prima_vacacional(
    dias_vacaciones: int,
    salario_diario: Decimal,
    porcentaje_prima: int = 25
) -> Decimal:
    """Calcula prima vacacional"""
    return Decimal(dias_vacaciones) * salario_diario * Decimal(porcentaje_prima) / 100


def calcular_aguinaldo(
    salario_diario: Decimal,
    dias_aguinaldo: int = 15,
    fecha_ingreso: date = None,
    fecha_calculo: date = None
) -> Dict:
    """
    Calcula aguinaldo (completo o proporcional).
    
    Args:
        salario_diario: Salario diario
        dias_aguinaldo: Días de aguinaldo según plan (mínimo 15 LFT)
        fecha_ingreso: Para calcular proporcional si no cumplió el año
        fecha_calculo: Fecha de cálculo (default: 20 dic del año actual)
    """
    if fecha_calculo is None:
        fecha_calculo = date(date.today().year, 12, 20)
    
    # Días trabajados en el año
    inicio_ano = date(fecha_calculo.year, 1, 1)
    fecha_inicio_conteo = max(fecha_ingreso, inicio_ano) if fecha_ingreso else inicio_ano
    dias_trabajados = (fecha_calculo - fecha_inicio_conteo).days + 1
    dias_ano = 365
    
    # Si trabajó todo el año
    if fecha_ingreso and fecha_ingreso <= inicio_ano:
        aguinaldo = salario_diario * dias_aguinaldo
        es_proporcional = False
    else:
        # Proporcional
        aguinaldo = (salario_diario * dias_aguinaldo * Decimal(dias_trabajados)) / Decimal(dias_ano)
        es_proporcional = True
    
    return {
        'dias_aguinaldo_plan': dias_aguinaldo,
        'dias_trabajados_ano': dias_trabajados,
        'es_proporcional': es_proporcional,
        'monto_bruto': round(aguinaldo, 2)
    }
