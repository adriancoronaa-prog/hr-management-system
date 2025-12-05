from rest_framework import serializers
from .models import Empleado, DocumentoEmpleado
from .services import calcular_resumen_vacaciones, calcular_antiguedad
from apps.core.validators import validar_rfc, validar_curp, validar_nss, validar_clabe


class EmpleadoListSerializer(serializers.ModelSerializer):
    """Serializer ligero para listados"""
    nombre_completo = serializers.ReadOnlyField()
    empresa_nombre = serializers.CharField(source='empresa.razon_social', read_only=True)
    antiguedad_anos = serializers.SerializerMethodField()

    class Meta:
        model = Empleado
        fields = [
            'id', 'nombre', 'apellido_paterno', 'apellido_materno',
            'nombre_completo', 'puesto', 'departamento',
            'empresa', 'empresa_nombre', 'estado', 'fecha_ingreso',
            'antiguedad_anos', 'foto', 'email_corporativo'
        ]
    
    def get_antiguedad_anos(self, obj):
        return obj.anos_completos


class EmpleadoSerializer(serializers.ModelSerializer):
    """Serializer completo para detalle/creación"""
    nombre_completo = serializers.ReadOnlyField()
    antiguedad = serializers.SerializerMethodField()
    antiguedad_anos = serializers.SerializerMethodField()
    proximo_aniversario = serializers.ReadOnlyField()
    salario_mensual = serializers.ReadOnlyField()
    resumen_vacaciones = serializers.SerializerMethodField()
    empresa_nombre = serializers.SerializerMethodField()
    jefe_directo_nombre = serializers.SerializerMethodField()

    class Meta:
        model = Empleado
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by', 'updated_by']

    def get_antiguedad(self, obj):
        return obj.antiguedad

    def get_antiguedad_anos(self, obj):
        return obj.anos_completos

    def get_empresa_nombre(self, obj):
        if obj.empresa:
            return obj.empresa.nombre_comercial or obj.empresa.razon_social
        return None

    def get_jefe_directo_nombre(self, obj):
        if obj.jefe_directo:
            return f"{obj.jefe_directo.nombre} {obj.jefe_directo.apellido_paterno}"
        return None
    
    def get_resumen_vacaciones(self, obj):
        # Obtener días extra del plan si existe
        dias_extra = 0
        if obj.plan_prestaciones:
            config = obj.plan_prestaciones.get_config_vacaciones()
            if config:
                dias_extra = config.get('dias_extra', 0)
        
        # Obtener días tomados de periodos existentes
        dias_tomados = {}
        for periodo in obj.periodos_vacacionales.all():
            dias_tomados[periodo.numero_periodo] = periodo.dias_tomados
        
        return calcular_resumen_vacaciones(
            obj.fecha_ingreso,
            dias_tomados,
            dias_extra
        )


