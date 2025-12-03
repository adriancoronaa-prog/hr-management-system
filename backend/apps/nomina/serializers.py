"""
Serializers para el módulo de Nómina
"""
from rest_framework import serializers
from .models import (
    PeriodoNomina,
    ReciboNomina,
    DetalleReciboNomina,
    IncidenciaNomina,
    ParametrosIMSS,
    TablaISR,
    TablaSubsidio
)


class ParametrosIMSSSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParametrosIMSS
        fields = '__all__'


class TablaISRSerializer(serializers.ModelSerializer):
    class Meta:
        model = TablaISR
        fields = '__all__'


class TablaSubsidioSerializer(serializers.ModelSerializer):
    class Meta:
        model = TablaSubsidio
        fields = '__all__'


class DetalleReciboNominaSerializer(serializers.ModelSerializer):
    concepto_nombre = serializers.CharField(source='concepto.nombre', read_only=True)
    concepto_tipo = serializers.CharField(source='concepto.tipo', read_only=True)
    
    class Meta:
        model = DetalleReciboNomina
        fields = [
            'id',
            'concepto',
            'concepto_nombre',
            'concepto_tipo',
            'cantidad',
            'valor_unitario',
            'importe_gravado',
            'importe_exento',
            'importe_total'
        ]


class ReciboNominaSerializer(serializers.ModelSerializer):
    empleado_nombre = serializers.CharField(source='empleado.nombre_completo', read_only=True)
    empresa_nombre = serializers.CharField(source='periodo.empresa.nombre_comercial', read_only=True)
    periodo_descripcion = serializers.CharField(source='periodo.__str__', read_only=True)
    
    class Meta:
        model = ReciboNomina
        fields = [
            'id',
            'periodo',
            'periodo_descripcion',
            'empleado',
            'empleado_nombre',
            'empresa_nombre',
            'estado',
            'salario_diario',
            'dias_trabajados',
            'dias_pagados',
            'total_percepciones',
            'total_deducciones',
            'neto_a_pagar',
            'uuid_cfdi',
            'fecha_timbrado',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'uuid_cfdi', 'fecha_timbrado']


class ReciboNominaDetalleSerializer(serializers.ModelSerializer):
    empleado_nombre = serializers.CharField(source='empleado.nombre_completo', read_only=True)
    empleado_curp = serializers.CharField(source='empleado.curp', read_only=True)
    empleado_rfc = serializers.CharField(source='empleado.rfc', read_only=True)
    empleado_nss = serializers.CharField(source='empleado.nss', read_only=True)
    empresa_nombre = serializers.CharField(source='periodo.empresa.nombre_comercial', read_only=True)
    empresa_rfc = serializers.CharField(source='periodo.empresa.rfc', read_only=True)
    detalles = DetalleReciboNominaSerializer(many=True, read_only=True)
    
    class Meta:
        model = ReciboNomina
        fields = [
            'id',
            'periodo',
            'empleado',
            'empleado_nombre',
            'empleado_curp',
            'empleado_rfc',
            'empleado_nss',
            'empresa_nombre',
            'empresa_rfc',
            'estado',
            'salario_diario',
            'salario_base_cotizacion',
            'dias_trabajados',
            'dias_pagados',
            # Percepciones
            'total_percepciones',
            'total_percepciones_gravadas',
            'total_percepciones_exentas',
            # Deducciones
            'total_deducciones',
            'base_gravable_isr',
            'isr_antes_subsidio',
            'subsidio_aplicado',
            'isr_retenido',
            'cuota_imss_obrera',
            'descuento_infonavit',
            'otras_deducciones',
            # Neto
            'neto_a_pagar',
            # CFDI
            'uuid_cfdi',
            'fecha_timbrado',
            'xml_cfdi',
            'pdf_cfdi',
            # Detalles
            'detalles',
            'created_at',
            'updated_at'
        ]


class PeriodoNominaSerializer(serializers.ModelSerializer):
    empresa_nombre = serializers.CharField(source='empresa.nombre_comercial', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    tipo_periodo_display = serializers.CharField(source='get_tipo_periodo_display', read_only=True)
    
    class Meta:
        model = PeriodoNomina
        fields = [
            'id',
            'empresa',
            'empresa_nombre',
            'tipo_periodo',
            'tipo_periodo_display',
            'numero_periodo',
            'año',
            'fecha_inicio',
            'fecha_fin',
            'fecha_pago',
            'estado',
            'estado_display',
            'total_empleados',
            'total_percepciones',
            'total_deducciones',
            'total_neto',
            'created_at'
        ]
        read_only_fields = [
            'id', 'total_empleados', 'total_percepciones',
            'total_deducciones', 'total_neto', 'created_at'
        ]


class PeriodoNominaDetalleSerializer(serializers.ModelSerializer):
    empresa_nombre = serializers.CharField(source='empresa.nombre_comercial', read_only=True)
    recibos = ReciboNominaSerializer(many=True, read_only=True)
    calculado_por_email = serializers.CharField(source='calculado_por.email', read_only=True, allow_null=True)
    aprobado_por_email = serializers.CharField(source='aprobado_por.email', read_only=True, allow_null=True)
    
    class Meta:
        model = PeriodoNomina
        fields = [
            'id',
            'empresa',
            'empresa_nombre',
            'tipo_periodo',
            'numero_periodo',
            'año',
            'fecha_inicio',
            'fecha_fin',
            'fecha_pago',
            'estado',
            'total_empleados',
            'total_percepciones',
            'total_deducciones',
            'total_neto',
            'calculado_por',
            'calculado_por_email',
            'fecha_calculo',
            'aprobado_por',
            'aprobado_por_email',
            'fecha_aprobacion',
            'notas',
            'recibos',
            'created_at',
            'updated_at'
        ]


class IncidenciaNominaSerializer(serializers.ModelSerializer):
    empleado_nombre = serializers.CharField(source='empleado.nombre_completo', read_only=True)
    empresa_nombre = serializers.CharField(source='empleado.empresa.nombre_comercial', read_only=True)
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    
    class Meta:
        model = IncidenciaNomina
        fields = [
            'id',
            'empleado',
            'empleado_nombre',
            'empresa_nombre',
            'tipo',
            'tipo_display',
            'fecha',
            'fecha_fin',
            'valor',
            'descripcion',
            'aplicado',
            'periodo_aplicado',
            'created_at'
        ]
        read_only_fields = ['id', 'aplicado', 'periodo_aplicado', 'created_at']
