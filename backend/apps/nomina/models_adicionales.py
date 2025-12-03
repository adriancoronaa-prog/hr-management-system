
# ============================================================
# MODELOS ADICIONALES PARA NÓMINA COMPLETA
# Agregar al final de apps/nomina/models.py
# ============================================================

class PeriodoNomina(BaseModel, AuditMixin):
    """
    Periodo de nómina (semanal, quincenal, mensual)
    """
    
    class TipoPeriodo(models.TextChoices):
        SEMANAL = 'semanal', 'Semanal'
        QUINCENAL = 'quincenal', 'Quincenal'
        MENSUAL = 'mensual', 'Mensual'
    
    class Estado(models.TextChoices):
        ABIERTO = 'abierto', 'Abierto'
        EN_PROCESO = 'en_proceso', 'En Proceso'
        CALCULADO = 'calculado', 'Calculado'
        AUTORIZADO = 'autorizado', 'Autorizado'
        PAGADO = 'pagado', 'Pagado'
        CERRADO = 'cerrado', 'Cerrado'
    
    empresa = models.ForeignKey(
        'empresas.Empresa', on_delete=models.CASCADE, related_name='periodos_nomina'
    )
    
    tipo = models.CharField(max_length=20, choices=TipoPeriodo.choices)
    numero_periodo = models.PositiveIntegerField(help_text='Número de periodo en el año')
    año = models.PositiveIntegerField()
    
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    fecha_pago = models.DateField()
    
    dias_periodo = models.PositiveIntegerField(default=15)
    
    estado = models.CharField(max_length=20, choices=Estado.choices, default=Estado.ABIERTO)
    
    # Totales calculados
    total_percepciones = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_deducciones = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_neto = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_empleados = models.PositiveIntegerField(default=0)
    
    # Autorización
    autorizado_por = models.ForeignKey(
        'empleados.Empleado', on_delete=models.SET_NULL, 
        null=True, blank=True, related_name='periodos_autorizados'
    )
    fecha_autorizacion = models.DateTimeField(null=True, blank=True)
    
    # Dispersión
    archivo_dispersion = models.FileField(
        upload_to='nomina/dispersion/', null=True, blank=True
    )
    fecha_dispersion = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'nomina_periodos'
        ordering = ['-año', '-numero_periodo']
        unique_together = ['empresa', 'tipo', 'año', 'numero_periodo']
        verbose_name = 'Periodo de Nómina'
        verbose_name_plural = 'Periodos de Nómina'

    def __str__(self):
        return f"{self.empresa.nombre_comercial} - {self.get_tipo_display()} {self.numero_periodo}/{self.año}"
    
    @property
    def nombre_periodo(self):
        return f"{self.get_tipo_display()} {self.numero_periodo} - {self.año}"


class Incidencia(BaseModel, AuditMixin):
    """
    Incidencias de nómina: faltas, retardos, horas extra, permisos, incapacidades
    """
    
    class TipoIncidencia(models.TextChoices):
        FALTA_JUSTIFICADA = 'falta_justificada', 'Falta Justificada'
        FALTA_INJUSTIFICADA = 'falta_injustificada', 'Falta Injustificada'
        RETARDO = 'retardo', 'Retardo'
        HORA_EXTRA_DOBLE = 'hora_extra_doble', 'Hora Extra Doble'
        HORA_EXTRA_TRIPLE = 'hora_extra_triple', 'Hora Extra Triple'
        PERMISO_CON_GOCE = 'permiso_con_goce', 'Permiso Con Goce'
        PERMISO_SIN_GOCE = 'permiso_sin_goce', 'Permiso Sin Goce'
        INCAPACIDAD_GENERAL = 'incapacidad_general', 'Incapacidad Enfermedad General'
        INCAPACIDAD_RIESGO = 'incapacidad_riesgo', 'Incapacidad Riesgo de Trabajo'
        INCAPACIDAD_MATERNIDAD = 'incapacidad_maternidad', 'Incapacidad Maternidad'
        VACACIONES = 'vacaciones', 'Vacaciones'
        DESCANSO_LABORADO = 'descanso_laborado', 'Descanso Laborado'
        FESTIVO_LABORADO = 'festivo_laborado', 'Día Festivo Laborado'
    
    class Estado(models.TextChoices):
        PENDIENTE = 'pendiente', 'Pendiente'
        APROBADA = 'aprobada', 'Aprobada'
        RECHAZADA = 'rechazada', 'Rechazada'
        APLICADA = 'aplicada', 'Aplicada en Nómina'
    
    empleado = models.ForeignKey(
        'empleados.Empleado', on_delete=models.CASCADE, related_name='incidencias'
    )
    periodo = models.ForeignKey(
        PeriodoNomina, on_delete=models.CASCADE, 
        related_name='incidencias', null=True, blank=True
    )
    
    tipo = models.CharField(max_length=30, choices=TipoIncidencia.choices)
    fecha = models.DateField()
    fecha_fin = models.DateField(null=True, blank=True, help_text='Para incidencias de varios días')
    
    cantidad = models.DecimalField(
        max_digits=5, decimal_places=2, default=1,
        help_text='Días, horas, o cantidad según el tipo'
    )
    
    motivo = models.TextField(blank=True)
    documento_soporte = models.FileField(
        upload_to='nomina/incidencias/', null=True, blank=True
    )
    
    # Para incapacidades IMSS
    folio_incapacidad = models.CharField(max_length=50, blank=True)
    
    estado = models.CharField(max_length=20, choices=Estado.choices, default=Estado.PENDIENTE)
    
    aprobado_por = models.ForeignKey(
        'empleados.Empleado', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='incidencias_aprobadas'
    )
    fecha_aprobacion = models.DateTimeField(null=True, blank=True)
    
    # Impacto en nómina
    monto_impacto = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True,
        help_text='Monto que afecta a la nómina (puede ser positivo o negativo)'
    )

    class Meta:
        db_table = 'nomina_incidencias'
        ordering = ['-fecha', 'empleado']
        verbose_name = 'Incidencia'
        verbose_name_plural = 'Incidencias'

    def __str__(self):
        return f"{self.empleado.nombre_completo} - {self.get_tipo_display()} ({self.fecha})"
    
    @property
    def dias_totales(self):
        if self.fecha_fin:
            return (self.fecha_fin - self.fecha).days + 1
        return 1


