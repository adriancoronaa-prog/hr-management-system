"""
Serializers para el Chat con IA
"""
from rest_framework import serializers
from .models import Conversacion, Mensaje


class MensajeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mensaje
        fields = [
            'id', 'rol', 'contenido', 'accion_ejecutada', 
            'resultado_accion', 'tiempo_respuesta_ms', 'created_at'
        ]
        read_only_fields = fields


class ConversacionSerializer(serializers.ModelSerializer):
    mensajes = MensajeSerializer(many=True, read_only=True)
    
    class Meta:
        model = Conversacion
        fields = [
            'id', 'titulo', 'empresa_contexto', 'activa',
            'created_at', 'updated_at', 'mensajes'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class EnviarMensajeSerializer(serializers.Serializer):
    mensaje = serializers.CharField(max_length=10000)
    archivo = serializers.FileField(required=False, allow_null=True)