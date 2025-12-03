from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
from apps.core.models import BaseModel


class TablaISR(BaseModel):
    """
    Tabla de ISR según Art. 96 LISR
    Se actualiza anualmente por el SAT
    """
    class Periodicidad(models.TextChoices):
        MENSUAL = 'mensual', 'Mensual'
        QUINCENAL = 'quincenal', 'Quincenal'
        SEMANAL = 'semanal', 'Semanal'
        DIARIO = 'diario', 'Diario'
    
    año = models.IntegerField()
    periodicidad = models.CharField(max_length=20, choices=Periodicidad.choices)
    limite_inferior = models.DecimalField(max_digits=12, decimal_places=2)
    limite_superior = models.DecimalField(max_digits=12, decimal_places=2)
    cuota_fija = models.DecimalField(max_digits=12, decimal_places=2)
    porcentaje_excedente = models.DecimalField(
        max_digits=5, 
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    
    class Meta:
        db_table = 'nomina_tabla_isr'
        verbose_name = 'Tabla ISR'
        verbose_name_plural = 'Tablas ISR'
        unique_together = ['año', 'periodicidad', 'limite_inferior']
        ordering = ['año', 'periodicidad', 'limite_inferior']
    
    def __str__(self):
        return f"ISR {self.año} {self.periodicidad} ({self.limite_inferior}-{self.limite_superior})"


class TablaSubsidio(BaseModel):
    """
    Tabla de subsidio al empleo
    Beneficio fiscal para salarios bajos
    """
    año = models.IntegerField()
    periodicidad = models.CharField(max_length=20, choices=TablaISR.Periodicidad.choices)
    limite_inferior = models.DecimalField(max_digits=12, decimal_places=2)
    limite_superior = models.DecimalField(max_digits=12, decimal_places=2)
    subsidio = models.DecimalField(max_digits=12, decimal_places=2)
    
    class Meta:
        db_table = 'nomina_tabla_subsidio'
        verbose_name = 'Tabla Subsidio'
        verbose_name_plural = 'Tablas Subsidio'
        unique_together = ['año', 'periodicidad', 'limite_inferior']


class ParametrosIMSS(BaseModel):
    """
    Parámetros para cálculo de cuotas IMSS
    Incluye topes, factores y porcentajes vigentes
    """
    año = models.IntegerField(unique=True)
    
    # UMA (Unidad de Medida y Actualización)
    uma_diaria = models.DecimalField(max_digits=10, decimal_places=2)
    uma_mensual = models.DecimalField(max_digits=10, decimal_places=2)
    uma_anual = models.DecimalField(max_digits=12, decimal_places=2)
    
    # Salario mínimo
    salario_minimo_general = models.DecimalField(max_digits=10, decimal_places=2)
    salario_minimo_frontera = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Topes de cotización
    tope_sbc_veces_uma = models.IntegerField(default=25)  # 25 UMAs
    
    # Porcentajes cuota obrera (lo que paga el empleado)
    porc_enf_mat_obrera = models.DecimalField(max_digits=5, decimal_places=4, default=0.0040)  # 0.40%
    porc_invalidez_vida_obrera = models.DecimalField(max_digits=5, decimal_places=4, default=0.00625)  # 0.625%
    porc_cesantia_vejez_obrera = models.DecimalField(max_digits=5, decimal_places=4, default=0.01125)  # 1.125%
    
    # Porcentajes cuota patronal
    porc_riesgo_trabajo = models.DecimalField(max_digits=5, decimal_places=4, default=0.005)  # Clase I
    porc_enf_mat_patronal = models.DecimalField(max_digits=5, decimal_places=4, default=0.0105)
    porc_invalidez_vida_patronal = models.DecimalField(max_digits=5, decimal_places=4, default=0.0175)
    porc_cesantia_vejez_patronal = models.DecimalField(max_digits=5, decimal_places=4, default=0.03150)
    porc_guarderias = models.DecimalField(max_digits=5, decimal_places=4, default=0.01)
    porc_infonavit = models.DecimalField(max_digits=5, decimal_places=4, default=0.05)
    
    # Cuota fija enfermedad y maternidad
    cuota_fija_enf_mat = models.DecimalField(max_digits=5, decimal_places=4, default=0.204)  # 20.40%
    
    vigente = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'nomina_parametros_imss'
        verbose_name = 'Parámetros IMSS'
        verbose_name_plural = 'Parámetros IMSS'
    
    def save(self, *args, **kwargs):
        if self.vigente:
            ParametrosIMSS.objects.exclude(pk=self.pk).update(vigente=False)
        super().save(*args, **kwargs)
    
    @property
    def tope_sbc(self):
        """Tope del Salario Base de Cotización"""
        return self.uma_diaria * self.tope_sbc_veces_uma
    
    def __str__(self):
        return f"IMSS {self.año} {'(Vigente)' if self.vigente else ''}"


class PeriodoNomina(BaseModel):
    """
    Periodo de nómina (quincenal, semanal, mensual)
    """
    class TipoPeriodo(models.TextChoices):
        SEMANAL = 'semanal', 'Semanal'
        QUINCENAL = 'quincenal', 'Quincenal'
        MENSUAL = 'mensual', 'Mensual'
    
    class Estado(models.TextChoices):
        BORRADOR = 'borrador', 'Borrador'
        CALCULADO = 'calculado', 'Calculado'
        AUTORIZADO = 'autorizado', 'Autorizado'
        PAGADO = 'pagado', 'Pagado'
        TIMBRADO = 'timbrado', 'Timbrado'
        CANCELADO = 'cancelado', 'Cancelado'
    
    empresa = models.ForeignKey(
        'empresas.Empresa',
        on_delete=models.PROTECT,
        related_name='periodos_nomina'
    )
    tipo_periodo = models.CharField(max_length=20, choices=TipoPeriodo.choices)
    numero_periodo = models.IntegerField()  # Ej: Quincena 1, Semana 15
    año = models.IntegerField()
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    fecha_pago = models.DateField()
    
    estado = models.CharField(max_length=20, choices=Estado.choices, default=Estado.BORRADOR)
    
    # Totales del periodo
    total_percepciones = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    total_deducciones = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    total_neto = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    total_empleados = models.IntegerField(default=0)
    
    # Auditoría
    calculado_por = models.ForeignKey(
        'usuarios.Usuario',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='periodos_calculados'
    )
    fecha_calculo = models.DateTimeField(null=True, blank=True)
    autorizado_por = models.ForeignKey(
        'usuarios.Usuario',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='periodos_autorizados'
    )
    fecha_autorizacion = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'nomina_periodos'
        verbose_name = 'Periodo de Nómina'
        verbose_name_plural = 'Periodos de Nómina'
        unique_together = ['empresa', 'tipo_periodo', 'numero_periodo', 'año']
        ordering = ['-año', '-numero_periodo']
    
    def __str__(self):
        return f"{self.empresa.nombre_comercial or self.empresa.razon_social} - {self.get_tipo_periodo_display()} {self.numero_periodo}/{self.año}"


class ConceptoNomina(BaseModel):
    """
    Catálogo de conceptos de nómina (percepciones y deducciones)
    Alineado con catálogo SAT para CFDI
    """
    class TipoConcepto(models.TextChoices):
        PERCEPCION = 'percepcion', 'Percepción'
        DEDUCCION = 'deduccion', 'Deducción'
        OTRO_PAGO = 'otro_pago', 'Otro Pago'
    
    codigo_sat = models.CharField(max_length=10, blank=True)  # Clave SAT
    codigo_interno = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    tipo = models.CharField(max_length=20, choices=TipoConcepto.choices)
    
    # Configuración de cálculo
    es_gravable = models.BooleanField(default=True)  # Grava ISR
    es_integrable_sbc = models.BooleanField(default=True)  # Integra al SBC
    es_fijo = models.BooleanField(default=False)  # Siempre aparece
    
    # Para deducciones
    es_obligatorio = models.BooleanField(default=False)  # ISR, IMSS
    
    activo = models.BooleanField(default=True)
    orden = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'nomina_conceptos'
        verbose_name = 'Concepto de Nómina'
        verbose_name_plural = 'Conceptos de Nómina'
        ordering = ['tipo', 'orden', 'nombre']
    
    def __str__(self):
        return f"{self.codigo_interno} - {self.nombre}"


class ReciboNomina(BaseModel):
    """
    Recibo de nómina individual por empleado y periodo
    """
    class Estado(models.TextChoices):
        BORRADOR = 'borrador', 'Borrador'
        CALCULADO = 'calculado', 'Calculado'
        TIMBRADO = 'timbrado', 'Timbrado'
        CANCELADO = 'cancelado', 'Cancelado'
    
    periodo = models.ForeignKey(
        PeriodoNomina,
        on_delete=models.PROTECT,
        related_name='recibos'
    )
    empleado = models.ForeignKey(
        'empleados.Empleado',
        on_delete=models.PROTECT,
        related_name='recibos_nomina'
    )
    
    estado = models.CharField(max_length=20, choices=Estado.choices, default=Estado.BORRADOR)
    
    # Datos del empleado al momento del cálculo (snapshot)
    salario_diario = models.DecimalField(max_digits=10, decimal_places=2)
    salario_base_cotizacion = models.DecimalField(max_digits=10, decimal_places=2)
    dias_trabajados = models.IntegerField(default=15)  # Quincenal
    dias_pagados = models.IntegerField(default=15)
    
    # Totales
    total_percepciones = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_percepciones_gravadas = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_percepciones_exentas = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_deducciones = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_otros_pagos = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    neto_a_pagar = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # ISR
    base_gravable_isr = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    isr_antes_subsidio = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    subsidio_aplicado = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    isr_retenido = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # IMSS
    cuota_imss_obrera = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Timbrado CFDI (para futuro)
    uuid_cfdi = models.CharField(max_length=36, blank=True)
    fecha_timbrado = models.DateTimeField(null=True, blank=True)
    xml_cfdi = models.TextField(blank=True)
    pdf_cfdi = models.TextField(blank=True)  # Base64
    
    # Pago
    fecha_pago_real = models.DateField(null=True, blank=True)
    referencia_pago = models.CharField(max_length=50, blank=True)
    
    class Meta:
        db_table = 'nomina_recibos'
        verbose_name = 'Recibo de Nómina'
        verbose_name_plural = 'Recibos de Nómina'
        unique_together = ['periodo', 'empleado']
        ordering = ['-periodo__año', '-periodo__numero_periodo']
    
    def __str__(self):
        return f"Recibo {self.empleado} - {self.periodo}"


class DetalleReciboNomina(BaseModel):
    """
    Detalle de cada concepto en un recibo
    """
    recibo = models.ForeignKey(
        ReciboNomina,
        on_delete=models.CASCADE,
        related_name='detalles'
    )
    concepto = models.ForeignKey(
        ConceptoNomina,
        on_delete=models.PROTECT,
        related_name='detalles_recibo'
    )
    
    # Valores
    cantidad = models.DecimalField(max_digits=10, decimal_places=2, default=1)  # Horas, días, etc.
    valor_unitario = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    importe_gravado = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    importe_exento = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    importe_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Notas
    observaciones = models.CharField(max_length=200, blank=True)
    
    class Meta:
        db_table = 'nomina_detalle_recibos'
        verbose_name = 'Detalle de Recibo'
        verbose_name_plural = 'Detalles de Recibo'
        unique_together = ['recibo', 'concepto']
    
    def __str__(self):
        return f"{self.recibo} - {self.concepto.nombre}: {self.importe_total}"


class IncidenciaNomina(BaseModel):
    """
    Incidencias que afectan la nómina:
    - Faltas
    - Incapacidades
    - Horas extra
    - Bonos especiales
    """
    class TipoIncidencia(models.TextChoices):
        FALTA = 'falta', 'Falta'
        INCAPACIDAD = 'incapacidad', 'Incapacidad'
        VACACIONES = 'vacaciones', 'Vacaciones'
        PERMISO_CON_GOCE = 'permiso_cg', 'Permiso con goce'
        PERMISO_SIN_GOCE = 'permiso_sg', 'Permiso sin goce'
        HORAS_EXTRA = 'horas_extra', 'Horas extra'
        BONO = 'bono', 'Bono'
        COMISION = 'comision', 'Comisión'
        DESCUENTO = 'descuento', 'Descuento'
        PRESTAMO = 'prestamo', 'Préstamo'
        OTRO = 'otro', 'Otro'
    
    empleado = models.ForeignKey(
        'empleados.Empleado',
        on_delete=models.CASCADE,
        related_name='incidencias'
    )
    periodo = models.ForeignKey(
        PeriodoNomina,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='incidencias'
    )
    
    tipo = models.CharField(max_length=20, choices=TipoIncidencia.choices)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField(null=True, blank=True)
    
    # Valores
    cantidad = models.DecimalField(max_digits=10, decimal_places=2, default=1)  # Días, horas
    monto = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    
    # Incapacidad específico
    folio_incapacidad = models.CharField(max_length=20, blank=True)
    tipo_incapacidad = models.CharField(max_length=50, blank=True)  # Enfermedad general, Riesgo trabajo, Maternidad
    
    descripcion = models.TextField(blank=True)
    aplicado = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'nomina_incidencias'
        verbose_name = 'Incidencia'
        verbose_name_plural = 'Incidencias'
        ordering = ['-fecha_inicio']
    
    def __str__(self):
        return f"{self.empleado} - {self.get_tipo_display()} ({self.fecha_inicio})"