class EmpleadoCreateSerializer(serializers.ModelSerializer):
    """Serializer para creación con alta retroactiva"""

    # Campo opcional para registrar historial de vacaciones al dar de alta
    vacaciones_historico = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        write_only=True,
        help_text="Lista de {periodo: int, dias_tomados: int} para registro retroactivo"
    )

    # Campo opcional para indicar saldo actual directo
    saldo_vacaciones_actual = serializers.IntegerField(
        required=False,
        write_only=True,
        help_text="Saldo actual de vacaciones (el sistema calcula los tomados)"
    )

    class Meta:
        model = Empleado
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by', 'updated_by']

    def validate_rfc(self, value):
        """Valida RFC mexicano"""
        if not value or value.lower() in ['pendiente', 'no tiene', 'n/a', '-']:
            return value
        es_valido, mensaje = validar_rfc(value, tipo='fisica')
        if not es_valido:
            raise serializers.ValidationError(mensaje)
        return value.upper().strip()

    def validate_curp(self, value):
        """Valida CURP mexicana"""
        if not value or value.lower() in ['pendiente', 'no tiene', 'n/a', '-']:
            return value
        es_valido, mensaje = validar_curp(value)
        if not es_valido:
            raise serializers.ValidationError(mensaje)
        return value.upper().strip()

    def validate_nss(self, value):
        """Valida NSS del IMSS"""
        if not value or value.lower() in ['pendiente', 'no tiene', 'n/a', '-']:
            return value
        es_valido, mensaje = validar_nss(value)
        if not es_valido:
            raise serializers.ValidationError(mensaje)
        return value.strip()

    def validate_clabe(self, value):
        """Valida CLABE bancaria"""
        if not value or value.lower() in ['pendiente', 'no tiene', 'n/a', '-']:
            return value
        es_valido, mensaje = validar_clabe(value)
        if not es_valido:
            raise serializers.ValidationError(mensaje)
        return value.strip()

    def validate_fecha_ingreso(self, value):
        """Permite fechas pasadas (retroactivas)"""
        from django.utils import timezone
        if value > timezone.now().date():
            raise serializers.ValidationError("La fecha de ingreso no puede ser futura")
        return value
    
    def create(self, validated_data):
        vacaciones_historico = validated_data.pop('vacaciones_historico', None)
        saldo_actual = validated_data.pop('saldo_vacaciones_actual', None)
        
        empleado = super().create(validated_data)
        
        # Generar periodos vacacionales
        from apps.vacaciones.models import PeriodoVacacional
        from .services import generar_periodos_vacacionales
        
        dias_extra = 0
        if empleado.plan_prestaciones:
            config = empleado.plan_prestaciones.get_config_vacaciones()
            if config:
                dias_extra = config.get('dias_extra', 0)
        
        periodos = generar_periodos_vacacionales(
            empleado.fecha_ingreso,
            dias_extra_plan=dias_extra
        )
        
        # Calcular días tomados si se proporcionó saldo actual
        dias_tomados_por_periodo = {}
        if vacaciones_historico:
            for item in vacaciones_historico:
                dias_tomados_por_periodo[item['periodo']] = item['dias_tomados']
        elif saldo_actual is not None:
            # Calcular cuántos días se han tomado en total
            total_derecho = sum(p['dias_derecho'] for p in periodos)
            total_tomados = total_derecho - saldo_actual
            
            # Distribuir días tomados empezando por periodos más antiguos
            restante = total_tomados
            for p in periodos:
                if restante <= 0:
                    break
                tomados_este = min(restante, p['dias_derecho'])
                dias_tomados_por_periodo[p['numero_periodo']] = tomados_este
                restante -= tomados_este
        
        # Crear periodos en BD
        for p in periodos:
            PeriodoVacacional.objects.create(
                empleado=empleado,
                numero_periodo=p['numero_periodo'],
                fecha_inicio_periodo=p['fecha_inicio'],
                fecha_fin_periodo=p['fecha_fin'],
                dias_derecho=p['dias_derecho'],
                dias_tomados=dias_tomados_por_periodo.get(p['numero_periodo'], 0),
                fecha_vencimiento=p['fecha_vencimiento'],
                es_historico=True
            )

        return empleado


class DocumentoEmpleadoSerializer(serializers.ModelSerializer):
    """Serializer para documentos del expediente del empleado"""
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    estatus_display = serializers.CharField(source='get_estatus_display', read_only=True)
    archivo_url = serializers.SerializerMethodField()
    revisado_por_nombre = serializers.SerializerMethodField()

    class Meta:
        model = DocumentoEmpleado
        fields = [
            'id', 'empleado', 'tipo', 'tipo_display', 'nombre', 'descripcion',
            'archivo', 'archivo_url', 'tipo_archivo', 'tamaño_bytes',
            'fecha_documento', 'fecha_vencimiento', 'folio',
            'estatus', 'estatus_display', 'revisado_por', 'revisado_por_nombre',
            'fecha_revision', 'notas_revision',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'empleado', 'tipo_archivo', 'tamaño_bytes',
            'created_at', 'updated_at', 'revisado_por', 'fecha_revision'
        ]

    def get_archivo_url(self, obj):
        if obj.archivo:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.archivo.url)
            return obj.archivo.url
        return None

    def get_revisado_por_nombre(self, obj):
        if obj.revisado_por:
            return f"{obj.revisado_por.nombre} {obj.revisado_por.apellido}"
        return None
