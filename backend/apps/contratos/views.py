from rest_framework import viewsets, serializers, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.utils import timezone
from datetime import timedelta
from .models import Contrato, Adenda


class ContratoSerializer(serializers.ModelSerializer):
    empleado_nombre = serializers.SerializerMethodField()
    empresa_nombre = serializers.SerializerMethodField()
    tipo_contrato_display = serializers.CharField(source='get_tipo_contrato_display', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    dias_para_vencer = serializers.SerializerMethodField()
    es_vigente = serializers.BooleanField(read_only=True)
    esta_por_vencer = serializers.BooleanField(read_only=True)
    numero_renovaciones = serializers.IntegerField(read_only=True)
    documento_url = serializers.SerializerMethodField()
    documento_firmado_url = serializers.SerializerMethodField()

    class Meta:
        model = Contrato
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by', 'updated_by']

    def get_empleado_nombre(self, obj):
        if obj.empleado:
            return f"{obj.empleado.nombre} {obj.empleado.apellido_paterno}"
        return None

    def get_empresa_nombre(self, obj):
        if obj.empleado and obj.empleado.empresa:
            return obj.empleado.empresa.nombre_comercial or obj.empleado.empresa.razon_social
        return None

    def get_dias_para_vencer(self, obj):
        if obj.fecha_fin:
            return (obj.fecha_fin - timezone.now().date()).days
        return None

    def get_documento_url(self, obj):
        if obj.documento:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.documento.url)
            return obj.documento.url
        return None

    def get_documento_firmado_url(self, obj):
        if obj.documento_firmado:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.documento_firmado.url)
            return obj.documento_firmado.url
        return None


class ContratoListSerializer(serializers.ModelSerializer):
    """Serializer ligero para listados"""
    empleado_nombre = serializers.SerializerMethodField()
    empresa_nombre = serializers.SerializerMethodField()
    tipo_contrato_display = serializers.CharField(source='get_tipo_contrato_display', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    dias_para_vencer = serializers.SerializerMethodField()

    class Meta:
        model = Contrato
        fields = [
            'id', 'empleado', 'empleado_nombre', 'empresa_nombre',
            'tipo_contrato', 'tipo_contrato_display',
            'fecha_inicio', 'fecha_fin',
            'puesto', 'departamento',
            'salario_mensual', 'salario_diario',
            'estado', 'estado_display',
            'dias_para_vencer',
        ]

    def get_empleado_nombre(self, obj):
        if obj.empleado:
            return f"{obj.empleado.nombre} {obj.empleado.apellido_paterno}"
        return None

    def get_empresa_nombre(self, obj):
        if obj.empleado and obj.empleado.empresa:
            return obj.empleado.empresa.nombre_comercial or obj.empleado.empresa.razon_social
        return None

    def get_dias_para_vencer(self, obj):
        if obj.fecha_fin:
            return (obj.fecha_fin - timezone.now().date()).days
        return None


class ContratoViewSet(viewsets.ModelViewSet):
    queryset = Contrato.objects.select_related('empleado', 'empleado__empresa')
    filterset_fields = ['empleado', 'estado', 'tipo_contrato', 'empleado__empresa']
    ordering_fields = ['fecha_inicio', 'fecha_fin']
    search_fields = ['empleado__nombre', 'empleado__apellido_paterno', 'puesto']

    def get_serializer_class(self):
        if self.action == 'list':
            return ContratoListSerializer
        return ContratoSerializer

    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset()
        empresa_id = self.request.headers.get('X-Empresa-ID')

        if empresa_id:
            qs = qs.filter(empleado__empresa_id=empresa_id)
        elif user.rol not in ['admin', 'administrador']:
            qs = qs.filter(empleado__empresa__in=user.empresas.all())

        # Filtro especial: por_vencer
        por_vencer = self.request.query_params.get('por_vencer')
        if por_vencer:
            dias = int(por_vencer)
            fecha_limite = timezone.now().date() + timedelta(days=dias)
            qs = qs.filter(
                estado='vigente',
                fecha_fin__isnull=False,
                fecha_fin__lte=fecha_limite,
                fecha_fin__gte=timezone.now().date()
            )

        return qs

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    @action(detail=True, methods=['post'])
    def renovar(self, request, pk=None):
        """Renueva un contrato existente"""
        contrato = self.get_object()

        fecha_inicio = request.data.get('fecha_inicio')
        fecha_fin = request.data.get('fecha_fin')

        if not fecha_inicio:
            return Response(
                {'error': 'La fecha de inicio es requerida'},
                status=status.HTTP_400_BAD_REQUEST
            )

        nuevo_contrato = contrato.renovar(
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            tipo_contrato=request.data.get('tipo_contrato'),
            puesto=request.data.get('puesto'),
            departamento=request.data.get('departamento'),
            salario_diario=request.data.get('salario_diario'),
            salario_mensual=request.data.get('salario_mensual'),
            jornada=request.data.get('jornada'),
            horario=request.data.get('horario'),
            created_by=request.user
        )

        return Response(ContratoSerializer(nuevo_contrato, context={'request': request}).data)

    @action(detail=True, methods=['post'])
    def terminar(self, request, pk=None):
        """Termina un contrato"""
        contrato = self.get_object()

        motivo = request.data.get('motivo', '')
        fecha = request.data.get('fecha')

        contrato.terminar(motivo=motivo, fecha=fecha)

        return Response(ContratoSerializer(contrato, context={'request': request}).data)

    @action(detail=False, methods=['get'])
    def resumen(self, request):
        """Obtiene resumen de contratos"""
        qs = self.get_queryset()

        total = qs.count()
        vigentes = qs.filter(estado='vigente').count()
        vencidos = qs.filter(estado='vencido').count()
        renovados = qs.filter(estado='renovado').count()

        # Por vencer en 30 dias
        fecha_limite = timezone.now().date() + timedelta(days=30)
        por_vencer = qs.filter(
            estado='vigente',
            fecha_fin__isnull=False,
            fecha_fin__lte=fecha_limite,
            fecha_fin__gte=timezone.now().date()
        ).count()

        return Response({
            'total': total,
            'vigentes': vigentes,
            'vencidos': vencidos,
            'renovados': renovados,
            'por_vencer_30_dias': por_vencer,
        })

    @action(detail=True, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def subir_documento(self, request, pk=None):
        """Subir el documento del contrato firmado"""
        contrato = self.get_object()

        archivo = request.FILES.get('archivo')
        if not archivo:
            return Response({'error': 'No se proporcionó archivo'}, status=status.HTTP_400_BAD_REQUEST)

        # Validar tipo de archivo
        allowed_types = ['application/pdf', 'image/jpeg', 'image/png', 'image/jpg']
        if archivo.content_type not in allowed_types:
            return Response(
                {'error': 'Tipo de archivo no permitido. Use PDF, JPG o PNG.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validar tamaño (máx 10MB)
        if archivo.size > 10 * 1024 * 1024:
            return Response(
                {'error': 'El archivo excede el tamaño máximo de 10MB'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Guardar archivo
        contrato.documento_firmado = archivo
        contrato.fecha_firma = timezone.now().date()
        contrato.save()

        return Response(ContratoSerializer(contrato, context={'request': request}).data)

    @action(detail=True, methods=['delete'])
    def eliminar_documento(self, request, pk=None):
        """Eliminar el documento del contrato"""
        contrato = self.get_object()

        if contrato.documento_firmado:
            contrato.documento_firmado.delete()
            contrato.fecha_firma = None
            contrato.save()

        return Response({'mensaje': 'Documento eliminado correctamente'})
