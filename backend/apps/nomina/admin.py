from django.contrib import admin
from .models import (
    TablaISR,
    TablaSubsidio,
    ParametrosIMSS,
    PeriodoNomina,
    ConceptoNomina,
    ReciboNomina,
    DetalleReciboNomina,
    IncidenciaNomina
)


@admin.register(TablaISR)
class TablaISRAdmin(admin.ModelAdmin):
    list_display = ['año', 'periodicidad', 'limite_inferior', 'limite_superior', 'cuota_fija', 'porcentaje_excedente']
    list_filter = ['año', 'periodicidad']
    ordering = ['año', 'periodicidad', 'limite_inferior']


@admin.register(TablaSubsidio)
class TablaSubsidioAdmin(admin.ModelAdmin):
    list_display = ['año', 'periodicidad', 'limite_inferior', 'limite_superior', 'subsidio']
    list_filter = ['año', 'periodicidad']
    ordering = ['año', 'periodicidad', 'limite_inferior']


@admin.register(ParametrosIMSS)
class ParametrosIMSSAdmin(admin.ModelAdmin):
    list_display = ['año', 'uma_diaria', 'salario_minimo_general', 'tope_sbc_veces_uma']
    list_filter = ['año']


@admin.register(PeriodoNomina)
class PeriodoNominaAdmin(admin.ModelAdmin):
    list_display = ['empresa', 'tipo_periodo', 'numero_periodo', 'año', 'fecha_inicio', 'fecha_fin', 'estado']
    list_filter = ['empresa', 'tipo_periodo', 'año', 'estado']
    search_fields = ['empresa__razon_social']


@admin.register(ConceptoNomina)
class ConceptoNominaAdmin(admin.ModelAdmin):
    list_display = ['codigo_interno', 'nombre', 'tipo', 'es_gravable', 'activo']
    list_filter = ['tipo', 'activo']
    search_fields = ['codigo_interno', 'nombre']


@admin.register(ReciboNomina)
class ReciboNominaAdmin(admin.ModelAdmin):
    list_display = ['empleado', 'periodo', 'total_percepciones', 'total_deducciones', 'neto_a_pagar', 'estado']
    list_filter = ['periodo__empresa', 'estado']
    search_fields = ['empleado__nombre', 'empleado__apellido_paterno']


@admin.register(IncidenciaNomina)
class IncidenciaNominaAdmin(admin.ModelAdmin):
    list_display = ['empleado', 'tipo', 'fecha_inicio', 'fecha_fin', 'aplicado']
    list_filter = ['tipo', 'aplicado']
    search_fields = ['empleado__nombre']