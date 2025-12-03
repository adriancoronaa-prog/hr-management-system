from django.db import models
from apps.core.models import BaseModel


class Conversacion(BaseModel):
    """
    Conversación de chat con el asistente IA
    """
    usuario = models.ForeignKey(
        'usuarios.Usuario',
        on_delete=models.CASCADE,
        related_name='conversaciones'
    )
    titulo = models.CharField(max_length=200, blank=True)
    
    # Contexto de la conversación
    empresa_contexto = models.ForeignKey(
        'empresas.Empresa',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='conversaciones'
    )
    empleado_contexto = models.ForeignKey(
        'empleados.Empleado',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='conversaciones'
    )
    
    activa = models.BooleanField(default=True)

    # Flujo guiado activo
    flujo_activo = models.CharField(max_length=50, blank=True)
    datos_flujo = models.JSONField(default=dict, blank=True)
    paso_actual = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'chat_conversaciones'
        verbose_name = 'Conversación'
        verbose_name_plural = 'Conversaciones'
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"{self.usuario.email} - {self.titulo or 'Sin título'}"


class Mensaje(BaseModel):
    """
    Mensaje individual en una conversación
    """
    class Rol(models.TextChoices):
        USUARIO = 'user', 'Usuario'
        ASISTENTE = 'assistant', 'Asistente'
        SISTEMA = 'system', 'Sistema'
    
    class TipoAccion(models.TextChoices):
        NINGUNA = 'ninguna', 'Ninguna'
        CREAR = 'crear', 'Crear'
        LEER = 'leer', 'Leer'
        ACTUALIZAR = 'actualizar', 'Actualizar'
        ELIMINAR = 'eliminar', 'Eliminar'
        CALCULAR = 'calcular', 'Calcular'
        GENERAR = 'generar', 'Generar documento'
    
    conversacion = models.ForeignKey(
        Conversacion,
        on_delete=models.CASCADE,
        related_name='mensajes'
    )
    rol = models.CharField(max_length=20, choices=Rol.choices)
    contenido = models.TextField()
    
    # Si el mensaje ejecutó una acción
    accion_ejecutada = models.CharField(
        max_length=20, 
        choices=TipoAccion.choices, 
        default=TipoAccion.NINGUNA
    )
    entidad_afectada = models.CharField(max_length=50, blank=True)  # empresa, empleado, etc.
    id_entidad = models.IntegerField(null=True, blank=True)
    resultado_accion = models.JSONField(null=True, blank=True)
    
    # Archivos adjuntos (PDFs, imágenes)
    archivo_adjunto = models.FileField(
        upload_to='chat/adjuntos/%Y/%m/',
        null=True,
        blank=True
    )
    archivo_nombre = models.CharField(max_length=255, blank=True)
    tipo_archivo = models.CharField(max_length=50, blank=True)
    archivo_contenido_texto = models.TextField(blank=True)  # Texto extraído para IA
    datos_extraidos = models.JSONField(null=True, blank=True)  # Datos extraídos del PDF
    
    # Métricas
    tokens_entrada = models.IntegerField(default=0)
    tokens_salida = models.IntegerField(default=0)
    tiempo_respuesta_ms = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'chat_mensajes'
        verbose_name = 'Mensaje'
        verbose_name_plural = 'Mensajes'
        ordering = ['created_at']
    
    def __str__(self):
        preview = self.contenido[:50] + '...' if len(self.contenido) > 50 else self.contenido
        return f"{self.get_rol_display()}: {preview}"


class ComandoIA(BaseModel):
    """
    Registro de comandos que el IA puede ejecutar
    Para auditoría y aprendizaje
    """
    class Estado(models.TextChoices):
        PENDIENTE = 'pendiente', 'Pendiente'
        EJECUTADO = 'ejecutado', 'Ejecutado'
        ERROR = 'error', 'Error'
        CANCELADO = 'cancelado', 'Cancelado'
    
    mensaje = models.ForeignKey(
        Mensaje,
        on_delete=models.CASCADE,
        related_name='comandos'
    )
    
    # Qué se pidió
    intencion = models.CharField(max_length=100)  # crear_empleado, calcular_nomina, etc.
    parametros = models.JSONField(default=dict)
    
    # Qué se ejecutó
    endpoint_api = models.CharField(max_length=200, blank=True)
    metodo_http = models.CharField(max_length=10, blank=True)
    payload = models.JSONField(null=True, blank=True)
    
    # Resultado
    estado = models.CharField(max_length=20, choices=Estado.choices, default=Estado.PENDIENTE)
    respuesta = models.JSONField(null=True, blank=True)
    error = models.TextField(blank=True)
    
    class Meta:
        db_table = 'chat_comandos'
        verbose_name = 'Comando IA'
        verbose_name_plural = 'Comandos IA'
        ordering = ['-created_at']


class ConfiguracionIA(BaseModel):
    """
    Configuración del asistente IA por empresa o global
    """
    empresa = models.OneToOneField(
        'empresas.Empresa',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='config_ia'
    )
    
    # Configuración del modelo
    modelo = models.CharField(max_length=50, default='claude-sonnet-4-20250514')
    temperatura = models.FloatField(default=0.3)
    max_tokens = models.IntegerField(default=4096)
    
    # Personalización
    nombre_asistente = models.CharField(max_length=50, default='Asistente RRHH')
    instrucciones_personalizadas = models.TextField(blank=True)
    
    # Límites
    mensajes_por_dia_empleado = models.IntegerField(default=50)
    mensajes_por_dia_empleador = models.IntegerField(default=500)
    
    # Features habilitadas
    puede_crear_entidades = models.BooleanField(default=True)
    puede_modificar_entidades = models.BooleanField(default=True)
    puede_eliminar_entidades = models.BooleanField(default=False)
    puede_procesar_nomina = models.BooleanField(default=True)
    puede_leer_documentos = models.BooleanField(default=True)
    puede_generar_documentos = models.BooleanField(default=True)
    
    activo = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'chat_configuracion'
        verbose_name = 'Configuración IA'
        verbose_name_plural = 'Configuraciones IA'
    
    def __str__(self):
        if self.empresa:
            return f"Config IA - {self.empresa}"
        return "Config IA - Global"
