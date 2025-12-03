from django.contrib import admin
from .models import Conversacion, Mensaje, ComandoIA, ConfiguracionIA


class MensajeInline(admin.TabularInline):
    model = Mensaje
    extra = 0
    readonly_fields = ['rol', 'contenido', 'created_at', 'accion_ejecutada']
    can_delete = False


@admin.register(Conversacion)
class ConversacionAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'titulo', 'empresa_contexto', 'activa', 'created_at']
    list_filter = ['activa', 'empresa_contexto']
    search_fields = ['usuario__email', 'titulo']
    inlines = [MensajeInline]


@admin.register(Mensaje)
class MensajeAdmin(admin.ModelAdmin):
    list_display = ['conversacion', 'rol', 'contenido_preview', 
                    'accion_ejecutada', 'created_at']
    list_filter = ['rol', 'accion_ejecutada']
    search_fields = ['contenido']
    
    def contenido_preview(self, obj):
        return obj.contenido[:100] + '...' if len(obj.contenido) > 100 else obj.contenido
    contenido_preview.short_description = 'Contenido'


@admin.register(ComandoIA)
class ComandoIAAdmin(admin.ModelAdmin):
    list_display = ['mensaje', 'intencion', 'estado', 'created_at']
    list_filter = ['estado', 'intencion']


@admin.register(ConfiguracionIA)
class ConfiguracionIAAdmin(admin.ModelAdmin):
    list_display = ['empresa', 'modelo', 'activo', 'puede_crear_entidades']
    list_filter = ['activo']
