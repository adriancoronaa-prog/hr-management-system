from django.contrib import admin
from django.utils.html import format_html
from .models import CategoriaDocumento, DocumentoEmpleado, Documento, FragmentoDocumento


@admin.register(CategoriaDocumento)
class CategoriaDocumentoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'empresa', 'requiere_vencimiento', 'es_obligatorio', 'activo', 'orden']
    list_filter = ['empresa', 'requiere_vencimiento', 'es_obligatorio', 'activo']
    search_fields = ['nombre', 'descripcion']
    ordering = ['orden', 'nombre']


@admin.register(DocumentoEmpleado)
class DocumentoEmpleadoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'empleado', 'categoria', 'fecha_vencimiento', 'version', 'activo']
    list_filter = ['categoria', 'activo', 'empleado__empresa']
    search_fields = ['nombre', 'empleado__nombre', 'empleado__apellido_paterno']
    raw_id_fields = ['empleado', 'categoria', 'documento_padre', 'created_by', 'updated_by']
    date_hierarchy = 'created_at'


@admin.register(Documento)
class DocumentoAdmin(admin.ModelAdmin):
    list_display = [
        'titulo', 'tipo', 'empresa', 'tipo_acceso',
        'procesado_badge', 'total_fragmentos', 'created_at'
    ]
    list_filter = ['tipo', 'tipo_acceso', 'procesado', 'empresa', 'activo']
    search_fields = ['titulo', 'descripcion', 'tags']
    readonly_fields = [
        'procesado', 'fecha_procesado', 'error_procesamiento',
        'contenido_texto', 'tipo_mime', 'tamaño_bytes'
    ]
    raw_id_fields = ['empresa', 'created_by', 'updated_by']
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Información básica', {
            'fields': ('titulo', 'descripcion', 'tipo', 'archivo')
        }),
        ('Acceso', {
            'fields': ('empresa', 'tipo_acceso', 'activo')
        }),
        ('Metadatos', {
            'fields': ('version', 'fecha_vigencia', 'tags')
        }),
        ('Procesamiento RAG', {
            'fields': ('procesado', 'fecha_procesado', 'error_procesamiento', 'contenido_texto'),
            'classes': ('collapse',)
        }),
        ('Archivo', {
            'fields': ('tipo_mime', 'tamaño_bytes'),
            'classes': ('collapse',)
        }),
        ('Auditoría', {
            'fields': ('created_by', 'updated_by'),
            'classes': ('collapse',)
        }),
    )

    actions = ['procesar_documentos', 'reprocesar_documentos']

    def procesado_badge(self, obj):
        if obj.procesado and not obj.error_procesamiento:
            return format_html('<span style="color: green;">Procesado</span>')
        elif obj.error_procesamiento:
            return format_html('<span style="color: red;" title="{}">Error</span>', obj.error_procesamiento[:100])
        return format_html('<span style="color: orange;">Pendiente</span>')
    procesado_badge.short_description = 'Estado'

    def total_fragmentos(self, obj):
        return obj.fragmentos.count()
    total_fragmentos.short_description = 'Fragmentos'

    @admin.action(description='Procesar documentos seleccionados')
    def procesar_documentos(self, request, queryset):
        from .services import ProcesadorDocumentos
        procesador = ProcesadorDocumentos()
        exitosos = 0
        fallidos = 0

        for doc in queryset.filter(procesado=False):
            resultado = procesador.procesar_documento(doc)
            if resultado['success']:
                exitosos += 1
            else:
                fallidos += 1

        self.message_user(
            request,
            f'Procesados: {exitosos} exitosos, {fallidos} fallidos'
        )

    @admin.action(description='Reprocesar documentos seleccionados')
    def reprocesar_documentos(self, request, queryset):
        from .services import ProcesadorDocumentos
        procesador = ProcesadorDocumentos()
        exitosos = 0
        fallidos = 0

        for doc in queryset:
            resultado = procesador.procesar_documento(doc)
            if resultado['success']:
                exitosos += 1
            else:
                fallidos += 1

        self.message_user(
            request,
            f'Reprocesados: {exitosos} exitosos, {fallidos} fallidos'
        )


@admin.register(FragmentoDocumento)
class FragmentoDocumentoAdmin(admin.ModelAdmin):
    list_display = ['documento', 'numero_fragmento', 'num_caracteres', 'tiene_embedding']
    list_filter = ['documento__tipo', 'documento__empresa']
    search_fields = ['contenido', 'documento__titulo']
    raw_id_fields = ['documento']
    readonly_fields = ['embedding', 'num_tokens', 'num_caracteres']

    def tiene_embedding(self, obj):
        return bool(obj.embedding)
    tiene_embedding.boolean = True
    tiene_embedding.short_description = 'Embedding'
