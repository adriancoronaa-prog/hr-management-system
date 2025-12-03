from django.contrib import admin
from .models import CatalogoKPI, AsignacionKPI, RegistroAvanceKPI, Evaluacion


@admin.register(CatalogoKPI)
class CatalogoKPIAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'categoria', 'tipo_medicion', 'frecuencia', 'activo']
    list_filter = ['categoria', 'tipo_medicion', 'frecuencia', 'activo', 'empresa']
    search_fields = ['nombre', 'descripcion']


@admin.register(AsignacionKPI)
class AsignacionKPIAdmin(admin.ModelAdmin):
    list_display = ['nombre_kpi', 'empleado', 'periodo', 'meta', 'valor_logrado', 'porcentaje_cumplimiento', 'estado']
    list_filter = ['estado', 'periodo']
    search_fields = ['nombre_personalizado', 'empleado__nombre', 'empleado__apellido_paterno']
    raw_id_fields = ['empleado', 'asignado_por', 'kpi_catalogo']


@admin.register(RegistroAvanceKPI)
class RegistroAvanceKPIAdmin(admin.ModelAdmin):
    list_display = ['asignacion', 'fecha', 'valor', 'registrado_por']
    list_filter = ['fecha']
    raw_id_fields = ['asignacion', 'registrado_por']


@admin.register(Evaluacion)
class EvaluacionAdmin(admin.ModelAdmin):
    list_display = ['empleado', 'tipo', 'periodo', 'puntuacion_final', 'estado']
    list_filter = ['tipo', 'estado', 'periodo']
    search_fields = ['empleado__nombre', 'empleado__apellido_paterno']
    raw_id_fields = ['empleado', 'evaluador']
