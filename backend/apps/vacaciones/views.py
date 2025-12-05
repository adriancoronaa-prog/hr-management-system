from rest_framework import viewsets, serializers, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Sum, Q
from datetime import date
from .models import (
    PeriodoVacacional,
    SolicitudVacaciones,
    calcular_dias_vacaciones_lft,
    calcular_antiguedad_anios
)
from apps.empleados.models import Empleado


class PeriodoVacacionalSerializer(serializers.ModelSerializer):
    dias_pendientes = serializers.ReadOnlyField()
    empleado_nombre = serializers.SerializerMethodField()

    class Meta:
        model = PeriodoVacacional
        fields = '__all__'

    def get_empleado_nombre(self, obj):
        if obj.empleado:
            return f"{obj.empleado.nombre} {obj.empleado.apellido_paterno}"
        return None


class SolicitudVacacionesSerializer(serializers.ModelSerializer):
    empleado_nombre = serializers.SerializerMethodField()
    empleado_puesto = serializers.SerializerMethodField()
    empresa_nombre = serializers.SerializerMethodField()
    aprobador_nombre = serializers.SerializerMethodField()
    puede_aprobar = serializers.SerializerMethodField()
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)

    class Meta:
        model = SolicitudVacaciones
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'aprobado_por', 'fecha_aprobacion']

    def get_empleado_nombre(self, obj):
        if obj.empleado:
            return f"{obj.empleado.nombre} {obj.empleado.apellido_paterno}"
        return None

    def get_empleado_puesto(self, obj):
        if obj.empleado:
            return obj.empleado.puesto
        return None

    def get_empresa_nombre(self, obj):
        if obj.empleado and obj.empleado.empresa:
            return obj.empleado.empresa.nombre_comercial or obj.empleado.empresa.razon_social
        return None

    def get_aprobador_nombre(self, obj):
        if obj.aprobado_por:
            return obj.aprobado_por.nombre
        return None

    def get_puede_aprobar(self, obj):
        request = self.context.get('request')
        if not request or not request.user:
            return False

        user = request.user

        # Admin y RRHH pueden aprobar todo
        if user.rol in ['admin', 'administrador', 'rrhh', 'empleador']:
            return True

        # Jefe directo puede aprobar
        if obj.empleado and obj.empleado.jefe_directo:
            if hasattr(user, 'empleado') and user.empleado:
                return str(user.empleado.id) == str(obj.empleado.jefe_directo_id)

        return False


class SolicitudVacacionesListSerializer(serializers.ModelSerializer):
    """Serializer ligero para listados"""
    empleado_nombre = serializers.SerializerMethodField()
    empleado_puesto = serializers.SerializerMethodField()
    empresa_nombre = serializers.SerializerMethodField()
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    puede_aprobar = serializers.SerializerMethodField()

    class Meta:
        model = SolicitudVacaciones
        fields = [
            'id', 'empleado', 'empleado_nombre', 'empleado_puesto', 'empresa_nombre',
            'fecha_inicio', 'fecha_fin', 'dias_solicitados',
            'estado', 'estado_display', 'puede_aprobar',
            'created_at',
        ]

    def get_empleado_nombre(self, obj):
        if obj.empleado:
            return f"{obj.empleado.nombre} {obj.empleado.apellido_paterno}"
        return None

    def get_empleado_puesto(self, obj):
        if obj.empleado:
            return obj.empleado.puesto
        return None

    def get_empresa_nombre(self, obj):
        if obj.empleado and obj.empleado.empresa:
            return obj.empleado.empresa.nombre_comercial or obj.empleado.empresa.razon_social
        return None

    def get_puede_aprobar(self, obj):
        request = self.context.get('request')
        if not request or not request.user:
            return False

        user = request.user
        if user.rol in ['admin', 'administrador', 'rrhh', 'empleador']:
            return True

        if obj.empleado and obj.empleado.jefe_directo:
            if hasattr(user, 'empleado') and user.empleado:
                return str(user.empleado.id) == str(obj.empleado.jefe_directo_id)

        return False


