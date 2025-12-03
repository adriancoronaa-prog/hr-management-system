from django.db import models
from apps.core.models import BaseModel, AuditMixin


class Contrato(BaseModel, AuditMixin):
    """Contrato laboral"""
    
    class TipoContrato(models.TextChoices):
        INDEFINIDO = 'indefinido', 'Indefinido'
        TEMPORAL = 'temporal', 'Temporal'
        OBRA = 'obra', 'Por obra determinada'
        TIEMPO = 'tiempo', 'Por tiempo determinado'
        CAPACITACION = 'capacitacion', 'Capacitación inicial'
        PRUEBA = 'prueba', 'Periodo de prueba'
    
    class Estado(models.TextChoices):
        VIGENTE = 'vigente', 'Vigente'
        VENCIDO = 'vencido', 'Vencido'
        RENOVADO = 'renovado', 'Renovado'
        CANCELADO = 'cancelado', 'Cancelado'
    
    empleado = models.ForeignKey(
        'empleados.Empleado',
        on_delete=models.CASCADE,
        related_name='contratos'
    )
    
    tipo_contrato = models.CharField(max_length=20, choices=TipoContrato.choices)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField(null=True, blank=True)
    
    puesto = models.CharField(max_length=100, blank=True)
    salario_diario = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    condiciones_especiales = models.TextField(blank=True)
    
    documento = models.FileField(upload_to='contratos/', blank=True, null=True)
    
    estado = models.CharField(max_length=20, choices=Estado.choices, default=Estado.VIGENTE)
    contrato_anterior = models.ForeignKey(
        'self', on_delete=models.SET_NULL, null=True, blank=True, related_name='renovacion'
    )

    class Meta:
        db_table = 'contratos'
        ordering = ['-fecha_inicio']

    def __str__(self):
        return f"{self.empleado} - {self.tipo_contrato} ({self.fecha_inicio})"
