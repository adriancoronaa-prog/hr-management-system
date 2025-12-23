"""
Serializers para el módulo de desempeño
"""
from rest_framework import serializers
from .models import (
    CatalogoKPI, AsignacionKPI, RegistroAvanceKPI,
    Evaluacion, CatalogoCompetencia, EvaluacionCompetencia,
    RetroalimentacionContinua
)


class CatalogoKPISerializer(serializers.ModelSerializer):
    categoria_display = serializers.CharField(source='get_categoria_display', read_only=True)
    tipo_medicion_display = serializers.CharField(source='get_tipo_medicion_display', read_only=True)
    frecuencia_display = serializers.CharField(source='get_frecuencia_display', read_only=True)

    class Meta:
        model = CatalogoKPI
        fields = [
            'id', 'nombre', 'descripcion', 'categoria', 'categoria_display',
            'tipo_medicion', 'tipo_medicion_display', 'unidad', 'frecuencia',
            'frecuencia_display', 'valor_minimo', 'valor_objetivo', 'valor_excelente',
            'es_mayor_mejor', 'activo'
        ]


class AsignacionKPISerializer(serializers.ModelSerializer):
    empleado_nombre = serializers.CharField(source='empleado.nombre_completo', read_only=True)
    nombre_kpi = serializers.ReadOnlyField()
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    tiene_cambios_pendientes = serializers.SerializerMethodField()

    class Meta:
        model = AsignacionKPI
        fields = [
            'id', 'empleado', 'empleado_nombre', 'nombre_kpi', 'descripcion_personalizada',
            'periodo', 'fecha_inicio', 'fecha_fin', 'meta', 'peso', 'es_mayor_mejor',
            'estado', 'estado_display', 'valor_logrado', 'porcentaje_cumplimiento',
            'tiene_cambios_pendientes', 'created_at'
        ]

    def get_tiene_cambios_pendientes(self, obj):
        return bool(obj.cambios_pendientes)


class EvaluacionSerializer(serializers.ModelSerializer):
    empleado_nombre = serializers.CharField(source='empleado.nombre_completo', read_only=True)
    evaluador_nombre = serializers.SerializerMethodField()
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    clasificacion_9box = serializers.ReadOnlyField()
    competencias_evaluadas_count = serializers.SerializerMethodField()

    class Meta:
        model = Evaluacion
        fields = [
            'id', 'empleado', 'empleado_nombre', 'evaluador_nombre', 'tipo', 'tipo_display',
            'periodo', 'fecha_inicio', 'fecha_fin', 'modalidad', 'estado', 'estado_display',
            'puntuacion_kpis', 'puntuacion_competencias', 'puntuacion_final',
            'clasificacion_desempeno', 'clasificacion_potencial', 'clasificacion_9box',
            'logros', 'areas_mejora', 'competencias_evaluadas_count', 'created_at'
        ]

    def get_evaluador_nombre(self, obj):
        if obj.evaluador:
            return obj.evaluador.nombre_completo
        return None

    def get_competencias_evaluadas_count(self, obj):
        return obj.competencias_evaluadas.count()


class RetroalimentacionSerializer(serializers.ModelSerializer):
    empleado_nombre = serializers.CharField(source='empleado.nombre_completo', read_only=True)
    autor_nombre = serializers.SerializerMethodField()
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)

    class Meta:
        model = RetroalimentacionContinua
        fields = [
            'id', 'empleado', 'empleado_nombre', 'autor_nombre', 'tipo', 'tipo_display',
            'contenido', 'es_privado', 'requiere_seguimiento', 'seguimiento_completado',
            'created_at'
        ]

    def get_autor_nombre(self, obj):
        if obj.autor:
            return obj.autor.nombre_completo
        return 'Sistema'
