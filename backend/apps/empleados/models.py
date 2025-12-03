from django.db import models
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from apps.core.models import BaseModel, AuditMixin


class Empleado(BaseModel, AuditMixin):
    """Empleado de una empresa"""

    class Estado(models.TextChoices):
        ACTIVO = 'activo', 'Activo'
        BAJA = 'baja', 'Baja'
        INCAPACIDAD = 'incapacidad', 'Incapacidad'

    class TipoBaja(models.TextChoices):
        RENUNCIA_VOLUNTARIA = 'renuncia_voluntaria', 'Renuncia Voluntaria'
        DESPIDO_JUSTIFICADO = 'despido_justificado', 'Despido Justificado'
        DESPIDO_INJUSTIFICADO = 'despido_injustificado', 'Despido Injustificado'
        TERMINO_CONTRATO = 'termino_contrato', 'Término de Contrato'
        JUBILACION = 'jubilacion', 'Jubilación'
        FALLECIMIENTO = 'fallecimiento', 'Fallecimiento'
        MUTUO_ACUERDO = 'mutuo_acuerdo', 'Mutuo Acuerdo'
        OTRO = 'otro', 'Otro'

    class TipoContrato(models.TextChoices):
        INDEFINIDO = 'indefinido', 'Indefinido'
        TEMPORAL = 'temporal', 'Temporal'
        OBRA = 'obra', 'Por obra determinada'
        TIEMPO = 'tiempo', 'Por tiempo determinado'
        CAPACITACION = 'capacitacion', 'Capacitación inicial'
        PRUEBA = 'prueba', 'Periodo de prueba'
    
    class Jornada(models.TextChoices):
        DIURNA = 'diurna', 'Diurna'
        NOCTURNA = 'nocturna', 'Nocturna'
        MIXTA = 'mixta', 'Mixta'
    
    # Relaciones
    empresa = models.ForeignKey(
        'empresas.Empresa', on_delete=models.PROTECT, related_name='empleados'
    )
    plan_prestaciones = models.ForeignKey(
        'prestaciones.PlanPrestaciones', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='empleados'
    )
    jefe_directo = models.ForeignKey(
        'self', on_delete=models.SET_NULL, null=True, blank=True, related_name='subordinados'
    )
    
    # Datos personales
    nombre = models.CharField(max_length=100)
    apellido_paterno = models.CharField(max_length=100)
    apellido_materno = models.CharField(max_length=100, blank=True)
    curp = models.CharField(max_length=18, blank=True)
    rfc = models.CharField(max_length=13, blank=True)
    nss_imss = models.CharField(max_length=11, blank=True)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    genero = models.CharField(max_length=20, blank=True)
    estado_civil = models.CharField(max_length=30, blank=True)
    
    # Contacto
    telefono_personal = models.CharField(max_length=20, blank=True)
    email_personal = models.EmailField(blank=True)
    email_corporativo = models.EmailField(blank=True)
    
    # Dirección
    direccion_calle = models.CharField(max_length=255, blank=True)
    direccion_numero = models.CharField(max_length=20, blank=True)
    direccion_colonia = models.CharField(max_length=100, blank=True)
    direccion_cp = models.CharField(max_length=5, blank=True)
    direccion_municipio = models.CharField(max_length=100, blank=True)
    direccion_estado = models.CharField(max_length=50, blank=True)
    
    # Contacto emergencia
    emergencia_nombre = models.CharField(max_length=255, blank=True)
    emergencia_parentesco = models.CharField(max_length=50, blank=True)
    emergencia_telefono = models.CharField(max_length=20, blank=True)
    
    # Datos bancarios
    banco = models.CharField(max_length=100, blank=True)
    clabe = models.CharField(max_length=18, blank=True)
    
    # Datos laborales
    fecha_ingreso = models.DateField()  # PUEDE SER RETROACTIVA
    puesto = models.CharField(max_length=100, blank=True)
    departamento = models.CharField(max_length=100, blank=True)
    tipo_contrato = models.CharField(max_length=20, choices=TipoContrato.choices, blank=True)
    jornada = models.CharField(max_length=20, choices=Jornada.choices, blank=True)
    modalidad = models.CharField(max_length=20, default='presencial')
    
    # Salario
    salario_diario = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    
    # Estado
    estado = models.CharField(max_length=20, choices=Estado.choices, default=Estado.ACTIVO)

    # Datos de baja
    fecha_baja = models.DateField(null=True, blank=True)
    tipo_baja = models.CharField(
        max_length=30,
        choices=TipoBaja.choices,
        null=True,
        blank=True
    )
    motivo_baja = models.TextField(blank=True)
    liquidacion_pagada = models.BooleanField(default=False)
    monto_liquidacion = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Monto total de liquidación/finiquito pagado'
    )
    fecha_ultimo_dia_laborado = models.DateField(
        null=True,
        blank=True,
        help_text='Último día que el empleado trabajó efectivamente'
    )

    # Foto
    foto = models.ImageField(upload_to='empleados/fotos/', blank=True, null=True)

    class Meta:
        db_table = 'empleados'
        ordering = ['apellido_paterno', 'apellido_materno', 'nombre']

    def __str__(self):
        return self.nombre_completo
    
    @property
    def nombre_completo(self):
        partes = [self.nombre, self.apellido_paterno, self.apellido_materno]
        return ' '.join(filter(None, partes))
    
    @property
    def antiguedad(self):
        """Retorna diccionario con años, meses, días de antigüedad"""
        fecha_fin = self.fecha_baja or timezone.now().date()
        delta = relativedelta(fecha_fin, self.fecha_ingreso)
        return {
            'anos': delta.years,
            'meses': delta.months,
            'dias': delta.days,
            'total_dias': (fecha_fin - self.fecha_ingreso).days
        }
    
    @property
    def anos_completos(self):
        return self.antiguedad['anos']
    
    @property
    def proximo_aniversario(self):
        hoy = timezone.now().date()
        aniversario = self.fecha_ingreso.replace(year=hoy.year)
        if aniversario <= hoy:
            aniversario = aniversario.replace(year=hoy.year + 1)
        return aniversario
    
    @property
    def salario_mensual(self):
        if self.salario_diario:
            return self.salario_diario * 30
        return None
    
