from django.db import models
from apps.core.models import BaseModel, AuditMixin


# ============ CATALOGOS DE PRESTACIONES ============

CATEGORIAS_PRESTACION = [
    ('economica', 'Economica'),
    ('salud', 'Salud y Bienestar'),
    ('tiempo', 'Tiempo y Flexibilidad'),
    ('desarrollo', 'Desarrollo y Educacion'),
    ('familia', 'Familia'),
    ('otro', 'Otro'),
]

TIPOS_PRESTACION_CATALOGO = [
    # Economicas
    ('vales_despensa', 'Vales de despensa', 'economica'),
    ('fondo_ahorro', 'Fondo de ahorro', 'economica'),
    ('bono_productividad', 'Bono de productividad', 'economica'),
    ('bono_puntualidad', 'Bono de puntualidad', 'economica'),
    ('bono_asistencia', 'Bono de asistencia', 'economica'),
    ('ayuda_transporte', 'Ayuda de transporte', 'economica'),
    ('ayuda_comedor', 'Ayuda de comedor', 'economica'),
    ('caja_ahorro', 'Caja de ahorro', 'economica'),
    # Salud
    ('sgmm', 'Seguro de Gastos Medicos Mayores', 'salud'),
    ('seguro_vida', 'Seguro de vida', 'salud'),
    ('seguro_dental', 'Seguro dental', 'salud'),
    ('seguro_vision', 'Seguro de vision', 'salud'),
    ('checkup_medico', 'Check-up medico anual', 'salud'),
    ('apoyo_psicologico', 'Apoyo psicologico', 'salud'),
    ('gimnasio', 'Gimnasio', 'salud'),
    # Tiempo
    ('vacaciones_extra', 'Dias de vacaciones adicionales', 'tiempo'),
    ('dia_cumpleanos', 'Dia de cumpleanos libre', 'tiempo'),
    ('dias_personales', 'Dias personales', 'tiempo'),
    ('home_office', 'Home office', 'tiempo'),
    ('horario_flexible', 'Horario flexible', 'tiempo'),
    ('viernes_corto', 'Viernes corto', 'tiempo'),
    # Desarrollo
    ('beca_educativa', 'Beca educativa', 'desarrollo'),
    ('cursos_certificaciones', 'Cursos y certificaciones', 'desarrollo'),
    ('clases_idiomas', 'Clases de idiomas', 'desarrollo'),
    # Familia
    ('guarderia', 'Apoyo de guarderia', 'familia'),
    ('beca_hijos', 'Beca para hijos', 'familia'),
    ('licencia_paternidad_ext', 'Licencia de paternidad extendida', 'familia'),
    ('licencia_maternidad_ext', 'Licencia de maternidad extendida', 'familia'),
    # Otros
    ('auto_empresarial', 'Auto empresarial', 'otro'),
    ('estacionamiento', 'Estacionamiento', 'otro'),
    ('telefono_celular', 'Telefono celular', 'otro'),
    ('laptop_equipo', 'Laptop/Equipo de trabajo', 'otro'),
    ('prestamo_personal', 'Prestamo personal', 'otro'),
    ('canasta_navidena', 'Canasta navidena', 'otro'),
    ('otro', 'Otro', 'otro'),
]

# Generar choices para el modelo
TIPOS_PRESTACION_CHOICES = [(t[0], t[1]) for t in TIPOS_PRESTACION_CATALOGO]

# Mapa tipo -> categoria para busqueda rapida
TIPO_A_CATEGORIA = {t[0]: t[2] for t in TIPOS_PRESTACION_CATALOGO}


class PlanPrestaciones(BaseModel, AuditMixin):
    """Plan de prestaciones por empresa"""
    
    empresa = models.ForeignKey(
        'empresas.Empresa',
        on_delete=models.CASCADE,
        related_name='planes_prestaciones'
    )
    
    nombre = models.CharField(max_length=100)  # "Plan Estándar", "Plan Ejecutivo"
    descripcion = models.TextField(blank=True)
    es_default = models.BooleanField(default=False)
    activo = models.BooleanField(default=True)
    
    # Configuración de prestaciones de ley (superiores al mínimo)
    # Vacaciones: días extra sobre la ley
    vacaciones_dias_extra = models.PositiveIntegerField(
        default=0,
        help_text="Días adicionales sobre los de ley"
    )
    
    # Prima vacacional: porcentaje (mínimo 25%)
    prima_vacacional_porcentaje = models.PositiveIntegerField(
        default=25,
        help_text="Porcentaje de prima vacacional"
    )
    
    # Aguinaldo: días (mínimo 15)
    aguinaldo_dias = models.PositiveIntegerField(
        default=15,
        help_text="Días de aguinaldo"
    )

    class Meta:
        db_table = 'planes_prestaciones'
        ordering = ['empresa', 'nombre']

    def __str__(self):
        return f"{self.empresa.razon_social} - {self.nombre}"
    
    def get_config_vacaciones(self):
        return {'dias_extra': self.vacaciones_dias_extra}
    
    def get_config_prima_vacacional(self):
        return {'porcentaje': self.prima_vacacional_porcentaje}
    
    def get_config_aguinaldo(self):
        return {'dias': self.aguinaldo_dias}
    
    def save(self, *args, **kwargs):
        # Validar mínimos de ley
        if self.prima_vacacional_porcentaje < 25:
            self.prima_vacacional_porcentaje = 25
        if self.aguinaldo_dias < 15:
            self.aguinaldo_dias = 15
        
        # Si es default, quitar default de otros planes de la misma empresa
        if self.es_default:
            PlanPrestaciones.objects.filter(
                empresa=self.empresa, es_default=True
            ).exclude(pk=self.pk).update(es_default=False)
        
        super().save(*args, **kwargs)