class SolicitudVacacionesViewSet(viewsets.ModelViewSet):
    queryset = SolicitudVacaciones.objects.select_related(
        'empleado', 'empleado__empresa', 'periodo_vacacional', 'aprobado_por'
    )
    filterset_fields = ['empleado', 'estado', 'empleado__empresa']
    ordering_fields = ['fecha_inicio', 'created_at']
    search_fields = ['empleado__nombre', 'empleado__apellido_paterno']

    def get_serializer_class(self):
        if self.action == 'list':
            return SolicitudVacacionesListSerializer
        return SolicitudVacacionesSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset()
        empresa_id = self.request.headers.get('X-Empresa-ID')

        if empresa_id:
            qs = qs.filter(empleado__empresa_id=empresa_id)
        elif user.rol not in ['admin', 'administrador']:
            if hasattr(user, 'empresas'):
                qs = qs.filter(empleado__empresa__in=user.empresas.all())

        # Filtro por estado
        estado = self.request.query_params.get('estado')
        if estado:
            qs = qs.filter(estado=estado)

        # Filtro por empleado
        empleado_id = self.request.query_params.get('empleado')
        if empleado_id:
            qs = qs.filter(empleado_id=empleado_id)

        # Si es empleado normal, solo ver sus propias solicitudes y las de sus subordinados
        if user.rol == 'empleado':
            if hasattr(user, 'empleado') and user.empleado:
                subordinados = Empleado.objects.filter(jefe_directo=user.empleado)
                qs = qs.filter(
                    Q(empleado=user.empleado) | Q(empleado__in=subordinados)
                )
            else:
                qs = qs.none()

        return qs.order_by('-created_at')

    def perform_create(self, serializer):
        # Calcular días si no vienen
        fecha_inicio = serializer.validated_data.get('fecha_inicio')
        fecha_fin = serializer.validated_data.get('fecha_fin')
        dias = serializer.validated_data.get('dias_solicitados')

        if not dias and fecha_inicio and fecha_fin:
            dias = (fecha_fin - fecha_inicio).days + 1
            serializer.validated_data['dias_solicitados'] = dias

        # Si no viene empleado, usar el del usuario actual
        empleado = serializer.validated_data.get('empleado')
        if not empleado and hasattr(self.request.user, 'empleado') and self.request.user.empleado:
            serializer.save(empleado=self.request.user.empleado, created_by=self.request.user)
        else:
            serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'])
    def aprobar(self, request, pk=None):
        """Aprobar una solicitud de vacaciones"""
        solicitud = self.get_object()

        if solicitud.estado != SolicitudVacaciones.Estado.PENDIENTE:
            return Response(
                {'error': 'Solo se pueden aprobar solicitudes pendientes'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Verificar permisos
        user = request.user
        puede_aprobar = False

        if user.rol in ['admin', 'administrador', 'rrhh', 'empleador']:
            puede_aprobar = True
        elif solicitud.empleado.jefe_directo:
            if hasattr(user, 'empleado') and user.empleado:
                puede_aprobar = str(user.empleado.id) == str(solicitud.empleado.jefe_directo_id)

        if not puede_aprobar:
            return Response(
                {'error': 'No tienes permisos para aprobar esta solicitud'},
                status=status.HTTP_403_FORBIDDEN
            )

        solicitud.estado = SolicitudVacaciones.Estado.APROBADA
        solicitud.aprobado_por = user
        solicitud.fecha_aprobacion = timezone.now()
        solicitud.comentarios = request.data.get('comentarios', '')
        solicitud.save()

        # Actualizar días tomados en el periodo
        if solicitud.periodo_vacacional:
            periodo = solicitud.periodo_vacacional
            periodo.dias_tomados += solicitud.dias_solicitados
            periodo.save()

        return Response(SolicitudVacacionesSerializer(solicitud, context={'request': request}).data)

    @action(detail=True, methods=['post'])
    def rechazar(self, request, pk=None):
        """Rechazar una solicitud de vacaciones"""
        solicitud = self.get_object()

        if solicitud.estado != SolicitudVacaciones.Estado.PENDIENTE:
            return Response(
                {'error': 'Solo se pueden rechazar solicitudes pendientes'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Verificar permisos
        user = request.user
        puede_rechazar = False

        if user.rol in ['admin', 'administrador', 'rrhh', 'empleador']:
            puede_rechazar = True
        elif solicitud.empleado.jefe_directo:
            if hasattr(user, 'empleado') and user.empleado:
                puede_rechazar = str(user.empleado.id) == str(solicitud.empleado.jefe_directo_id)

        if not puede_rechazar:
            return Response(
                {'error': 'No tienes permisos para rechazar esta solicitud'},
                status=status.HTTP_403_FORBIDDEN
            )

        motivo = request.data.get('motivo', '')
        if not motivo:
            return Response(
                {'error': 'Debe proporcionar un motivo de rechazo'},
                status=status.HTTP_400_BAD_REQUEST
            )

        solicitud.estado = SolicitudVacaciones.Estado.RECHAZADA
        solicitud.aprobado_por = user
        solicitud.fecha_aprobacion = timezone.now()
        solicitud.comentarios = motivo
        solicitud.save()

        return Response(SolicitudVacacionesSerializer(solicitud, context={'request': request}).data)

    @action(detail=True, methods=['post'])
    def cancelar(self, request, pk=None):
        """Cancelar una solicitud (solo el empleado o admin)"""
        solicitud = self.get_object()

        if solicitud.estado not in ['pendiente', 'aprobada']:
            return Response(
                {'error': 'No se puede cancelar esta solicitud'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = request.user
        es_propietario = hasattr(user, 'empleado') and user.empleado and str(user.empleado.id) == str(solicitud.empleado.id)
        es_admin = user.rol in ['admin', 'administrador', 'rrhh']

        if not es_propietario and not es_admin:
            return Response(
                {'error': 'No tienes permisos para cancelar esta solicitud'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Si estaba aprobada, restaurar saldo
        if solicitud.estado == 'aprobada' and solicitud.periodo_vacacional:
            periodo = solicitud.periodo_vacacional
            periodo.dias_tomados = max(0, periodo.dias_tomados - solicitud.dias_solicitados)
            periodo.save()

        solicitud.estado = SolicitudVacaciones.Estado.CANCELADA
        solicitud.save()

        return Response(SolicitudVacacionesSerializer(solicitud, context={'request': request}).data)

    @action(detail=False, methods=['get'])
    def resumen(self, request):
        """Obtener resumen de vacaciones de un empleado"""
        empleado_id = request.query_params.get('empleado')

        if not empleado_id:
            # Si no se especifica, usar el del usuario actual
            if hasattr(request.user, 'empleado') and request.user.empleado:
                empleado_id = request.user.empleado.id
            else:
                return Response({'error': 'Debe especificar un empleado'}, status=400)

        try:
            empleado = Empleado.objects.get(id=empleado_id)
        except Empleado.DoesNotExist:
            return Response({'error': 'Empleado no encontrado'}, status=404)

        # Calcular antigüedad y días correspondientes
        antiguedad = calcular_antiguedad_anios(empleado.fecha_ingreso)
        dias_correspondientes = calcular_dias_vacaciones_lft(antiguedad)

        # Días tomados en el año actual
        hoy = date.today()
        inicio_anio = date(hoy.year, 1, 1)
        fin_anio = date(hoy.year, 12, 31)

        dias_tomados = SolicitudVacaciones.objects.filter(
            empleado=empleado,
            estado='aprobada',
            fecha_inicio__gte=inicio_anio,
            fecha_fin__lte=fin_anio
        ).aggregate(total=Sum('dias_solicitados'))['total'] or 0

        # Solicitudes pendientes
        solicitudes_pendientes = SolicitudVacaciones.objects.filter(
            empleado=empleado,
            estado='pendiente'
        ).count()

        # Días de años anteriores (periodos con días pendientes)
        dias_anteriores = PeriodoVacacional.objects.filter(
            empleado=empleado,
        ).exclude(
            numero_periodo=antiguedad
        ).aggregate(
            total=Sum('dias_derecho') - Sum('dias_tomados')
        )
        dias_pendientes_anteriores = max(0, dias_anteriores.get('total') or 0)

        resumen = {
            'empleado_id': str(empleado.id),
            'empleado_nombre': f"{empleado.nombre} {empleado.apellido_paterno}",
            'fecha_ingreso': empleado.fecha_ingreso,
            'antiguedad_anios': antiguedad,
            'dias_correspondientes_anio_actual': dias_correspondientes,
            'dias_tomados_anio_actual': dias_tomados,
            'dias_disponibles': max(0, dias_correspondientes - dias_tomados),
            'dias_pendientes_anteriores': dias_pendientes_anteriores,
            'total_disponible': max(0, (dias_correspondientes - dias_tomados) + dias_pendientes_anteriores),
            'solicitudes_pendientes': solicitudes_pendientes,
        }

        return Response(resumen)

    @action(detail=False, methods=['get'])
    def estadisticas(self, request):
        """Estadísticas generales de vacaciones"""
        qs = self.get_queryset()

        pendientes = qs.filter(estado='pendiente').count()
        aprobadas = qs.filter(estado='aprobada').count()
        rechazadas = qs.filter(estado='rechazada').count()

        # Por vencer (vacaciones que inician en los próximos 7 días)
        hoy = date.today()
        from datetime import timedelta
        proximas = qs.filter(
            estado='aprobada',
            fecha_inicio__gte=hoy,
            fecha_inicio__lte=hoy + timedelta(days=7)
        ).count()

        return Response({
            'pendientes': pendientes,
            'aprobadas': aprobadas,
            'rechazadas': rechazadas,
            'proximas_7_dias': proximas,
        })


class PeriodoVacacionalViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PeriodoVacacional.objects.select_related('empleado')
    serializer_class = PeriodoVacacionalSerializer
    filterset_fields = ['empleado']

    def get_queryset(self):
        qs = super().get_queryset()
        empleado_id = self.request.query_params.get('empleado')
        if empleado_id:
            qs = qs.filter(empleado_id=empleado_id)
        return qs.order_by('-numero_periodo')
