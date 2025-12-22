"""
Serializers para reportes y dashboards
"""
from rest_framework import serializers


class MetricaEmpleadosSerializer(serializers.Serializer):
    total = serializers.IntegerField()
    activos = serializers.IntegerField()
    inactivos = serializers.IntegerField()
    bajas = serializers.IntegerField()
    antiguedad_promedio_anos = serializers.FloatField()
    salario_diario_promedio = serializers.DecimalField(max_digits=12, decimal_places=2)
    salario_mensual_promedio = serializers.DecimalField(max_digits=12, decimal_places=2)
    nomina_mensual_estimada = serializers.DecimalField(max_digits=14, decimal_places=2)
    por_departamento = serializers.ListField(required=False)


class MetricaNominaSerializer(serializers.Serializer):
    periodos_procesados_ano = serializers.IntegerField()
    total_percepciones_ano = serializers.DecimalField(max_digits=14, decimal_places=2)
    total_deducciones_ano = serializers.DecimalField(max_digits=14, decimal_places=2)
    total_neto_pagado_ano = serializers.DecimalField(max_digits=14, decimal_places=2)
    ultimo_periodo = serializers.DictField(required=False, allow_null=True)


class MetricaVacacionesSerializer(serializers.Serializer):
    dias_pendientes_total = serializers.IntegerField()
    dias_tomados_ano = serializers.IntegerField()
    pasivo_vacaciones = serializers.DecimalField(max_digits=14, decimal_places=2)


class CostosProyectadosSerializer(serializers.Serializer):
    aguinaldo_proyectado = serializers.DecimalField(max_digits=14, decimal_places=2)
    prima_vacacional_proyectada = serializers.DecimalField(max_digits=14, decimal_places=2)
    nomina_mensual = serializers.DecimalField(max_digits=14, decimal_places=2)
    costo_anual_estimado = serializers.DecimalField(max_digits=14, decimal_places=2)


class AlertaSerializer(serializers.Serializer):
    tipo = serializers.CharField()
    nivel = serializers.CharField()
    empleado = serializers.CharField()
    mensaje = serializers.CharField()


class DashboardEmpresaSerializer(serializers.Serializer):
    empresa = serializers.DictField()
    empleados = MetricaEmpleadosSerializer()
    nomina = MetricaNominaSerializer()
    vacaciones = MetricaVacacionesSerializer()
    costos_proyectados = CostosProyectadosSerializer()
    alertas = AlertaSerializer(many=True)
    fecha_generacion = serializers.CharField()


class InfoEmpleadoSerializer(serializers.Serializer):
    id = serializers.CharField()  # UUID as string
    nombre_completo = serializers.CharField()
    curp = serializers.CharField(allow_null=True)
    rfc = serializers.CharField(allow_null=True)
    nss = serializers.CharField(allow_null=True)
    fecha_ingreso = serializers.CharField()
    puesto = serializers.CharField(allow_null=True)
    departamento = serializers.CharField(allow_null=True)
    tipo_contrato = serializers.CharField(allow_null=True)
    estado = serializers.CharField()
    empresa = serializers.CharField(allow_null=True)


class AntiguedadSerializer(serializers.Serializer):
    anos = serializers.IntegerField()
    meses = serializers.IntegerField()
    dias = serializers.IntegerField()
    total_dias = serializers.IntegerField()
    descripcion = serializers.CharField()


class SalarioSerializer(serializers.Serializer):
    salario_diario = serializers.DecimalField(max_digits=12, decimal_places=2)
    salario_semanal = serializers.DecimalField(max_digits=12, decimal_places=2)
    salario_quincenal = serializers.DecimalField(max_digits=12, decimal_places=2)
    salario_mensual = serializers.DecimalField(max_digits=12, decimal_places=2)
    salario_anual = serializers.DecimalField(max_digits=14, decimal_places=2)


class VacacionesEmpleadoSerializer(serializers.Serializer):
    dias_por_ley = serializers.IntegerField()
    dias_tomados_ano = serializers.IntegerField()
    dias_pendientes = serializers.IntegerField()
    prima_vacacional_porcentaje = serializers.IntegerField()
    prima_vacacional_monto = serializers.DecimalField(max_digits=12, decimal_places=2)
    proximo_aniversario = serializers.CharField()


class AguinaldoSerializer(serializers.Serializer):
    dias = serializers.IntegerField()
    monto = serializers.DecimalField(max_digits=12, decimal_places=2)
    es_proporcional = serializers.BooleanField()
    dias_trabajados = serializers.IntegerField()


class PrimaVacacionalSerializer(serializers.Serializer):
    dias_vacaciones = serializers.IntegerField()
    porcentaje = serializers.IntegerField()
    monto = serializers.DecimalField(max_digits=12, decimal_places=2)


class PrestacionesSerializer(serializers.Serializer):
    aguinaldo = AguinaldoSerializer()
    prima_vacacional = PrimaVacacionalSerializer()


class HistorialNominaSerializer(serializers.Serializer):
    recibos_count = serializers.IntegerField()
    total_percepciones_12m = serializers.DecimalField(max_digits=14, decimal_places=2)
    total_deducciones_12m = serializers.DecimalField(max_digits=14, decimal_places=2)
    promedio_neto_mensual = serializers.DecimalField(max_digits=12, decimal_places=2)


class FiniquitoSerializer(serializers.Serializer):
    aguinaldo_proporcional = serializers.DecimalField(max_digits=12, decimal_places=2)
    vacaciones_proporcionales_dias = serializers.DecimalField(max_digits=8, decimal_places=2)
    vacaciones_proporcionales_monto = serializers.DecimalField(max_digits=12, decimal_places=2)
    prima_vacacional = serializers.DecimalField(max_digits=12, decimal_places=2)
    subtotal_finiquito = serializers.DecimalField(max_digits=12, decimal_places=2)


class LiquidacionDetalleSerializer(serializers.Serializer):
    aplica = serializers.BooleanField()
    indemnizacion_3_meses = serializers.DecimalField(max_digits=12, decimal_places=2)
    indemnizacion_20_dias_ano = serializers.DecimalField(max_digits=12, decimal_places=2)
    anos_para_calculo = serializers.IntegerField(required=False)
    prima_antiguedad = serializers.DecimalField(max_digits=12, decimal_places=2)
    subtotal_liquidacion = serializers.DecimalField(max_digits=12, decimal_places=2)


class LiquidacionSerializer(serializers.Serializer):
    fecha_baja = serializers.CharField()
    tipo = serializers.CharField()
    salario_diario = serializers.DecimalField(max_digits=12, decimal_places=2)
    salario_diario_integrado = serializers.DecimalField(max_digits=12, decimal_places=2)
    antiguedad = AntiguedadSerializer()
    finiquito = FiniquitoSerializer()
    liquidacion = LiquidacionDetalleSerializer()
    total_a_pagar = serializers.DecimalField(max_digits=14, decimal_places=2)


class DashboardEmpleadoSerializer(serializers.Serializer):
    empleado = InfoEmpleadoSerializer()
    antiguedad = AntiguedadSerializer()
    salario = SalarioSerializer()
    vacaciones = VacacionesEmpleadoSerializer()
    prestaciones = PrestacionesSerializer()
    historial_nomina = HistorialNominaSerializer()
    liquidacion = LiquidacionSerializer(required=False, allow_null=True)
    fecha_generacion = serializers.CharField()


class SolicitudLiquidacionSerializer(serializers.Serializer):
    fecha_baja = serializers.DateField(required=False, allow_null=True)
    es_despido_injustificado = serializers.BooleanField(default=True)
