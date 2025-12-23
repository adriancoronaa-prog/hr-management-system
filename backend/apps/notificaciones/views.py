"""
Views para el sistema de notificaciones
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import serializers
from .models import Notificacion


class NotificacionSerializer(serializers.ModelSerializer):
    """Serializer para notificaciones"""
    leida = serializers.SerializerMethodField()
    url_destino = serializers.SerializerMethodField()

    class Meta:
        model = Notificacion
        fields = [
            'id', 'tipo', 'prioridad', 'titulo', 'mensaje',
            'estado', 'leida', 'url_destino', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

    def get_leida(self, obj):
        """Convierte estado a booleano para el frontend"""
        return obj.estado == 'leida'

    def get_url_destino(self, obj):
        """Extrae url_destino de datos_extra si existe"""
        return obj.datos_extra.get('url') if obj.datos_extra else None


class NotificacionViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para notificaciones del usuario"""
    serializer_class = NotificacionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notificacion.objects.filter(
            destinatario=self.request.user
        ).order_by('-created_at')

    @action(detail=False, methods=['get'])
    def no_leidas(self, request):
        """Contador de notificaciones no leidas"""
        count = self.get_queryset().exclude(estado='leida').count()
        return Response({'count': count})

    @action(detail=False, methods=['get'])
    def recientes(self, request):
        """Ultimas 10 notificaciones"""
        qs = self.get_queryset()[:10]
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def marcar_leida(self, request, pk=None):
        """Marca notificacion como leida"""
        notificacion = self.get_object()
        notificacion.marcar_leida()
        return Response({'success': True})

    @action(detail=False, methods=['post'])
    def marcar_todas_leidas(self, request):
        """Marca todas como leidas"""
        from django.utils import timezone
        self.get_queryset().exclude(estado='leida').update(
            estado='leida',
            fecha_lectura=timezone.now()
        )
        return Response({'success': True})
