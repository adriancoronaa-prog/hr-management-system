"""
Módulo de Integraciones Externas
Arquitectura preparada para:
- PAC para timbrado CFDI
- IMSS/SUA
- Bancos (dispersión SPEI)
- SAT (validación RFC)
"""
from django.db import models
from django.core.validators import MinValueValidator
from apps.core.models import BaseModel


class ProveedorIntegracion(BaseModel):
    """
    Proveedores de servicios externos
    """
    class TipoProveedor(models.TextChoices):
        PAC = 'pac', 'PAC (Timbrado CFDI)'
        BANCO = 'banco', 'Banco (Dispersión)'
        IMSS = 'imss', 'IMSS/SUA'
        SAT = 'sat', 'SAT'
        ALMACENAMIENTO = 'storage', 'Almacenamiento'
        EMAIL = 'email', 'Email'
        SMS = 'sms', 'SMS'
        IA = 'ia', 'Inteligencia Artificial'
    
    nombre = models.CharField(max_length=100)
    tipo = models.CharField(max_length=20, choices=TipoProveedor.choices)
    descripcion = models.TextField(blank=True)
    
    # Configuración de conexión
    api_url_produccion = models.URLField(blank=True)
    api_url_sandbox = models.URLField(blank=True)
    
    # Documentación
    url_documentacion = models.URLField(blank=True)
    
    activo = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'integraciones_proveedor'
        verbose_name = 'Proveedor de Integración'
        verbose_name_plural = 'Proveedores de Integración'
    
    def __str__(self):
        return f"{self.nombre} ({self.get_tipo_display()})"


class ConfiguracionIntegracion(BaseModel):
    """
    Configuración de integración por empresa
    Cada empresa puede tener su propio PAC, banco, etc.
    """
    empresa = models.ForeignKey(
        'empresas.Empresa',
        on_delete=models.CASCADE,
        related_name='integraciones'
    )
    proveedor = models.ForeignKey(
        ProveedorIntegracion,
        on_delete=models.PROTECT,
        related_name='configuraciones'
    )
    
    # Credenciales (encriptadas en producción)
    api_key = models.CharField(max_length=500, blank=True)
    api_secret = models.CharField(max_length=500, blank=True)
    usuario = models.CharField(max_length=200, blank=True)
    password = models.CharField(max_length=500, blank=True)
    
    # Certificados para CFDI
    certificado_cer = models.FileField(upload_to='certificados/', blank=True, null=True)
    certificado_key = models.FileField(upload_to='certificados/', blank=True, null=True)
    password_key = models.CharField(max_length=200, blank=True)
    
    # Modo de operación
    modo_sandbox = models.BooleanField(
        default=True,
        help_text='True = ambiente de pruebas, False = producción'
    )
    
    # Configuraciones adicionales en JSON
    configuracion_extra = models.JSONField(default=dict, blank=True)
    
    activo = models.BooleanField(default=True)
    
    # Última verificación de conexión
    ultima_verificacion = models.DateTimeField(null=True, blank=True)
    estado_conexion = models.CharField(
        max_length=20,
        choices=[
            ('no_verificado', 'No Verificado'),
            ('conectado', 'Conectado'),
            ('error', 'Error de Conexión'),
        ],
        default='no_verificado'
    )
    ultimo_error = models.TextField(blank=True)
    
    class Meta:
        db_table = 'integraciones_configuracion'
        verbose_name = 'Configuración de Integración'
        verbose_name_plural = 'Configuraciones de Integración'
        unique_together = ['empresa', 'proveedor']
    
    def __str__(self):
        return f"{self.empresa} - {self.proveedor}"


class LogIntegracion(BaseModel):
    """
    Log de llamadas a APIs externas
    """
    class Estado(models.TextChoices):
        PENDIENTE = 'pendiente', 'Pendiente'
        EN_PROCESO = 'en_proceso', 'En Proceso'
        EXITOSO = 'exitoso', 'Exitoso'
        ERROR = 'error', 'Error'
        REINTENTANDO = 'reintentando', 'Reintentando'
    
    configuracion = models.ForeignKey(
        ConfiguracionIntegracion,
        on_delete=models.CASCADE,
        related_name='logs'
    )
    
    # Tipo de operación
    operacion = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=500, blank=True)
    
    # Request/Response
    request_url = models.URLField(blank=True)
    request_method = models.CharField(max_length=10, default='POST')
    request_headers = models.JSONField(default=dict, blank=True)
    request_body = models.TextField(blank=True)
    
    response_status = models.IntegerField(null=True, blank=True)
    response_headers = models.JSONField(default=dict, blank=True)
    response_body = models.TextField(blank=True)
    
    # Estado
    estado = models.CharField(max_length=20, choices=Estado.choices, default=Estado.PENDIENTE)
    mensaje_error = models.TextField(blank=True)
    
    # Tiempo
    tiempo_respuesta_ms = models.IntegerField(null=True, blank=True)
    intentos = models.IntegerField(default=1)
    
    # Referencias
    referencia_tipo = models.CharField(max_length=50, blank=True)  # ej: 'recibo_nomina'
    referencia_id = models.IntegerField(null=True, blank=True)
    
    class Meta:
        db_table = 'integraciones_log'
        verbose_name = 'Log de Integración'
        verbose_name_plural = 'Logs de Integración'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.operacion} - {self.estado} ({self.created_at})"


