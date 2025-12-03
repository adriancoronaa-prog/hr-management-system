"""
Vistas para reportes y dashboards
"""
from datetime import date
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from apps.empresas.models import Empresa
from apps.empleados.models import Empleado
from .services import MetricasEmpresa, MetricasEmpleado
from .serializers import (
    DashboardEmpresaSerializer, 
    DashboardEmpleadoSerializer,
    LiquidacionSerializer,
    SolicitudLiquidacionSerializer
)
from .pdf_generator import PDFDashboardEmpresa, PDFDashboardEmpleado


class DashboardEmpresaView(APIView):
    """GET /api/reportes/empresa/{id}/dashboard/"""
    permission_classes = [AllowAny]  # Temporal para pruebas
    
    def get(self, request, empresa_id):
        empresa = get_object_or_404(Empresa, id=empresa_id)
        metricas = MetricasEmpresa(empresa)
        datos = metricas.obtener_resumen_completo()
        serializer = DashboardEmpresaSerializer(datos)
        return Response(serializer.data)


class DashboardEmpresaPDFView(APIView):
    """GET /api/reportes/empresa/{id}/dashboard/pdf/"""
    permission_classes = [AllowAny]  # Temporal para pruebas
    
    def get(self, request, empresa_id):
        empresa = get_object_or_404(Empresa, id=empresa_id)
        metricas = MetricasEmpresa(empresa)
        datos = metricas.obtener_resumen_completo()
        
        generador = PDFDashboardEmpresa()
        pdf_buffer = generador.generar(datos)
        
        nombre_archivo = f"dashboard_{empresa.rfc}_{date.today().isoformat()}.pdf"
        
        response = HttpResponse(pdf_buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{nombre_archivo}"'
        return response


class DashboardEmpleadoView(APIView):
    """GET /api/reportes/empleado/{id}/dashboard/"""
    permission_classes = [AllowAny]  # Temporal para pruebas
    
    def get(self, request, empleado_id):
        empleado = get_object_or_404(Empleado, id=empleado_id)
        
        incluir_liquidacion = request.query_params.get('incluir_liquidacion', 'false').lower() == 'true'
        
        metricas = MetricasEmpleado(empleado)
        datos = metricas.obtener_resumen_completo(incluir_liquidacion=incluir_liquidacion)
        
        if incluir_liquidacion:
            es_despido = request.query_params.get('es_despido_injustificado', 'true').lower() == 'true'
            fecha_baja_str = request.query_params.get('fecha_baja')
            
            fecha_baja = None
            if fecha_baja_str:
                try:
                    fecha_baja = date.fromisoformat(fecha_baja_str)
                except ValueError:
                    pass
            
            datos['liquidacion'] = metricas.calcular_liquidacion(
                fecha_baja=fecha_baja,
                es_despido_injustificado=es_despido
            )
        
        serializer = DashboardEmpleadoSerializer(datos)
        return Response(serializer.data)


class DashboardEmpleadoPDFView(APIView):
    """GET /api/reportes/empleado/{id}/dashboard/pdf/"""
    permission_classes = [AllowAny]  # Temporal para pruebas
    
    def get(self, request, empleado_id):
        empleado = get_object_or_404(Empleado, id=empleado_id)
        
        incluir_liquidacion = request.query_params.get('incluir_liquidacion', 'false').lower() == 'true'
        es_despido = request.query_params.get('es_despido_injustificado', 'true').lower() == 'true'
        fecha_baja_str = request.query_params.get('fecha_baja')
        
        fecha_baja = None
        if fecha_baja_str:
            try:
                fecha_baja = date.fromisoformat(fecha_baja_str)
            except ValueError:
                pass
        
        metricas = MetricasEmpleado(empleado)
        datos = metricas.obtener_resumen_completo(incluir_liquidacion=False)
        
        if incluir_liquidacion:
            datos['liquidacion'] = metricas.calcular_liquidacion(
                fecha_baja=fecha_baja,
                es_despido_injustificado=es_despido
            )
        
        generador = PDFDashboardEmpleado()
        pdf_buffer = generador.generar(datos, incluir_liquidacion=incluir_liquidacion)
        
        nombre_base = f"reporte_{empleado.curp or empleado.id}_{date.today().isoformat()}"
        if incluir_liquidacion:
            nombre_base += "_liquidacion"
        nombre_archivo = f"{nombre_base}.pdf"
        
        response = HttpResponse(pdf_buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{nombre_archivo}"'
        return response


class CalcularLiquidacionView(APIView):
    """POST/GET /api/reportes/empleado/{id}/liquidacion/"""
    permission_classes = [AllowAny]  # Temporal para pruebas
    
    def get(self, request, empleado_id):
        empleado = get_object_or_404(Empleado, id=empleado_id)
        
        es_despido = request.query_params.get('es_despido_injustificado', 'true').lower() == 'true'
        fecha_baja_str = request.query_params.get('fecha_baja')
        
        fecha_baja = None
        if fecha_baja_str:
            try:
                fecha_baja = date.fromisoformat(fecha_baja_str)
            except ValueError:
                pass
        
        metricas = MetricasEmpleado(empleado)
        liquidacion = metricas.calcular_liquidacion(
            fecha_baja=fecha_baja,
            es_despido_injustificado=es_despido
        )
        
        serializer = LiquidacionSerializer(liquidacion)
        return Response(serializer.data)
    
    def post(self, request, empleado_id):
        empleado = get_object_or_404(Empleado, id=empleado_id)
        
        serializer_input = SolicitudLiquidacionSerializer(data=request.data)
        serializer_input.is_valid(raise_exception=True)
        
        fecha_baja = serializer_input.validated_data.get('fecha_baja')
        es_despido = serializer_input.validated_data.get('es_despido_injustificado', True)
        
        metricas = MetricasEmpleado(empleado)
        liquidacion = metricas.calcular_liquidacion(
            fecha_baja=fecha_baja,
            es_despido_injustificado=es_despido
        )
        
        serializer = LiquidacionSerializer(liquidacion)
        return Response(serializer.data)


class LiquidacionPDFView(APIView):
    """GET /api/reportes/empleado/{id}/liquidacion/pdf/"""
    permission_classes = [AllowAny]  # Temporal para pruebas
    
    def get(self, request, empleado_id):
        empleado = get_object_or_404(Empleado, id=empleado_id)
        
        es_despido = request.query_params.get('es_despido_injustificado', 'true').lower() == 'true'
        fecha_baja_str = request.query_params.get('fecha_baja')
        
        fecha_baja = None
        if fecha_baja_str:
            try:
                fecha_baja = date.fromisoformat(fecha_baja_str)
            except ValueError:
                pass
        
        metricas = MetricasEmpleado(empleado)
        datos = metricas.obtener_resumen_completo(incluir_liquidacion=False)
        datos['liquidacion'] = metricas.calcular_liquidacion(
            fecha_baja=fecha_baja,
            es_despido_injustificado=es_despido
        )
        
        generador = PDFDashboardEmpleado()
        pdf_buffer = generador.generar(datos, incluir_liquidacion=True)
        
        tipo = "liquidacion" if es_despido else "finiquito"
        nombre_archivo = f"{tipo}_{empleado.curp or empleado.id}_{date.today().isoformat()}.pdf"
        
        response = HttpResponse(pdf_buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{nombre_archivo}"'
        return response
