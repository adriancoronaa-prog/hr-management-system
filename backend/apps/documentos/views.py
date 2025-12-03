from rest_framework import viewsets, serializers, parsers, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta
from .models import CategoriaDocumento, DocumentoEmpleado, Documento, TipoDocumento, NivelAcceso
from .services import ProcesadorDocumentos


class CategoriaDocumentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoriaDocumento
        fields = '__all__'


class DocumentoEmpleadoSerializer(serializers.ModelSerializer):
    empleado_nombre = serializers.CharField(source='empleado.nombre_completo', read_only=True)
    categoria_nombre = serializers.CharField(source='categoria.nombre', read_only=True)
    dias_para_vencer = serializers.SerializerMethodField()
    
    class Meta:
        model = DocumentoEmpleado
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'tipo_mime', 'tamaño_bytes']
    
    def get_dias_para_vencer(self, obj):
        if obj.fecha_vencimiento:
            return (obj.fecha_vencimiento - timezone.now().date()).days
        return None


class CategoriaDocumentoViewSet(viewsets.ModelViewSet):
    queryset = CategoriaDocumento.objects.all()
    serializer_class = CategoriaDocumentoSerializer
    filterset_fields = ['empresa', 'activo', 'es_obligatorio']
    
    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset()
        if not user.es_super_admin:
            # Categorías globales + de sus empresas
            from django.db.models import Q
            qs = qs.filter(
                Q(empresa__isnull=True) | Q(empresa__in=user.empresas.all())
            )
        return qs


class DocumentoEmpleadoViewSet(viewsets.ModelViewSet):
    queryset = DocumentoEmpleado.objects.select_related('empleado', 'categoria')
    serializer_class = DocumentoEmpleadoSerializer
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]
    filterset_fields = ['empleado', 'categoria', 'activo']
    
    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset()
        
        if not user.es_super_admin:
            qs = qs.filter(empleado__empresa__in=user.empresas.all())
        
        # Filtro: por_vencer
        por_vencer = self.request.query_params.get('por_vencer')
        if por_vencer:
            dias = int(por_vencer)
            fecha_limite = timezone.now().date() + timedelta(days=dias)
            qs = qs.filter(
                activo=True,
                fecha_vencimiento__isnull=False,
                fecha_vencimiento__lte=fecha_limite
            )
        
        return qs
    
    def perform_create(self, serializer):
        archivo = self.request.FILES.get('archivo')
        extra = {'created_by': self.request.user}
        if archivo:
            extra['tipo_mime'] = archivo.content_type
            extra['tamaño_bytes'] = archivo.size
        serializer.save(**extra)


# ============ DOCUMENTOS RAG ============

class DocumentoSerializer(serializers.ModelSerializer):
    """Serializer para documentos RAG"""
    empresa_nombre = serializers.CharField(source='empresa.razon_social', read_only=True)
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    tipo_acceso_display = serializers.CharField(source='get_tipo_acceso_display', read_only=True)
    total_fragmentos = serializers.IntegerField(read_only=True)
    created_by_email = serializers.CharField(source='created_by.email', read_only=True)

    class Meta:
        model = Documento
        fields = [
            'id', 'empresa', 'empresa_nombre', 'titulo', 'descripcion',
            'tipo', 'tipo_display', 'archivo', 'tipo_mime', 'tamaño_bytes',
            'tipo_acceso', 'tipo_acceso_display', 'procesado', 'fecha_procesado',
            'error_procesamiento', 'version', 'fecha_vigencia', 'tags',
            'activo', 'total_fragmentos', 'created_at', 'created_by_email'
        ]
        read_only_fields = [
            'id', 'tipo_mime', 'tamaño_bytes', 'procesado', 'fecha_procesado',
            'error_procesamiento', 'total_fragmentos', 'created_at'
        ]


class DocumentoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar documentos RAG.
    Solo accesible por Admin y RRHH.
    """
    queryset = Documento.objects.select_related('empresa', 'created_by')
    serializer_class = DocumentoSerializer
    parser_classes = [parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser]
    filterset_fields = ['empresa', 'tipo', 'tipo_acceso', 'procesado', 'activo']

    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset()

        # Solo Admin y RRHH pueden ver documentos
        if user.rol not in ['administrador', 'empleador']:
            return qs.none()

        # Admin ve todo, RRHH solo de sus empresas
        if user.rol == 'empleador':
            qs = qs.filter(empresa__in=user.empresas.all())

        return qs.order_by('-created_at')

    def perform_create(self, serializer):
        """Al crear documento, guardar metadatos y procesar automáticamente"""
        archivo = self.request.FILES.get('archivo')
        extra = {
            'created_by': self.request.user,
            'updated_by': self.request.user,
        }

        if archivo:
            extra['tipo_mime'] = archivo.content_type
            extra['tamaño_bytes'] = archivo.size

        documento = serializer.save(**extra)

        # Procesar automáticamente si hay archivo
        if archivo:
            procesador = ProcesadorDocumentos()
            procesador.procesar_documento(documento)

    def perform_update(self, serializer):
        """Al actualizar, reprocesar si cambió el archivo"""
        archivo = self.request.FILES.get('archivo')
        extra = {'updated_by': self.request.user}

        if archivo:
            extra['tipo_mime'] = archivo.content_type
            extra['tamaño_bytes'] = archivo.size
            extra['procesado'] = False  # Marcar para reprocesar

        documento = serializer.save(**extra)

        # Reprocesar si hay nuevo archivo
        if archivo:
            procesador = ProcesadorDocumentos()
            procesador.procesar_documento(documento)

    @action(detail=True, methods=['post'])
    def procesar(self, request, pk=None):
        """Procesar/reprocesar un documento manualmente"""
        documento = self.get_object()

        procesador = ProcesadorDocumentos()
        resultado = procesador.procesar_documento(documento)

        if resultado['success']:
            return Response({
                'mensaje': 'Documento procesado exitosamente',
                'fragmentos_creados': resultado['fragmentos_creados'],
                'texto_extraido': resultado['texto_extraido'],
            })
        else:
            return Response({
                'error': resultado['error']
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def estadisticas(self, request):
        """Obtener estadísticas de documentos"""
        qs = self.get_queryset()

        total = qs.count()
        procesados = qs.filter(procesado=True).count()
        con_error = qs.filter(error_procesamiento__isnull=False).exclude(error_procesamiento='').count()

        por_tipo = {}
        for tipo in TipoDocumento:
            por_tipo[tipo.label] = qs.filter(tipo=tipo.value).count()

        return Response({
            'total': total,
            'procesados': procesados,
            'pendientes': total - procesados,
            'con_error': con_error,
            'por_tipo': por_tipo,
        })