class PrestacionAdicional(BaseModel):
    """Prestaciones adicionales (no de ley) en un plan"""

    class TipoValor(models.TextChoices):
        MONTO_FIJO = 'monto', 'Monto fijo'
        PORCENTAJE = 'porcentaje', 'Porcentaje del salario'
        TEXTO = 'texto', 'Descripcion'

    class Periodicidad(models.TextChoices):
        MENSUAL = 'mensual', 'Mensual'
        ANUAL = 'anual', 'Anual'
        UNICA = 'unica', 'Unica vez'

    plan = models.ForeignKey(
        PlanPrestaciones,
        on_delete=models.CASCADE,
        related_name='prestaciones_adicionales'
    )

    # Clasificacion
    categoria = models.CharField(
        max_length=20,
        choices=CATEGORIAS_PRESTACION,
        default='otro',
        help_text='Categoria de la prestacion'
    )
    tipo_prestacion = models.CharField(
        max_length=50,
        choices=TIPOS_PRESTACION_CHOICES,
        null=True,
        blank=True,
        help_text='Tipo predefinido del catalogo'
    )

    # Datos basicos (nombre se mantiene para compatibilidad y prestaciones personalizadas)
    nombre = models.CharField(max_length=100)  # "Vales de despensa", "SGMM"
    descripcion = models.TextField(blank=True, help_text='Descripcion detallada de la prestacion')

    # Valor y periodicidad
    tipo_valor = models.CharField(max_length=20, choices=TipoValor.choices)
    valor = models.CharField(max_length=100)  # "2000", "10", "Cobertura basica"
    periodicidad = models.CharField(
        max_length=20, choices=Periodicidad.choices, default=Periodicidad.MENSUAL
    )

    # Topes
    tope_mensual = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True,
        help_text='Tope maximo mensual en pesos'
    )
    tope_anual = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True,
        help_text='Tope maximo anual en pesos'
    )

    # Para fondo de ahorro y similares
    porcentaje_empresa = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True,
        help_text='Porcentaje que aporta la empresa'
    )
    porcentaje_empleado = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True,
        help_text='Porcentaje que aporta el empleado'
    )

    # Dependientes (para seguros)
    aplica_a_dependientes = models.BooleanField(
        default=False,
        help_text='Si la prestacion aplica a familiares/dependientes'
    )
    numero_dependientes = models.PositiveIntegerField(
        null=True, blank=True,
        help_text='Numero maximo de dependientes cubiertos'
    )

    # Proveedor
    proveedor = models.CharField(
        max_length=200, blank=True,
        help_text='Nombre del proveedor (aseguradora, empresa de vales, etc.)'
    )

    # Estado y orden
    activo = models.BooleanField(default=True)
    orden = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'prestaciones_adicionales'
        ordering = ['plan', 'categoria', 'orden', 'nombre']

    def __str__(self):
        if self.tipo_prestacion:
            return f"{self.plan.nombre} - {self.get_tipo_prestacion_display()}"
        return f"{self.plan.nombre} - {self.nombre}"

    def get_categoria_from_tipo(self):
        """Obtiene la categoria basada en el tipo_prestacion del catalogo"""
        if self.tipo_prestacion and self.tipo_prestacion in TIPO_A_CATEGORIA:
            return TIPO_A_CATEGORIA[self.tipo_prestacion]
        return self.categoria

    def save(self, *args, **kwargs):
        # Auto-asignar categoria si se selecciona un tipo del catalogo
        if self.tipo_prestacion and self.tipo_prestacion in TIPO_A_CATEGORIA:
            self.categoria = TIPO_A_CATEGORIA[self.tipo_prestacion]
            # Auto-asignar nombre si esta vacio
            if not self.nombre:
                for t in TIPOS_PRESTACION_CATALOGO:
                    if t[0] == self.tipo_prestacion:
                        self.nombre = t[1]
                        break
        super().save(*args, **kwargs)


class AjusteIndividual(BaseModel, AuditMixin):
    """Ajustes individuales de prestaciones por empleado"""
    
    class TipoAjuste(models.TextChoices):
        REEMPLAZA = 'reemplaza', 'Reemplaza valor del plan'
        SUMA = 'suma', 'Suma al valor del plan'
    
    empleado = models.ForeignKey(
        'empleados.Empleado',
        on_delete=models.CASCADE,
        related_name='ajustes_prestaciones'
    )
    
    # Tipo de prestación afectada
    concepto = models.CharField(max_length=50)  # vacaciones, aguinaldo, prima_vac, etc.
    
    tipo_ajuste = models.CharField(max_length=20, choices=TipoAjuste.choices)
    valor = models.CharField(max_length=100)
    
    motivo = models.TextField()
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField(null=True, blank=True)  # NULL = permanente
    
    activo = models.BooleanField(default=True)

    class Meta:
        db_table = 'ajustes_individuales'
        ordering = ['-fecha_inicio']

    def __str__(self):
        return f"{self.empleado} - {self.concepto}"
