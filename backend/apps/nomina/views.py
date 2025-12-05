"""
Vistas API para el módulo de Nómina
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from apps.core.permissions import (
    EsEmpleadorOAdmin, 
    AccesoNomina, 
    EmpresaFilterMixin,
    EmpleadoFilterMixin
)
from .models import (
    PeriodoNomina, 
    ReciboNomina, 
    IncidenciaNomina,
    ParametrosIMSS,
    TablaISR,
    TablaSubsidio
)
from .serializers import (
    PeriodoNominaSerializer,
    PeriodoNominaDetalleSerializer,
    ReciboNominaSerializer,
    ReciboNominaDetalleSerializer,
    IncidenciaNominaSerializer,
    ParametrosIMSSSerializer,
    TablaISRSerializer,
    TablaSubsidioSerializer
)
from .services import procesar_nomina_periodo, CalculadoraNomina


class ParametrosIMSSViewSet(viewsets.ModelViewSet):
    """
    ViewSet para parámetros IMSS y configuración fiscal
    Solo administradores pueden modificar
    """
    queryset = ParametrosIMSS.objects.all()
    serializer_class = ParametrosIMSSSerializer
    permission_classes = [EsEmpleadorOAdmin]
    
    def get_queryset(self):
        qs = super().get_queryset()
        anio = self.request.query_params.get('anio')
        if anio:
            qs = qs.filter(año=anio)
        return qs
    
    @action(detail=False, methods=['get'])
    def vigente(self, request):
        """Obtiene los parámetros IMSS vigentes"""
        from datetime import date
        config = self.get_queryset().filter(año=date.today().year).first()
        if config:
            serializer = self.get_serializer(config)
            return Response(serializer.data)
        return Response(
            {'error': 'No hay parámetros IMSS vigentes'},
            status=status.HTTP_404_NOT_FOUND
        )


class PeriodoNominaViewSet(EmpresaFilterMixin, viewsets.ModelViewSet):
    """
    ViewSet para periodos de nómina
    """
    permission_classes = [EsEmpleadorOAdmin]

    def get_queryset(self):
        qs = PeriodoNomina.objects.select_related('empresa').prefetch_related('recibos')
        user = self.request.user

        # Filtrar por empresa del header X-Empresa-ID
        empresa_id = self.request.headers.get('X-Empresa-ID')
        if empresa_id:
            qs = qs.filter(empresa_id=empresa_id)
        elif user.rol not in ['admin', 'administrador']:
            # Si no es admin y no hay header, filtrar por empresas del usuario
            qs = qs.filter(empresa__in=user.empresas.all())

        # Filtros adicionales por query params
        empresa_param = self.request.query_params.get('empresa')
        if empresa_param:
            qs = qs.filter(empresa_id=empresa_param)

        anio = self.request.query_params.get('anio')
        if anio:
            qs = qs.filter(año=anio)

        estado = self.request.query_params.get('estado')
        if estado:
            qs = qs.filter(estado=estado)

        return qs.order_by('-año', '-numero_periodo')
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return PeriodoNominaDetalleSerializer
        return PeriodoNominaSerializer
    
    def perform_create(self, serializer):
        serializer.save(creado_por=self.request.user)
    
    @action(detail=True, methods=['post'])
    def calcular(self, request, pk=None):
        """
        Calcula la nómina del periodo
        """
        periodo = self.get_object()
        
        if periodo.estado not in ['borrador', 'calculado']:
            return Response(
                {'error': 'El periodo no puede ser calculado en este estado'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            resultado = procesar_nomina_periodo(periodo.id, request.user.id)
            return Response(resultado)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def aprobar(self, request, pk=None):
        """
        Aprueba la nómina del periodo
        """
        periodo = self.get_object()
        
        if periodo.estado != 'calculado':
            return Response(
                {'error': 'El periodo debe estar calculado para aprobarse'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        periodo.estado = 'aprobado'
        periodo.aprobado_por = request.user
        periodo.fecha_aprobacion = timezone.now()
        periodo.save()
        
        serializer = self.get_serializer(periodo)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def resumen(self, request, pk=None):
        """
        Obtiene resumen del periodo
        """
        periodo = self.get_object()
        
        return Response({
            'periodo': str(periodo),
            'estado': periodo.estado,
            'total_empleados': periodo.total_empleados,
            'total_percepciones': float(periodo.total_percepciones),
            'total_deducciones': float(periodo.total_deducciones),
            'total_neto': float(periodo.total_neto),
            'recibos_por_estado': {
                'borrador': periodo.recibos.filter(estado='borrador').count(),
                'calculado': periodo.recibos.filter(estado='calculado').count(),
                'timbrado': periodo.recibos.filter(estado='timbrado').count(),
            }
        })


class ReciboNominaViewSet(EmpleadoFilterMixin, viewsets.ModelViewSet):
    """
    ViewSet para recibos de nómina individuales
    - Empleados solo ven sus propios recibos
    - RRHH ve recibos de sus empresas
    """
    permission_classes = [AccesoNomina]

    def get_queryset(self):
        qs = ReciboNomina.objects.select_related(
            'periodo', 'periodo__empresa', 'empleado'
        )
        user = self.request.user

        # Filtrar por empresa del header X-Empresa-ID
        empresa_id = self.request.headers.get('X-Empresa-ID')
        if empresa_id:
            qs = qs.filter(periodo__empresa_id=empresa_id)
        elif user.rol not in ['admin', 'administrador']:
            # Si no es admin y no hay header, filtrar por empresas del usuario
            qs = qs.filter(periodo__empresa__in=user.empresas.all())

        # Filtros
        periodo_id = self.request.query_params.get('periodo')
        if periodo_id:
            qs = qs.filter(periodo_id=periodo_id)

        empleado_id = self.request.query_params.get('empleado')
        if empleado_id and user.rol in ['admin', 'administrador']:
            qs = qs.filter(empleado_id=empleado_id)

        return qs
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ReciboNominaDetalleSerializer
        return ReciboNominaSerializer
    
    @action(detail=True, methods=['get'])
    def pdf(self, request, pk=None):
        """
        Genera PDF del recibo
        """
        recibo = self.get_object()
        
        # Si ya tiene PDF timbrado, retornarlo
        if recibo.pdf_cfdi:
            return Response({
                'url': recibo.pdf_cfdi.url,
                'uuid': recibo.uuid_cfdi
            })
        
        # Generar PDF simple (sin timbrar)
        # TODO: Implementar generación de PDF
        return Response({
            'mensaje': 'Generación de PDF pendiente de implementar',
            'recibo_id': recibo.id
        })
    
    @action(detail=True, methods=['post'])
    def timbrar(self, request, pk=None):
        """
        Timbra el recibo con el PAC configurado
        """
        recibo = self.get_object()
        
        # Solo admin puede timbrar
        if request.user.rol not in ['admin', 'administrador']:
            return Response(
                {'error': 'No tienes permiso para timbrar recibos'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if recibo.estado != 'calculado':
            return Response(
                {'error': 'El recibo debe estar calculado para timbrarse'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # TODO: Implementar timbrado con PAC
        return Response({
            'mensaje': 'Timbrado pendiente de configurar PAC',
            'recibo_id': recibo.id
        })


class IncidenciaNominaViewSet(EmpresaFilterMixin, viewsets.ModelViewSet):
    """
    ViewSet para incidencias de nómina (faltas, horas extra, etc.)
    """
    serializer_class = IncidenciaNominaSerializer
    permission_classes = [EsEmpleadorOAdmin]

    def get_queryset(self):
        qs = IncidenciaNomina.objects.select_related('empleado', 'empleado__empresa')
        user = self.request.user

        # Filtrar por empresa del header X-Empresa-ID
        empresa_id = self.request.headers.get('X-Empresa-ID')
        if empresa_id:
            qs = qs.filter(empleado__empresa_id=empresa_id)
        elif user.rol not in ['admin', 'administrador']:
            # Si no es admin y no hay header, filtrar por empresas del usuario
            qs = qs.filter(empleado__empresa__in=user.empresas.all())

        # Filtros
        empleado_id = self.request.query_params.get('empleado')
        if empleado_id:
            qs = qs.filter(empleado_id=empleado_id)

        tipo = self.request.query_params.get('tipo')
        if tipo:
            qs = qs.filter(tipo=tipo)

        aplicado = self.request.query_params.get('aplicado')
        if aplicado is not None:
            qs = qs.filter(aplicado=aplicado.lower() == 'true')

        return qs
    
    @action(detail=False, methods=['get'])
    def pendientes(self, request):
        """
        Obtiene incidencias pendientes de aplicar
        """
        qs = self.get_queryset().filter(aplicado=False)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)
