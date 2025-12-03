from rest_framework import viewsets, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from collections import defaultdict
from .models import (
    PlanPrestaciones,
    PrestacionAdicional,
    AjusteIndividual,
    CATEGORIAS_PRESTACION,
    TIPOS_PRESTACION_CATALOGO,
    TIPO_A_CATEGORIA,
)
from apps.empleados.services import VACACIONES_LFT


class PrestacionAdicionalSerializer(serializers.ModelSerializer):
    categoria_display = serializers.CharField(source='get_categoria_display', read_only=True)
    tipo_prestacion_display = serializers.SerializerMethodField()
    plan_nombre = serializers.CharField(source='plan.nombre', read_only=True)
    empresa_nombre = serializers.CharField(source='plan.empresa.razon_social', read_only=True)

    class Meta:
        model = PrestacionAdicional
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_tipo_prestacion_display(self, obj):
        """Busca el nombre legible del tipo en el catalogo"""
        if not obj.tipo_prestacion:
            return None
        for tipo_key, tipo_nombre, _ in TIPOS_PRESTACION_CATALOGO:
            if tipo_key == obj.tipo_prestacion:
                return tipo_nombre
        return obj.tipo_prestacion


class PlanPrestacionesSerializer(serializers.ModelSerializer):
    prestaciones_adicionales = PrestacionAdicionalSerializer(many=True, read_only=True)
    empresa_nombre = serializers.CharField(source='empresa.razon_social', read_only=True)
    
    # Comparativa con ley
    comparativa_ley = serializers.SerializerMethodField()
    
    class Meta:
        model = PlanPrestaciones
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_comparativa_ley(self, obj):
        return {
            'vacaciones': {
                'ley': 'Según tabla LFT',
                'plan': f'+{obj.vacaciones_dias_extra} días sobre ley',
                'diferencia': obj.vacaciones_dias_extra
            },
            'prima_vacacional': {
                'ley': 25,
                'plan': obj.prima_vacacional_porcentaje,
                'diferencia': obj.prima_vacacional_porcentaje - 25
            },
            'aguinaldo': {
                'ley': 15,
                'plan': obj.aguinaldo_dias,
                'diferencia': obj.aguinaldo_dias - 15
            }
        }


class PlanPrestacionesViewSet(viewsets.ModelViewSet):
    queryset = PlanPrestaciones.objects.prefetch_related('prestaciones_adicionales')
    serializer_class = PlanPrestacionesSerializer
    filterset_fields = ['empresa', 'activo', 'es_default']
    
    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset()
        if not user.es_super_admin:
            qs = qs.filter(empresa__in=user.empresas.all())
        return qs
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=False, methods=['get'])
    def referencia_ley(self, request):
        """Retorna tabla de referencia de prestaciones de ley"""
        return Response({
            'vacaciones_por_antiguedad': VACACIONES_LFT,
            'prima_vacacional_minima': 25,
            'aguinaldo_minimo_dias': 15,
            'prima_dominical': 25
        })


class AjusteIndividualSerializer(serializers.ModelSerializer):
    empleado_nombre = serializers.CharField(source='empleado.nombre_completo', read_only=True)
    
    class Meta:
        model = AjusteIndividual
        fields = '__all__'
        read_only_fields = ['id', 'created_at']


class AjusteIndividualViewSet(viewsets.ModelViewSet):
    queryset = AjusteIndividual.objects.select_related('empleado')
    serializer_class = AjusteIndividualSerializer
    filterset_fields = ['empleado', 'concepto', 'activo']

    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset()
        if not user.es_super_admin:
            qs = qs.filter(empleado__empresa__in=user.empresas.all())
        return qs

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class PrestacionAdicionalViewSet(viewsets.ModelViewSet):
    """ViewSet para gestionar prestaciones adicionales"""
    queryset = PrestacionAdicional.objects.select_related('plan', 'plan__empresa')
    serializer_class = PrestacionAdicionalSerializer
    filterset_fields = ['plan', 'categoria', 'tipo_prestacion', 'activo', 'periodicidad']
    search_fields = ['nombre', 'descripcion', 'proveedor']

    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset()
        if not user.es_super_admin:
            qs = qs.filter(plan__empresa__in=user.empresas.all())
        return qs

    @action(detail=False, methods=['get'])
    def catalogo(self, request):
        """
        Retorna el catalogo completo de categorias y tipos de prestacion
        agrupados por categoria
        """
        # Agrupar tipos por categoria
        tipos_por_categoria = defaultdict(list)
        for tipo_key, tipo_nombre, categoria in TIPOS_PRESTACION_CATALOGO:
            tipos_por_categoria[categoria].append({
                'key': tipo_key,
                'nombre': tipo_nombre,
            })

        # Construir respuesta con categorias y sus tipos
        categorias_con_tipos = []
        for cat_key, cat_nombre in CATEGORIAS_PRESTACION:
            categorias_con_tipos.append({
                'key': cat_key,
                'nombre': cat_nombre,
                'tipos': tipos_por_categoria.get(cat_key, [])
            })

        return Response({
            'categorias': [
                {'key': k, 'nombre': v} for k, v in CATEGORIAS_PRESTACION
            ],
            'tipos': [
                {'key': t[0], 'nombre': t[1], 'categoria': t[2]}
                for t in TIPOS_PRESTACION_CATALOGO
            ],
            'categorias_con_tipos': categorias_con_tipos,
        })

    @action(detail=False, methods=['get'])
    def por_categoria(self, request):
        """
        Filtra prestaciones adicionales por categoria
        Uso: GET /api/prestaciones/adicionales/por_categoria/?categoria=salud
        """
        categoria = request.query_params.get('categoria')
        if not categoria:
            return Response(
                {'error': 'Parametro categoria es requerido'},
                status=400
            )

        # Validar categoria
        categorias_validas = [c[0] for c in CATEGORIAS_PRESTACION]
        if categoria not in categorias_validas:
            return Response(
                {'error': f'Categoria invalida. Opciones: {categorias_validas}'},
                status=400
            )

        qs = self.get_queryset().filter(categoria=categoria)
        serializer = self.get_serializer(qs, many=True)
        return Response({
            'categoria': categoria,
            'categoria_display': dict(CATEGORIAS_PRESTACION).get(categoria),
            'total': qs.count(),
            'prestaciones': serializer.data,
        })
