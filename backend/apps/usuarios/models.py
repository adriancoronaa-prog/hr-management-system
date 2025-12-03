from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from datetime import timedelta
import secrets

from apps.core.models import BaseModel


class Usuario(AbstractUser, BaseModel):
    """
    Usuario del sistema con 3 niveles de acceso:
    - admin: Acceso total al sistema (el dueño)
    - empleador: RRHH que maneja empleados de sus empresas asignadas
    - empleado: Solo ve su propia información
    """
    
    class Rol(models.TextChoices):
        ADMIN = 'admin', 'Administrador'
        EMPLEADOR = 'empleador', 'Empleador/RRHH'
        EMPLEADO = 'empleado', 'Empleado'
    
    email = models.EmailField(unique=True)
    rol = models.CharField(max_length=20, choices=Rol.choices, default=Rol.EMPLEADO)
    
    # Relación con empleado (para portal autoservicio)
    empleado = models.OneToOneField(
        'empleados.Empleado',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='usuario'
    )
    
    # Empresas a las que tiene acceso (para empleador)
    empresas = models.ManyToManyField(
        'empresas.Empresa',
        blank=True,
        related_name='usuarios_acceso'
    )
    
    # Configuraciones de usuario
    notificaciones_email = models.BooleanField(default=True)
    notificaciones_push = models.BooleanField(default=True)
    tema_oscuro = models.BooleanField(default=False)
    
    # Auditoría
    ultimo_acceso_chat = models.DateTimeField(null=True, blank=True)
    ip_ultimo_acceso = models.GenericIPAddressField(null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        db_table = 'usuarios'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    def __str__(self):
        return f"{self.email} ({self.get_rol_display()})"
    
    # ============ PROPIEDADES DE ROL ============
    @property
    def es_admin(self):
        """Administrador total del sistema"""
        return self.rol == self.Rol.ADMIN or self.is_superuser
    
    @property
    def es_empleador(self):
        """Empleador/RRHH - maneja empresas asignadas"""
        return self.rol == self.Rol.EMPLEADOR
    
    @property
    def es_empleado(self):
        """Empleado - solo ve su información"""
        return self.rol == self.Rol.EMPLEADO
    
    # ============ MÉTODOS DE ACCESO ============
    def tiene_acceso_empresa(self, empresa_id):
        """Verifica si el usuario tiene acceso a una empresa"""
        if self.es_admin:
            return True
        if self.es_empleador:
            return self.empresas.filter(id=empresa_id, activa=True).exists()
        if self.es_empleado and self.empleado:
            return self.empleado.empresa_id == empresa_id
        return False
    
    def tiene_acceso_empleado(self, empleado):
        """Verifica si puede ver/editar un empleado"""
        if self.es_admin:
            return True
        if self.es_empleador:
            return self.tiene_acceso_empresa(empleado.empresa_id)
        if self.es_empleado:
            return self.empleado_id == empleado.id
        return False
    
    def get_empresas_acceso(self):
        """Retorna las empresas a las que tiene acceso"""
        if self.es_admin:
            from apps.empresas.models import Empresa
            return Empresa.objects.filter(activa=True)
        if self.es_empleador:
            return self.empresas.filter(activa=True)
        if self.es_empleado and self.empleado:
            from apps.empresas.models import Empresa
            return Empresa.objects.filter(id=self.empleado.empresa_id)
        return self.empresas.none()
    
    def get_empleados_acceso(self):
        """Retorna los empleados que puede ver"""
        from apps.empleados.models import Empleado
        if self.es_admin:
            return Empleado.objects.all()
        if self.es_empleador:
            return Empleado.objects.filter(empresa__in=self.empresas.all())
        if self.es_empleado and self.empleado:
            return Empleado.objects.filter(id=self.empleado_id)
        return Empleado.objects.none()
    
    # ============ PERMISOS ESPECÍFICOS ============
    def puede_crear_empresa(self):
        return self.es_admin
    
    def puede_editar_empresa(self, empresa_id):
        return self.es_admin
    
    def puede_crear_empleado(self, empresa_id):
        return self.es_admin or (self.es_empleador and self.tiene_acceso_empresa(empresa_id))
    
    def puede_procesar_nomina(self, empresa_id):
        return self.es_admin or (self.es_empleador and self.tiene_acceso_empresa(empresa_id))
    
    def puede_aprobar_vacaciones(self, empleado):
        if self.es_admin:
            return True
        if self.es_empleador:
            return self.tiene_acceso_empresa(empleado.empresa_id)
        return False
    
    def puede_ver_nomina_empleado(self, empleado):
        if self.es_admin or self.es_empleador:
            return self.tiene_acceso_empleado(empleado)
        if self.es_empleado:
            return self.empleado_id == empleado.id
        return False
    
    def puede_usar_chat_admin(self):
        """Puede usar comandos administrativos en el chat"""
        return self.es_admin or self.es_empleador
    
    def puede_configurar_sistema(self):
        return self.es_admin


class TokenUsuario(models.Model):
    """Token para activacion de cuenta y reset de password"""

    class TipoToken(models.TextChoices):
        ACTIVACION = 'activacion', 'Activacion de Cuenta'
        RESET_PASSWORD = 'reset', 'Reset de Password'

    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='tokens'
    )
    token = models.CharField(max_length=64, unique=True, db_index=True)
    tipo = models.CharField(max_length=20, choices=TipoToken.choices)
    usado = models.BooleanField(default=False)
    expira_en = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    usado_en = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'usuarios_tokens'
        verbose_name = 'Token de Usuario'
        verbose_name_plural = 'Tokens de Usuario'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.usuario.email}"

    @classmethod
    def generar_token(cls):
        """Genera un token seguro"""
        return secrets.token_urlsafe(48)

    @classmethod
    def crear_token_activacion(cls, usuario, horas_valido=48):
        """Crea un token de activacion"""
        # Invalidar tokens anteriores del mismo tipo
        cls.objects.filter(
            usuario=usuario,
            tipo=cls.TipoToken.ACTIVACION,
            usado=False
        ).update(usado=True)

        return cls.objects.create(
            usuario=usuario,
            token=cls.generar_token(),
            tipo=cls.TipoToken.ACTIVACION,
            expira_en=timezone.now() + timedelta(hours=horas_valido)
        )

    @classmethod
    def crear_token_reset(cls, usuario, horas_valido=24):
        """Crea un token de reset de password"""
        # Invalidar tokens anteriores del mismo tipo
        cls.objects.filter(
            usuario=usuario,
            tipo=cls.TipoToken.RESET_PASSWORD,
            usado=False
        ).update(usado=True)

        return cls.objects.create(
            usuario=usuario,
            token=cls.generar_token(),
            tipo=cls.TipoToken.RESET_PASSWORD,
            expira_en=timezone.now() + timedelta(hours=horas_valido)
        )

    @property
    def es_valido(self):
        """Verifica si el token es valido"""
        return not self.usado and timezone.now() < self.expira_en

    def usar(self):
        """Marca el token como usado"""
        self.usado = True
        self.usado_en = timezone.now()
        self.save(update_fields=['usado', 'usado_en'])