class WebhookEntrada(BaseModel):
    """
    Webhooks recibidos de servicios externos
    """
    proveedor = models.ForeignKey(
        ProveedorIntegracion,
        on_delete=models.SET_NULL,
        null=True,
        related_name='webhooks'
    )
    
    # Datos del webhook
    evento = models.CharField(max_length=100)
    payload = models.JSONField(default=dict)
    headers = models.JSONField(default=dict)
    
    # Validación
    firma_valida = models.BooleanField(null=True, blank=True)
    
    # Procesamiento
    procesado = models.BooleanField(default=False)
    fecha_procesado = models.DateTimeField(null=True, blank=True)
    resultado_procesamiento = models.JSONField(default=dict, blank=True)
    
    class Meta:
        db_table = 'integraciones_webhook'
        verbose_name = 'Webhook Entrada'
        verbose_name_plural = 'Webhooks Entrada'
        ordering = ['-created_at']


# ============ MODELOS ESPECÍFICOS POR INTEGRACIÓN ============

class ConfiguracionPAC(BaseModel):
    """
    Configuración específica para PAC de timbrado
    """
    configuracion = models.OneToOneField(
        ConfiguracionIntegracion,
        on_delete=models.CASCADE,
        related_name='config_pac'
    )
    
    # Datos fiscales de la empresa
    rfc_emisor = models.CharField(max_length=13)
    regimen_fiscal = models.CharField(max_length=3)
    lugar_expedicion = models.CharField(max_length=5, help_text='Código postal')
    
    # Serie y folio para CFDI
    serie_nomina = models.CharField(max_length=25, default='N')
    folio_actual = models.IntegerField(default=1)
    
    # Opciones
    generar_pdf = models.BooleanField(default=True)
    enviar_email_empleado = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'integraciones_config_pac'
        verbose_name = 'Configuración PAC'


class ConfiguracionBanco(BaseModel):
    """
    Configuración para dispersión bancaria
    """
    configuracion = models.OneToOneField(
        ConfiguracionIntegracion,
        on_delete=models.CASCADE,
        related_name='config_banco'
    )
    
    # Cuenta de la empresa
    cuenta_origen = models.CharField(max_length=20)
    clabe_origen = models.CharField(max_length=18)
    
    # Formato de layout
    formato_layout = models.CharField(
        max_length=50,
        choices=[
            ('spei', 'SPEI Estándar'),
            ('banamex', 'Banamex'),
            ('bancomer', 'BBVA'),
            ('santander', 'Santander'),
            ('banorte', 'Banorte'),
            ('hsbc', 'HSBC'),
        ],
        default='spei'
    )
    
    # Configuración de archivos
    directorio_layouts = models.CharField(max_length=500, blank=True)
    
    class Meta:
        db_table = 'integraciones_config_banco'
        verbose_name = 'Configuración Banco'


class ArchivoDispersion(BaseModel):
    """
    Archivos de dispersión bancaria generados
    """
    class Estado(models.TextChoices):
        GENERADO = 'generado', 'Generado'
        ENVIADO = 'enviado', 'Enviado al Banco'
        PROCESANDO = 'procesando', 'Procesando'
        COMPLETADO = 'completado', 'Completado'
        PARCIAL = 'parcial', 'Parcialmente Aplicado'
        RECHAZADO = 'rechazado', 'Rechazado'

    config_banco = models.ForeignKey(
        ConfiguracionBanco,
        on_delete=models.CASCADE,
        related_name='archivos'
    )

    periodo_nomina = models.ForeignKey(
        'nomina.PeriodoNomina',
        on_delete=models.CASCADE,
        related_name='archivos_dispersion'
    )

    # Archivo
    archivo = models.FileField(upload_to='dispersion/')
    nombre_archivo = models.CharField(max_length=255)

    # Totales
    total_registros = models.IntegerField(default=0)
    total_importe = models.DecimalField(max_digits=14, decimal_places=2, default=0)

    # Estado
    estado = models.CharField(max_length=20, choices=Estado.choices, default=Estado.GENERADO)

    # Respuesta del banco
    referencia_banco = models.CharField(max_length=100, blank=True)
    fecha_aplicacion = models.DateTimeField(null=True, blank=True)
    registros_aplicados = models.IntegerField(default=0)
    registros_rechazados = models.IntegerField(default=0)

    class Meta:
        db_table = 'integraciones_archivo_dispersion'
        verbose_name = 'Archivo de Dispersión'
        verbose_name_plural = 'Archivos de Dispersión'


