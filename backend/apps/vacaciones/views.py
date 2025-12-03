from rest_framework import viewsets, serializers, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import PeriodoVacacional, SolicitudVacaciones


class PeriodoVacacionalSerializer(serializers.ModelSerializer):
    dias_pendientes = serializers.ReadOnlyField()
    
    class Meta:
        model = PeriodoVacacional
        fields = '__all__'


class SolicitudVacacionesSerializer(serializers.ModelSerializer):
    empleado_nombre = serializers.CharField(source='empleado.nombre_completo', read_only=True)
    
    class Meta:
        model = SolicitudVacaciones
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'aprobado_por', 'fecha_aprobacion']


class SolicitudVacacionesViewSet(viewsets.ModelViewSet):
    queryset = SolicitudVacaciones.objects.select_related('empleado', 'periodo_vacacional')
    serializer_class = SolicitudVacacionesSerializer
    filterset_fields = ['empleado', 'estado', 'empleado__empresa']
    ordering_fields = ['fecha_inicio', 'created_at']
    
    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset()
        if not user.es_super_admin:
            qs = qs.filter(empleado__empresa__in=user.empresas.all())
        return qs
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def aprobar(self, request, pk=None):
        solicitud = self.get_object()
        
        if solicitud.estado != SolicitudVacaciones.Estado.PENDIENTE:
            return Response(
                {'error': 'Solo se pueden aprobar solicitudes pendientes'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        solicitud.estado = SolicitudVacaciones.Estado.APROBADA
        solicitud.aprobado_por = request.user
        solicitud.fecha_aprobacion = timezone.now()
        solicitud.comentarios = request.data.get('comentarios', '')
        solicitud.save()
        
        # Actualizar días tomados en el periodo
        if solicitud.periodo_vacacional:
            periodo = solicitud.periodo_vacacional
            periodo.dias_tomados += solicitud.dias_solicitados
            periodo.save()
        
        return Response(SolicitudVacacionesSerializer(solicitud).data)
    
    @action(detail=True, methods=['post'])
    def rechazar(self, request, pk=None):
        solicitud = self.get_object()
        
        if solicitud.estado != SolicitudVacaciones.Estado.PENDIENTE:
            return Response(
                {'error': 'Solo se pueden rechazar solicitudes pendientes'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        solicitud.estado = SolicitudVacaciones.Estado.RECHAZADA
        solicitud.aprobado_por = request.user
        solicitud.fecha_aprobacion = timezone.now()
        solicitud.comentarios = request.data.get('comentarios', '')
        solicitud.save()
        
        return Response(SolicitudVacacionesSerializer(solicitud).data)
