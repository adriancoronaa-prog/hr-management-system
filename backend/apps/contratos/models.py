from django.db import models
from django.utils import timezone
from datetime import timedelta
from apps.core.models import BaseModel, AuditMixin


class Contrato(BaseModel, AuditMixin):
    """Contrato laboral"""

    class TipoContrato(models.TextChoices):
        INDEFINIDO = 'indefinido', 'Indefinido'
        TEMPORAL = 'temporal', 'Temporal'
        OBRA = 'obra', 'Por obra determinada'
        TIEMPO = 'tiempo', 'Por tiempo determinado'
        CAPACITACION = 'capacitacion', 'Capacitacion inicial'
        PRUEBA = 'prueba', 'Periodo de prueba'

    class Estado(models.TextChoices):
        VIGENTE = 'vigente', 'Vigente'
        VENCIDO = 'vencido', 'Vencido'
        RENOVADO = 'renovado', 'Renovado'
        CANCELADO = 'cancelado', 'Cancelado'
        TERMINADO = 'terminado', 'Terminado'

    empleado = models.ForeignKey(
        'empleados.Empleado',
        on_delete=models.CASCADE,
        related_name='contratos'
    )

    tipo_contrato = models.CharField(max_length=20, choices=TipoContrato.choices)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField(null=True, blank=True)

    puesto = models.CharField(max_length=100, blank=True)
    departamento = models.CharField(max_length=100, blank=True)
    salario_diario = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    salario_mensual = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    jornada = models.CharField(max_length=20, blank=True)  # diurna, nocturna, mixta
    horario = models.CharField(max_length=100, blank=True)  # "9:00 - 18:00"

    condiciones_especiales = models.TextField(blank=True)
    clausulas_adicionales = models.TextField(blank=True)

    documento = models.FileField(upload_to='contratos/', blank=True, null=True)
    documento_firmado = models.FileField(upload_to='contratos/firmados/', blank=True, null=True)
    fecha_firma = models.DateField(null=True, blank=True)

    estado = models.CharField(max_length=20, choices=Estado.choices, default=Estado.VIGENTE)
    contrato_anterior = models.ForeignKey(
        'self', on_delete=models.SET_NULL, null=True, blank=True, related_name='renovaciones'
    )
    motivo_terminacion = models.TextField(blank=True)
    fecha_terminacion = models.DateField(null=True, blank=True)

    # Alertas
    alerta_enviada_30 = models.BooleanField(default=False)
    alerta_enviada_15 = models.BooleanField(default=False)
    alerta_enviada_7 = models.BooleanField(default=False)

    class Meta:
        db_table = 'contratos'
        ordering = ['-fecha_inicio']

    def __str__(self):
        return f"{self.empleado} - {self.get_tipo_contrato_display()} ({self.fecha_inicio})"

    @property
    def es_vigente(self):
        if self.estado != self.Estado.VIGENTE:
            return False
        if self.fecha_fin and self.fecha_fin < timezone.now().date():
            return False
        return True

    @property
    def es_indefinido(self):
        return self.tipo_contrato == self.TipoContrato.INDEFINIDO

    @property
    def dias_para_vencer(self):
        if not self.fecha_fin:
            return None
        return (self.fecha_fin - timezone.now().date()).days

    @property
    def esta_por_vencer(self):
        dias = self.dias_para_vencer
        return dias is not None and 0 < dias <= 30

    @property
    def esta_vencido(self):
        dias = self.dias_para_vencer
        return dias is not None and dias <= 0

    @property
    def duracion_dias(self):
        fecha_fin = self.fecha_fin or timezone.now().date()
        return (fecha_fin - self.fecha_inicio).days

    @property
    def numero_renovaciones(self):
        return Contrato.objects.filter(contrato_anterior=self).count()

    @property
    def contrato_original(self):
        """Obtiene el primer contrato de la cadena de renovaciones"""
        actual = self
        while actual.contrato_anterior:
            actual = actual.contrato_anterior
        return actual

    def renovar(self, fecha_inicio, fecha_fin=None, **kwargs):
        """Crea un nuevo contrato como renovacion de este"""
        self.estado = self.Estado.RENOVADO
        self.save()

        nuevo = Contrato.objects.create(
            empleado=self.empleado,
            tipo_contrato=kwargs.get('tipo_contrato', self.tipo_contrato),
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            puesto=kwargs.get('puesto', self.puesto),
            departamento=kwargs.get('departamento', self.departamento),
            salario_diario=kwargs.get('salario_diario', self.salario_diario),
            salario_mensual=kwargs.get('salario_mensual', self.salario_mensual),
            jornada=kwargs.get('jornada', self.jornada),
            horario=kwargs.get('horario', self.horario),
            condiciones_especiales=kwargs.get('condiciones_especiales', self.condiciones_especiales),
            contrato_anterior=self,
            created_by=kwargs.get('created_by')
        )
        return nuevo

    def terminar(self, motivo, fecha=None):
        """Termina el contrato"""
        self.estado = self.Estado.TERMINADO
        self.motivo_terminacion = motivo
        self.fecha_terminacion = fecha or timezone.now().date()
        self.save()

    def actualizar_estado(self):
        """Actualiza el estado segun las fechas"""
        if self.estado in [self.Estado.RENOVADO, self.Estado.CANCELADO, self.Estado.TERMINADO]:
            return

        if self.esta_vencido:
            self.estado = self.Estado.VENCIDO
            self.save()


class Adenda(BaseModel, AuditMixin):
    """Modificacion/Adenda a un contrato existente"""

    class TipoAdenda(models.TextChoices):
        CAMBIO_SALARIO = 'cambio_salario', 'Cambio de Salario'
        CAMBIO_PUESTO = 'cambio_puesto', 'Cambio de Puesto'
        CAMBIO_HORARIO = 'cambio_horario', 'Cambio de Horario'
        CAMBIO_DEPARTAMENTO = 'cambio_departamento', 'Cambio de Departamento'
        EXTENSION = 'extension', 'Extension de Contrato'
        CONDICIONES = 'condiciones', 'Cambio de Condiciones'
        OTRO = 'otro', 'Otro'

    contrato = models.ForeignKey(
        Contrato, on_delete=models.CASCADE, related_name='adendas'
    )

    tipo = models.CharField(max_length=30, choices=TipoAdenda.choices)
    fecha_aplicacion = models.DateField()
    descripcion = models.TextField()

    # Valores anteriores y nuevos (JSON para flexibilidad)
    valores_anteriores = models.JSONField(default=dict, blank=True)
    valores_nuevos = models.JSONField(default=dict, blank=True)

    documento = models.FileField(upload_to='contratos/adendas/', blank=True, null=True)

    aplicada = models.BooleanField(default=False)
    fecha_aplicada = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'contratos_adendas'
        ordering = ['-fecha_aplicacion']

    def __str__(self):
        return f"Adenda {self.get_tipo_display()} - {self.contrato.empleado}"

    def aplicar(self):
        """Aplica los cambios de la adenda al contrato"""
        if self.aplicada:
            return

        contrato = self.contrato

        for campo, valor in self.valores_nuevos.items():
            if hasattr(contrato, campo):
                setattr(contrato, campo, valor)

        contrato.save()
        self.aplicada = True
        self.fecha_aplicada = timezone.now()
        self.save()