class PercepcionVariable(BaseModel):
    """
    Percepciones variables: comisiones, bonos, premios, etc.
    """
    
    class TipoPercepcion(models.TextChoices):
        COMISION = 'comision', 'Comisión'
        BONO_PRODUCTIVIDAD = 'bono_productividad', 'Bono de Productividad'
        BONO_PUNTUALIDAD = 'bono_puntualidad', 'Bono de Puntualidad'
        BONO_ASISTENCIA = 'bono_asistencia', 'Bono de Asistencia'
        PREMIO = 'premio', 'Premio'
        GRATIFICACION = 'gratificacion', 'Gratificación'
        RETROACTIVO = 'retroactivo', 'Pago Retroactivo'
        VALES_DESPENSA = 'vales_despensa', 'Vales de Despensa'
        AYUDA_TRANSPORTE = 'ayuda_transporte', 'Ayuda de Transporte'
        AYUDA_ALIMENTACION = 'ayuda_alimentacion', 'Ayuda de Alimentación'
        OTRO = 'otro', 'Otro'
    
    empleado = models.ForeignKey(
        'empleados.Empleado', on_delete=models.CASCADE, related_name='percepciones_variables'
    )
    periodo = models.ForeignKey(
        PeriodoNomina, on_delete=models.CASCADE, related_name='percepciones_variables'
    )
    
    tipo = models.CharField(max_length=30, choices=TipoPercepcion.choices)
    concepto = models.CharField(max_length=200, blank=True, help_text='Descripción adicional')
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    
    es_gravable = models.BooleanField(default=True)
    es_integrable_sdi = models.BooleanField(default=False, help_text='Integra al SDI')

    class Meta:
        db_table = 'nomina_percepciones_variables'
        ordering = ['-created_at']
        verbose_name = 'Percepción Variable'
        verbose_name_plural = 'Percepciones Variables'

    def __str__(self):
        return f"{self.empleado.nombre_completo} - {self.get_tipo_display()} ${self.monto}"


class DeduccionVariable(BaseModel):
    """
    Deducciones variables: préstamos, pensiones alimenticias, etc.
    """
    
    class TipoDeduccion(models.TextChoices):
        PRESTAMO_EMPRESA = 'prestamo_empresa', 'Préstamo de Empresa'
        PRESTAMO_INFONAVIT = 'prestamo_infonavit', 'Crédito INFONAVIT'
        PRESTAMO_FONACOT = 'prestamo_fonacot', 'Crédito FONACOT'
        PENSION_ALIMENTICIA = 'pension_alimenticia', 'Pensión Alimenticia'
        CAJA_AHORRO = 'caja_ahorro', 'Caja de Ahorro'
        SEGURO_VIDA = 'seguro_vida', 'Seguro de Vida'
        SEGURO_GMM = 'seguro_gmm', 'Seguro Gastos Médicos'
        FONDO_RETIRO = 'fondo_retiro', 'Fondo de Retiro'
        DESCUENTO_NOMINA = 'descuento', 'Descuento por Nómina'
        OTRO = 'otro', 'Otro'
    
    class TipoCalculo(models.TextChoices):
        FIJO = 'fijo', 'Monto Fijo'
        PORCENTAJE_SUELDO = 'porcentaje_sueldo', 'Porcentaje del Sueldo'
        PORCENTAJE_NETO = 'porcentaje_neto', 'Porcentaje del Neto'
        FACTOR_VSM = 'factor_vsm', 'Factor Veces Salario Mínimo'
    
    empleado = models.ForeignKey(
        'empleados.Empleado', on_delete=models.CASCADE, related_name='deducciones_fijas'
    )
    
    tipo = models.CharField(max_length=30, choices=TipoDeduccion.choices)
    concepto = models.CharField(max_length=200, blank=True)
    
    tipo_calculo = models.CharField(max_length=20, choices=TipoCalculo.choices, default=TipoCalculo.FIJO)
    valor = models.DecimalField(max_digits=12, decimal_places=2, help_text='Monto, porcentaje o factor')
    
    # Para préstamos
    monto_total = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    saldo_pendiente = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    numero_pagos = models.PositiveIntegerField(null=True, blank=True)
    pagos_realizados = models.PositiveIntegerField(default=0)
    
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField(null=True, blank=True)
    activa = models.BooleanField(default=True)
    
    # Referencia externa
    numero_credito = models.CharField(max_length=50, blank=True, help_text='No. crédito INFONAVIT/FONACOT')

    class Meta:
        db_table = 'nomina_deducciones_fijas'
        ordering = ['empleado', 'tipo']
        verbose_name = 'Deducción Fija/Variable'
        verbose_name_plural = 'Deducciones Fijas/Variables'

    def __str__(self):
        return f"{self.empleado.nombre_completo} - {self.get_tipo_display()}"
    
    def calcular_monto(self, salario_base, salario_neto=None):
        """Calcula el monto de la deducción según el tipo de cálculo"""
        from decimal import Decimal
        
        if self.tipo_calculo == self.TipoCalculo.FIJO:
            return self.valor
        elif self.tipo_calculo == self.TipoCalculo.PORCENTAJE_SUELDO:
            return salario_base * (self.valor / Decimal('100'))
        elif self.tipo_calculo == self.TipoCalculo.PORCENTAJE_NETO:
            if salario_neto:
                return salario_neto * (self.valor / Decimal('100'))
            return Decimal('0')
        elif self.tipo_calculo == self.TipoCalculo.FACTOR_VSM:
            # Salario mínimo 2024
            sm = Decimal('248.93')
            return sm * self.valor
        return self.valor