class SolicitudCambioDatos(BaseModel):
    """Solicitud de cambio de datos sensibles del empleado"""

    class TipoCambio(models.TextChoices):
        RFC = 'rfc', 'RFC'
        CURP = 'curp', 'CURP'
        NSS = 'nss', 'Numero de Seguro Social'
        CUENTA_BANCARIA = 'cuenta_bancaria', 'Cuenta Bancaria'
        DIRECCION = 'direccion', 'Direccion'
        TELEFONO = 'telefono', 'Telefono'
        EMAIL = 'email_personal', 'Email Personal'
        CONTACTO_EMERGENCIA = 'contacto_emergencia', 'Contacto de Emergencia'

    class Estado(models.TextChoices):
        PENDIENTE = 'pendiente', 'Pendiente de Revision'
        APROBADA = 'aprobada', 'Aprobada'
        RECHAZADA = 'rechazada', 'Rechazada'

    empleado = models.ForeignKey(
        'empleados.Empleado',
        on_delete=models.CASCADE,
        related_name='solicitudes_cambio'
    )
    tipo_cambio = models.CharField(max_length=30, choices=TipoCambio.choices)
    datos_actuales = models.JSONField(default=dict, help_text='Datos actuales del empleado')
    datos_nuevos = models.JSONField(default=dict, help_text='Datos nuevos solicitados')
    justificacion = models.TextField(blank=True)
    documento_soporte = models.FileField(
        upload_to='solicitudes_cambio/%Y/%m/',
        blank=True,
        null=True,
        help_text='Documento de soporte (INE, comprobante, etc.)'
    )
    estado = models.CharField(
        max_length=20,
        choices=Estado.choices,
        default=Estado.PENDIENTE
    )
    revisado_por = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='solicitudes_revisadas'
    )
    fecha_revision = models.DateTimeField(null=True, blank=True)
    comentario_revision = models.TextField(blank=True)

    class Meta:
        db_table = 'usuarios_solicitudes_cambio'
        verbose_name = 'Solicitud de Cambio de Datos'
        verbose_name_plural = 'Solicitudes de Cambio de Datos'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.empleado.nombre_completo} - {self.get_tipo_cambio_display()}"

    def aprobar(self, usuario, comentario=''):
        """Aprueba la solicitud y aplica el cambio"""
        from apps.integraciones.google_calendar import AuditoriaService

        self.estado = self.Estado.APROBADA
        self.revisado_por = usuario
        self.fecha_revision = timezone.now()
        self.comentario_revision = comentario
        self.save()

        # Aplicar el cambio al empleado
        empleado = self.empleado
        datos_anteriores = {}

        for campo, valor in self.datos_nuevos.items():
            if hasattr(empleado, campo):
                datos_anteriores[campo] = getattr(empleado, campo)
                setattr(empleado, campo, valor)

        empleado.save()

        # Registrar en auditoria
        try:
            AuditoriaService.registrar(
                usuario=usuario,
                accion='UPDATE',
                descripcion=f'Cambio de {self.get_tipo_cambio_display()} aprobado para {empleado.nombre_completo}',
                objeto=empleado,
                datos_anteriores=datos_anteriores,
                datos_nuevos=self.datos_nuevos
            )
        except Exception:
            pass

        return True

    def rechazar(self, usuario, comentario=''):
        """Rechaza la solicitud"""
        self.estado = self.Estado.RECHAZADA
        self.revisado_por = usuario
        self.fecha_revision = timezone.now()
        self.comentario_revision = comentario
        self.save()
        return True
