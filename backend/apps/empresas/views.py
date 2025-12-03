from rest_framework import serializers, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters import rest_framework as filters
from .models import Empresa


class EmpresaSerializer(serializers.ModelSerializer):
    direccion_completa = serializers.ReadOnlyField()
    total_empleados = serializers.SerializerMethodField()
    
    class Meta:
        model = Empresa
        fields = [
            'id', 'rfc', 'razon_social', 'nombre_comercial', 'regimen_fiscal',
            'calle', 'numero_exterior', 'numero_interior', 'colonia',
            'codigo_postal', 'municipio', 'estado', 'direccion_completa',
            'representante_legal', 'telefono', 'email', 'logo',
            'activa', 'created_at', 'updated_at', 'total_empleados'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_total_empleados(self, obj):
        return obj.empleados.filter(estado='activo').count()


class EmpresaListSerializer(serializers.ModelSerializer):
    """Serializer ligero para listados"""
    total_empleados = serializers.SerializerMethodField()
    
    class Meta:
        model = Empresa
        fields = ['id', 'rfc', 'razon_social', 'activa', 'total_empleados']
    
    def get_total_empleados(self, obj):
        return obj.empleados.filter(estado='activo').count()


class EmpresaFilter(filters.FilterSet):
    class Meta:
        model = Empresa
        fields = {
            'activa': ['exact'],
            'razon_social': ['icontains'],
            'rfc': ['exact', 'icontains'],
        }


class EmpresaViewSet(viewsets.ModelViewSet):
    queryset = Empresa.objects.all()
    serializer_class = EmpresaSerializer
    filterset_class = EmpresaFilter
    search_fields = ['razon_social', 'nombre_comercial', 'rfc']
    ordering_fields = ['razon_social', 'created_at']
    
    def get_queryset(self):
        user = self.request.user
        if user.es_super_admin:
            return Empresa.objects.all()
        return user.empresas.all()
    
    def get_serializer_class(self):
        if self.action == 'list':
            return EmpresaListSerializer
        return EmpresaSerializer
    
    def perform_create(self, serializer):
        empresa = serializer.save(created_by=self.request.user)
        # Asignar al usuario que la crea
        self.request.user.empresas.add(empresa)
    
    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)
    
    def destroy(self, request, *args, **kwargs):
        empresa = self.get_object()
        # Soft delete - solo desactivar
        if empresa.empleados.filter(estado='activo').exists():
            return Response(
                {'error': 'No se puede desactivar una empresa con empleados activos'},
                status=status.HTTP_400_BAD_REQUEST
            )
        empresa.activa = False
        empresa.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