class PreNomina(BaseModel):
    """
    Pre-nómina: cálculo preliminar antes de autorización
    """
    
    periodo = models.ForeignKey(
        PeriodoNomina, on_delete=models.CASCADE, related_name='pre_nominas'
    )
    empleado = models.ForeignKey(
        'empleados.Empleado', on_delete=models.CASCADE, related_name='pre_nominas'
    )
    
    # Datos del empleado al momento del cálculo
    salario_diario = models.DecimalField(max_digits=12, decimal_places=2)
    salario_diario_integrado = models.DecimalField(max_digits=12, decimal_places=2)
    
    # Días
    dias_trabajados = models.DecimalField(max_digits=5, decimal_places=2)
    dias_pagados = models.DecimalField(max_digits=5, decimal_places=2)
    dias_incapacidad = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    dias_faltas = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    dias_vacaciones = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # Horas extra
    horas_extra_dobles = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    horas_extra_triples = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # Totales
    total_percepciones = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_percepciones_gravadas = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_percepciones_exentas = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    total_deducciones = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    isr_retenido = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    imss_empleado = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    otras_deducciones = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    neto_a_pagar = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Costo empresa
    imss_patron = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    rcv_patron = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    infonavit_patron = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    impuesto_nomina = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    costo_total_empresa = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Detalle JSON
    detalle_percepciones = models.JSONField(default=list)
    detalle_deducciones = models.JSONField(default=list)
    
    # Estado
    revisado = models.BooleanField(default=False)
    observaciones = models.TextField(blank=True)

    class Meta:
        db_table = 'nomina_pre_nomina'
        ordering = ['periodo', 'empleado']
        unique_together = ['periodo', 'empleado']
        verbose_name = 'Pre-Nómina'
        verbose_name_plural = 'Pre-Nóminas'

    def __str__(self):
        return f"{self.empleado.nombre_completo} - {self.periodo.nombre_periodo}"


class MovimientoBancario(BaseModel):
    """
    Movimientos para dispersión bancaria
    """
    
    class Estado(models.TextChoices):
        PENDIENTE = 'pendiente', 'Pendiente'
        PROCESADO = 'procesado', 'Procesado'
        RECHAZADO = 'rechazado', 'Rechazado'
        PAGADO = 'pagado', 'Pagado'
    
    periodo = models.ForeignKey(
        PeriodoNomina, on_delete=models.CASCADE, related_name='movimientos_bancarios'
    )
    empleado = models.ForeignKey(
        'empleados.Empleado', on_delete=models.CASCADE, related_name='movimientos_bancarios'
    )
    
    banco = models.CharField(max_length=100)
    clabe = models.CharField(max_length=18)
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    
    referencia = models.CharField(max_length=50, blank=True)
    concepto = models.CharField(max_length=200, default='PAGO DE NOMINA')
    
    estado = models.CharField(max_length=20, choices=Estado.choices, default=Estado.PENDIENTE)
    fecha_proceso = models.DateTimeField(null=True, blank=True)
    respuesta_banco = models.TextField(blank=True)

    class Meta:
        db_table = 'nomina_movimientos_bancarios'
        ordering = ['-created_at']
        verbose_name = 'Movimiento Bancario'
        verbose_name_plural = 'Movimientos Bancarios'

    def __str__(self):
        return f"{self.empleado.nombre_completo} - ${self.monto} ({self.estado})"
