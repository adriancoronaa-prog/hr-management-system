from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters import rest_framework as filters
from .models import Empleado
from .serializers import EmpleadoSerializer, EmpleadoListSerializer, EmpleadoCreateSerializer
from .services import calcular_resumen_vacaciones, calcular_aguinaldo


class EmpleadoFilter(filters.FilterSet):
    fecha_ingreso_desde = filters.DateFilter(field_name='fecha_ingreso', lookup_expr='gte')
    fecha_ingreso_hasta = filters.DateFilter(field_name='fecha_ingreso', lookup_expr='lte')
    
    class Meta:
        model = Empleado
        fields = {
            'empresa': ['exact'],
            'estado': ['exact'],
            'departamento': ['exact', 'icontains'],
            'puesto': ['icontains'],
        }


class EmpleadoViewSet(viewsets.ModelViewSet):
    queryset = Empleado.objects.select_related('empresa', 'plan_prestaciones')
    filterset_class = EmpleadoFilter
    search_fields = ['nombre', 'apellido_paterno', 'apellido_materno', 'curp', 'rfc']
    ordering_fields = ['apellido_paterno', 'fecha_ingreso', 'created_at']
    
    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset()
        if not user.es_super_admin:
            qs = qs.filter(empresa__in=user.empresas.all())
        return qs
    
    def get_serializer_class(self):
        if self.action == 'list':
            return EmpleadoListSerializer
        if self.action == 'create':
            return EmpleadoCreateSerializer
        return EmpleadoSerializer
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)
    
    @action(detail=True, methods=['get'])
    def vacaciones(self, request, pk=None):
        """Obtiene resumen detallado de vacaciones del empleado"""
        empleado = self.get_object()
        
        dias_extra = 0
        if empleado.plan_prestaciones:
            config = empleado.plan_prestaciones.get_config_vacaciones()
            if config:
                dias_extra = config.get('dias_extra', 0)
        
        dias_tomados = {}
        for periodo in empleado.periodos_vacacionales.all():
            dias_tomados[periodo.numero_periodo] = periodo.dias_tomados
        
        resumen = calcular_resumen_vacaciones(
            empleado.fecha_ingreso,
            dias_tomados,
            dias_extra
        )
        
        return Response(resumen)
    
    @action(detail=True, methods=['get'])
    def aguinaldo(self, request, pk=None):
        """Calcula aguinaldo del empleado"""
        empleado = self.get_object()
        
        if not empleado.salario_diario:
            return Response(
                {'error': 'Empleado sin salario diario registrado'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        dias_aguinaldo = 15  # Ley
        if empleado.plan_prestaciones:
            config = empleado.plan_prestaciones.get_config_aguinaldo()
            if config:
                dias_aguinaldo = config.get('dias', 15)
        
        resultado = calcular_aguinaldo(
            empleado.salario_diario,
            dias_aguinaldo,
            empleado.fecha_ingreso
        )
        
        return Response(resultado)
    
    @action(detail=True, methods=['post'])
    def registrar_baja(self, request, pk=None):
        """Registra baja del empleado"""
        empleado = self.get_object()
        
        fecha_baja = request.data.get('fecha_baja')
        motivo = request.data.get('motivo', '')
        
        if not fecha_baja:
            return Response(
                {'error': 'Fecha de baja requerida'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        empleado.estado = Empleado.Estado.BAJA
        empleado.fecha_baja = fecha_baja
        empleado.motivo_baja = motivo
        empleado.save()
        
        # TODO: Calcular finiquito
        
        return Response(EmpleadoSerializer(empleado).data)
