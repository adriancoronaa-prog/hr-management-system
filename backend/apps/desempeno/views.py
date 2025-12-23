"""
Views REST para el módulo de desempeño
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Avg, Count, Q
from .models import (
    CatalogoKPI, AsignacionKPI, Evaluacion,
    CatalogoCompetencia, RetroalimentacionContinua
)
from .serializers import (
    CatalogoKPISerializer, AsignacionKPISerializer,
    EvaluacionSerializer, RetroalimentacionSerializer
)


class CatalogoKPIViewSet(viewsets.ReadOnlyModelViewSet):
    """Catálogo de KPIs disponibles"""
    serializer_class = CatalogoKPISerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        # KPIs globales + de las empresas del usuario
        empresa_ids = list(user.empresas.values_list('id', flat=True))
        return CatalogoKPI.objects.filter(
            Q(empresa__isnull=True) | Q(empresa_id__in=empresa_ids),
            activo=True
        )


class MisKPIsViewSet(viewsets.ReadOnlyModelViewSet):
    """KPIs asignados al usuario actual"""
    serializer_class = AsignacionKPISerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'empleado') and user.empleado:
            return AsignacionKPI.objects.filter(
                empleado=user.empleado
            ).order_by('-fecha_inicio')
        return AsignacionKPI.objects.none()

    @action(detail=False, methods=['get'])
    def activos(self, request):
        """Solo KPIs en estado activo"""
        qs = self.get_queryset().filter(estado='activo')
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def resumen(self, request):
        """Resumen de KPIs del usuario"""
        qs = self.get_queryset()
        activos = qs.filter(estado='activo')

        # Calcular promedio de cumplimiento
        promedio = activos.filter(
            porcentaje_cumplimiento__isnull=False
        ).aggregate(promedio=Avg('porcentaje_cumplimiento'))['promedio']

        return Response({
            'total': qs.count(),
            'activos': activos.count(),
            'promedio_cumplimiento': round(promedio, 1) if promedio else None,
            'pendientes_cambio': qs.filter(
                cambios_pendientes__isnull=False
            ).exclude(cambios_pendientes={}).count(),
        })


class KPIsEquipoViewSet(viewsets.ReadOnlyModelViewSet):
    """KPIs del equipo (para jefes)"""
    serializer_class = AsignacionKPISerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if not hasattr(user, 'empleado') or not user.empleado:
            return AsignacionKPI.objects.none()

        # Obtener subordinados
        subordinados = user.empleado.subordinados.all()
        if not subordinados.exists() and user.rol not in ['administrador', 'empleador']:
            return AsignacionKPI.objects.none()

        if user.rol in ['administrador', 'empleador']:
            # Ver todos los de la empresa
            empresa_ids = list(user.empresas.values_list('id', flat=True))
            return AsignacionKPI.objects.filter(
                empleado__empresa_id__in=empresa_ids
            ).select_related('empleado').order_by('-fecha_inicio')

        return AsignacionKPI.objects.filter(
            empleado__in=subordinados
        ).select_related('empleado').order_by('-fecha_inicio')


class EvaluacionViewSet(viewsets.ReadOnlyModelViewSet):
    """Evaluaciones de desempeño"""
    serializer_class = EvaluacionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        empresa_ids = list(user.empresas.values_list('id', flat=True))

        qs = Evaluacion.objects.filter(
            empleado__empresa_id__in=empresa_ids
        ).select_related('empleado', 'evaluador')

        # Filtrar por empleado si viene en params
        empleado_id = self.request.query_params.get('empleado')
        if empleado_id:
            qs = qs.filter(empleado_id=empleado_id)

        return qs.order_by('-fecha_fin')

    @action(detail=False, methods=['get'])
    def mis_evaluaciones(self, request):
        """Evaluaciones del usuario actual"""
        if not hasattr(request.user, 'empleado') or not request.user.empleado:
            return Response([])

        qs = Evaluacion.objects.filter(
            empleado=request.user.empleado
        ).order_by('-fecha_fin')
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def matriz_9box(self, request):
        """Datos para la matriz 9-box"""
        qs = self.get_queryset().filter(
            clasificacion_desempeno__isnull=False,
            clasificacion_potencial__isnull=False
        ).exclude(
            clasificacion_desempeno='',
        ).exclude(
            clasificacion_potencial=''
        )

        # Agrupar por clasificación
        matriz = {}
        for eval_obj in qs:
            clas = eval_obj.clasificacion_9box
            if clas:
                if clas not in matriz:
                    matriz[clas] = []
                matriz[clas].append({
                    'id': str(eval_obj.empleado.id),
                    'nombre': eval_obj.empleado.nombre_completo,
                    'puesto': eval_obj.empleado.puesto,
                    'puntuacion': float(eval_obj.puntuacion_final) if eval_obj.puntuacion_final else None
                })

        return Response(matriz)


class RetroalimentacionViewSet(viewsets.ReadOnlyModelViewSet):
    """Retroalimentación continua"""
    serializer_class = RetroalimentacionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        # Si es empleado, solo ve las suyas (no privadas o las propias)
        if hasattr(user, 'empleado') and user.empleado:
            if user.rol in ['administrador', 'empleador', 'rrhh']:
                # Admin/RRHH ve todas de su empresa
                empresa_ids = list(user.empresas.values_list('id', flat=True))
                return RetroalimentacionContinua.objects.filter(
                    empleado__empresa_id__in=empresa_ids
                ).order_by('-created_at')
            else:
                # Empleado ve las suyas
                return RetroalimentacionContinua.objects.filter(
                    Q(empleado=user.empleado) & (Q(es_privado=False) | Q(autor=user.empleado))
                ).order_by('-created_at')

        return RetroalimentacionContinua.objects.none()
