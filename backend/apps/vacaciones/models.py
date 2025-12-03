from django.db import models
from apps.core.models import BaseModel, AuditMixin


class PeriodoVacacional(BaseModel):
    """Periodo vacacional por año de antigüedad"""
    
    empleado = models.ForeignKey(
        'empleados.Empleado',
        on_delete=models.CASCADE,
        related_name='periodos_vacacionales'
    )
    
    numero_periodo = models.PositiveIntegerField()  # 1, 2, 3...
    fecha_inicio_periodo = models.DateField()
    fecha_fin_periodo = models.DateField()
    
    dias_derecho = models.PositiveIntegerField()
    dias_tomados = models.PositiveIntegerField(default=0)
    
    fecha_vencimiento = models.DateField()
    es_historico = models.BooleanField(default=False)  # Registrado en alta retroactiva

    class Meta:
        db_table = 'periodos_vacacionales'
        unique_together = ['empleado', 'numero_periodo']
        ordering = ['numero_periodo']

    def __str__(self):
        return f"{self.empleado} - Año {self.numero_periodo}"
    
    @property
    def dias_pendientes(self):
        return self.dias_derecho - self.dias_tomados


class SolicitudVacaciones(BaseModel, AuditMixin):
    """Solicitud de vacaciones"""
    
    class Estado(models.TextChoices):
        PENDIENTE = 'pendiente', 'Pendiente'
        APROBADA = 'aprobada', 'Aprobada'
        RECHAZADA = 'rechazada', 'Rechazada'
        CANCELADA = 'cancelada', 'Cancelada'
    
    empleado = models.ForeignKey(
        'empleados.Empleado',
        on_delete=models.CASCADE,
        related_name='solicitudes_vacaciones'
    )
    periodo_vacacional = models.ForeignKey(
        PeriodoVacacional,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='solicitudes'
    )
    
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    dias_solicitados = models.PositiveIntegerField()
    
    estado = models.CharField(max_length=20, choices=Estado.choices, default=Estado.PENDIENTE)
    es_historico = models.BooleanField(default=False)  # Registro retroactivo
    
    # Aprobación
    aprobado_por = models.ForeignKey(
        'usuarios.Usuario',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='solicitudes_aprobadas'
    )
    fecha_aprobacion = models.DateTimeField(null=True, blank=True)
    comentarios = models.TextField(blank=True)
    
    # Datos adicionales
    sustituto = models.ForeignKey(
        'empleados.Empleado',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sustituciones'
    )
    notas = models.TextField(blank=True)

    class Meta:
        db_table = 'solicitudes_vacaciones'
        ordering = ['-fecha_inicio']

    def __str__(self):
        return f"{self.empleado} - {self.fecha_inicio} al {self.fecha_fin}"