# ============ GOOGLE CALENDAR ============

class ConfiguracionGoogleCalendar(BaseModel):
    """Configuracion de Google Calendar por empresa"""

    empresa = models.OneToOneField(
        'empresas.Empresa',
        on_delete=models.CASCADE,
        related_name='config_google_calendar'
    )

    # Credenciales OAuth
    credentials_json = models.TextField(blank=True, help_text='Credenciales OAuth JSON')
    refresh_token = models.TextField(blank=True)

    # Configuracion
    calendar_id = models.CharField(
        max_length=255,
        blank=True,
        default='primary',
        help_text='ID del calendario (default: primary)'
    )
    sincronizar_vacaciones = models.BooleanField(default=True)
    sincronizar_cumpleanos = models.BooleanField(default=True)
    sincronizar_aniversarios = models.BooleanField(default=True)
    sincronizar_incapacidades = models.BooleanField(default=False)

    # Estado
    activo = models.BooleanField(default=False)
    ultima_sincronizacion = models.DateTimeField(null=True, blank=True)
    error_ultimo = models.TextField(blank=True)

    class Meta:
        db_table = 'integraciones_google_calendar'
        verbose_name = 'Configuracion Google Calendar'
        verbose_name_plural = 'Configuraciones Google Calendar'

    def __str__(self):
        return f"Google Calendar - {self.empresa.nombre_comercial}"


class EventoSincronizado(BaseModel):
    """Registro de eventos sincronizados con Google Calendar"""

    class TipoEvento(models.TextChoices):
        VACACIONES = 'vacaciones', 'Vacaciones'
        CUMPLEANOS = 'cumpleanos', 'Cumpleanos'
        ANIVERSARIO = 'aniversario', 'Aniversario Laboral'
        INCAPACIDAD = 'incapacidad', 'Incapacidad'
        OTRO = 'otro', 'Otro'

    empresa = models.ForeignKey(
        'empresas.Empresa',
        on_delete=models.CASCADE,
        related_name='eventos_sincronizados'
    )
    empleado = models.ForeignKey(
        'empleados.Empleado',
        on_delete=models.CASCADE,
        related_name='eventos_calendario',
        null=True,
        blank=True
    )

    tipo = models.CharField(max_length=20, choices=TipoEvento.choices)
    titulo = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True)

    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    todo_el_dia = models.BooleanField(default=True)

    # Referencia en Google Calendar
    google_event_id = models.CharField(max_length=255, blank=True)
    google_calendar_id = models.CharField(max_length=255, blank=True)

    # Estado
    sincronizado = models.BooleanField(default=False)
    fecha_sincronizacion = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'integraciones_eventos_sincronizados'
        verbose_name = 'Evento Sincronizado'
        verbose_name_plural = 'Eventos Sincronizados'
        ordering = ['-fecha_inicio']

    def __str__(self):
        return f"{self.titulo} ({self.fecha_inicio})"


# ============ AUDITORIA ============

class RegistroAuditoria(models.Model):
    """Registro de cambios en el sistema para auditoria"""

    class Accion(models.TextChoices):
        CREAR = 'crear', 'Crear'
        MODIFICAR = 'modificar', 'Modificar'
        ELIMINAR = 'eliminar', 'Eliminar'
        CONSULTAR = 'consultar', 'Consultar'
        LOGIN = 'login', 'Inicio de Sesion'
        LOGOUT = 'logout', 'Cierre de Sesion'
        EXPORTAR = 'exportar', 'Exportar'
        APROBAR = 'aprobar', 'Aprobar'
        RECHAZAR = 'rechazar', 'Rechazar'

    # Quien hizo el cambio
    usuario = models.ForeignKey(
        'usuarios.Usuario',
        on_delete=models.SET_NULL,
        null=True,
        related_name='registros_auditoria'
    )

    # Que se modifico (relacion generica)
    content_type = models.ForeignKey(
        'contenttypes.ContentType',
        on_delete=models.SET_NULL,
        null=True
    )
    object_id = models.CharField(max_length=50, blank=True)

    # Detalles
    accion = models.CharField(max_length=20, choices=Accion.choices)
    descripcion = models.TextField()
    modelo = models.CharField(max_length=100, blank=True)

    # Valores antes/despues
    datos_anteriores = models.JSONField(null=True, blank=True)
    datos_nuevos = models.JSONField(null=True, blank=True)

    # Metadatos
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)

    # Timestamp
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'auditoria_registros'
        verbose_name = 'Registro de Auditoria'
        verbose_name_plural = 'Registros de Auditoria'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['usuario', '-created_at']),
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['accion', '-created_at']),
        ]

    def __str__(self):
        return f"{self.usuario} - {self.accion} - {self.created_at}"