# ============ PROPIEDADES DE ESTRUCTURA ORGANIZACIONAL ============
    
    @property
    def es_jefe(self) -> bool:
        """Indica si el empleado tiene subordinados directos"""
        return self.subordinados.filter(estado='activo').exists()
    
    @property
    def nivel_jerarquico(self) -> int:
        """Calcula el nivel jerárquico (1=CEO, 2=Reporta a CEO, etc.)"""
        nivel = 1
        actual = self.jefe_directo
        while actual:
            nivel += 1
            actual = actual.jefe_directo
            if nivel > 10:
                break
        return nivel
    
    @property
    def total_subordinados(self) -> int:
        """Total de subordinados directos activos"""
        return self.subordinados.filter(estado='activo').count()
    
    def es_jefe_de(self, empleado) -> bool:
        """Verifica si es jefe directo o indirecto de otro empleado"""
        actual = empleado.jefe_directo
        while actual:
            if actual.id == self.id:
                return True
            actual = actual.jefe_directo
        return False


class DocumentoEmpleado(BaseModel):
    """Documento del expediente de un empleado"""

    class TipoDocumento(models.TextChoices):
        # Personales
        INE = 'ine', 'INE/IFE'
        CURP = 'curp', 'CURP'
        RFC = 'rfc', 'Constancia RFC'
        COMPROBANTE_DOMICILIO = 'comprobante_domicilio', 'Comprobante de Domicilio'
        ACTA_NACIMIENTO = 'acta_nacimiento', 'Acta de Nacimiento'
        NSS = 'nss', 'Número de Seguro Social'
        FOTO = 'foto', 'Fotografía'

        # Laborales
        CONTRATO = 'contrato', 'Contrato Laboral'
        ALTA_IMSS = 'alta_imss', 'Alta IMSS'
        MODIFICACION_SALARIO = 'mod_salario', 'Modificación de Salario IMSS'
        CARTA_RENUNCIA = 'carta_renuncia', 'Carta de Renuncia'
        CARTA_DESPIDO = 'carta_despido', 'Carta de Despido'
        FINIQUITO = 'finiquito', 'Finiquito'
        CONSTANCIA_LABORAL = 'constancia', 'Constancia Laboral'

        # Incidencias
        INCAPACIDAD_IMSS = 'incapacidad', 'Incapacidad IMSS'
        PERMISO = 'permiso', 'Permiso/Justificante'
        ACTA_ADMINISTRATIVA = 'acta_admin', 'Acta Administrativa'

        # Nómina
        RECIBO_NOMINA = 'recibo', 'Recibo de Nómina'
        CFDI = 'cfdi', 'CFDI Nómina'

        # Otros
        EVALUACION = 'evaluacion', 'Evaluación de Desempeño'
        CAPACITACION = 'capacitacion', 'Constancia de Capacitación'
        OTRO = 'otro', 'Otro'

    class Estatus(models.TextChoices):
        PENDIENTE = 'pendiente', 'Pendiente de Revisión'
        APROBADO = 'aprobado', 'Aprobado'
        RECHAZADO = 'rechazado', 'Rechazado'
        VENCIDO = 'vencido', 'Vencido'

    empleado = models.ForeignKey(
        'Empleado', on_delete=models.CASCADE, related_name='expediente'
    )

    tipo = models.CharField(max_length=30, choices=TipoDocumento.choices)
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True)

    archivo = models.FileField(upload_to='expedientes/%Y/%m/')
    tipo_archivo = models.CharField(max_length=20)  # pdf, jpg, png, docx
    tamaño_bytes = models.PositiveIntegerField(default=0)

    # Contenido extraído (para búsqueda y que la IA lo lea)
    contenido_texto = models.TextField(blank=True)

    # Metadatos específicos
    fecha_documento = models.DateField(null=True, blank=True)
    fecha_vencimiento = models.DateField(null=True, blank=True)
    folio = models.CharField(max_length=50, blank=True)  # Folio IMSS, etc.

    # Estado
    estatus = models.CharField(
        max_length=20, choices=Estatus.choices, default=Estatus.PENDIENTE
    )
    revisado_por = models.ForeignKey(
        'usuarios.Usuario', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='documentos_revisados'
    )
    fecha_revision = models.DateTimeField(null=True, blank=True)
    notas_revision = models.TextField(blank=True)

    # Vinculación con otros registros
    incidencia = models.ForeignKey(
        'nomina.IncidenciaNomina', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='documentos_soporte'
    )
    recibo_nomina = models.ForeignKey(
        'nomina.ReciboNomina', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='documentos_soporte'
    )

    # Subido desde chat
    mensaje_chat = models.ForeignKey(
        'chat.Mensaje', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='documentos_adjuntos'
    )

    class Meta:
        db_table = 'empleados_documentos'
        ordering = ['-created_at']
        verbose_name = 'Documento de Expediente'
        verbose_name_plural = 'Documentos de Expediente'

    def __str__(self):
        return f"{self.empleado.nombre_completo} - {self.get_tipo_display()}"

    @property
    def esta_vencido(self):
        """Verifica si el documento está vencido"""
        if self.fecha_vencimiento:
            return self.fecha_vencimiento < timezone.now().date()
        return False

    @property
    def dias_para_vencer(self):
        """Días restantes para vencimiento"""
        if self.fecha_vencimiento:
            return (self.fecha_vencimiento - timezone.now().date()).days
        return None