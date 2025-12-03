"""
Vistas para el Chat con IA
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.shortcuts import get_object_or_404

from .models import Conversacion, Mensaje
from .services import AsistenteRRHH
from .serializers import (
    ConversacionSerializer,
    MensajeSerializer,
    EnviarMensajeSerializer
)


class ConversacionViewSet(viewsets.ModelViewSet):
    """ViewSet para conversaciones"""
    serializer_class = ConversacionSerializer
    permission_classes = [AllowAny]  # Temporal para pruebas
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Conversacion.objects.filter(usuario=self.request.user)
        return Conversacion.objects.none()
    
    @action(detail=True, methods=['post'])
    def enviar_mensaje(self, request, pk=None):
        """Envía un mensaje a la conversación (con soporte para archivos)"""
        conversacion = self.get_object()

        # Obtener mensaje del body
        mensaje = request.data.get('mensaje', '')

        # Obtener archivo si existe
        archivo = request.FILES.get('archivo')

        if not mensaje and not archivo:
            return Response(
                {'error': 'Debes enviar un mensaje o un archivo'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Obtener empresa en contexto
        empresa_contexto = conversacion.empresa_contexto

        # Procesar con el asistente
        asistente = AsistenteRRHH(request.user, empresa_contexto)
        resultado = asistente.procesar_mensaje(
            mensaje=mensaje,
            conversacion_id=conversacion.id,
            archivo=archivo
        )

        return Response(resultado)
    
    @action(detail=True, methods=['post'])
    def confirmar_accion(self, request, pk=None):
        """Confirma una acción pendiente"""
        conversacion = self.get_object()
        
        accion = request.data.get('accion')
        if not accion:
            return Response(
                {'error': 'Debes enviar la acción a confirmar'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        asistente = AsistenteRRHH(request.user, conversacion.empresa_contexto)
        resultado = asistente.confirmar_accion(conversacion.id, accion)
        
        return Response(resultado)
    
    @action(detail=True, methods=['post'])
    def cancelar_accion(self, request, pk=None):
        """Cancela una acción pendiente"""
        conversacion = self.get_object()
        
        asistente = AsistenteRRHH(request.user, conversacion.empresa_contexto)
        resultado = asistente.cancelar_accion(conversacion.id)
        
        return Response(resultado)


class ChatView(APIView):
    """
    Vista simple para el chat con soporte para archivos
    POST /api/chat/mensaje/

    Puede enviarse como JSON o como multipart/form-data (para archivos)
    """
    permission_classes = [AllowAny]  # Temporal para pruebas
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def post(self, request):
        mensaje = request.data.get('mensaje', '')
        conversacion_id = request.data.get('conversacion_id')
        empresa_id = request.data.get('empresa_id')
        empleado_id = request.data.get('empleado_id')  # Para contexto de expediente

        # Obtener archivo si existe
        archivo = request.FILES.get('archivo')

        if not mensaje and not archivo:
            return Response(
                {'error': 'Debes enviar un mensaje o un archivo'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Obtener empresa si se especifica
        empresa_contexto = None
        if empresa_id:
            from apps.empresas.models import Empresa
            try:
                empresa_contexto = Empresa.objects.get(pk=empresa_id)
            except Empresa.DoesNotExist:
                pass

        # Crear usuario anónimo temporal si no está autenticado
        if not request.user.is_authenticated:
            from apps.usuarios.models import Usuario
            usuario = Usuario.objects.first()  # Temporal para pruebas
        else:
            usuario = request.user

        asistente = AsistenteRRHH(usuario, empresa_contexto)

        # Establecer empleado en contexto si se especifica
        if empleado_id and conversacion_id:
            asistente.establecer_empleado_contexto(conversacion_id, empleado_id)

        resultado = asistente.procesar_mensaje(
            mensaje=mensaje,
            conversacion_id=conversacion_id,
            archivo=archivo
        )

        return Response(resultado)


class DocumentoProcesadoViewSet(viewsets.ViewSet):
    """ViewSet placeholder para documentos procesados"""
    permission_classes = [AllowAny]
    
    def list(self, request):
        return Response({'mensaje': 'Procesamiento de documentos pendiente'})