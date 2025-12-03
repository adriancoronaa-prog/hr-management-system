from rest_framework import viewsets, serializers
from django.utils import timezone
from datetime import timedelta
from .models import Contrato


class ContratoSerializer(serializers.ModelSerializer):
    empleado_nombre = serializers.CharField(source='empleado.nombre_completo', read_only=True)
    dias_para_vencer = serializers.SerializerMethodField()
    
    class Meta:
        model = Contrato
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_dias_para_vencer(self, obj):
        if obj.fecha_fin:
            return (obj.fecha_fin - timezone.now().date()).days
        return None


class ContratoViewSet(viewsets.ModelViewSet):
    queryset = Contrato.objects.select_related('empleado', 'empleado__empresa')
    serializer_class = ContratoSerializer
    filterset_fields = ['empleado', 'estado', 'tipo_contrato', 'empleado__empresa']
    ordering_fields = ['fecha_inicio', 'fecha_fin']
    
    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset()
        
        if not user.es_super_admin:
            qs = qs.filter(empleado__empresa__in=user.empresas.all())
        
        # Filtro especial: por_vencer
        por_vencer = self.request.query_params.get('por_vencer')
        if por_vencer:
            dias = int(por_vencer)
            fecha_limite = timezone.now().date() + timedelta(days=dias)
            qs = qs.filter(
                estado='vigente',
                fecha_fin__isnull=False,
                fecha_fin__lte=fecha_limite
            )
        
        return qs
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
