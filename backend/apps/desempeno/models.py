"""
Modelos para KPIs y Evaluaciones de Desempeño
"""
from django.db import models
from django.utils import timezone
from apps.core.models import BaseModel, AuditMixin


class CatalogoKPI(BaseModel, AuditMixin):
    """
    Catálogo de KPIs disponibles para asignar.
    Pueden ser globales o específicos de una empresa.
    """
    
    class TipoMedicion(models.TextChoices):
        NUMERO = 'numero', 'Número'
        PORCENTAJE = 'porcentaje', 'Porcentaje'
        MONEDA = 'moneda', 'Moneda'
        BOOLEAN = 'boolean', 'Sí/No'
        ESCALA = 'escala', 'Escala (1-10)'
    
    class Frecuencia(models.TextChoices):
        SEMANAL = 'semanal', 'Semanal'
        QUINCENAL = 'quincenal', 'Quincenal'
        MENSUAL = 'mensual', 'Mensual'
        TRIMESTRAL = 'trimestral', 'Trimestral'
        SEMESTRAL = 'semestral', 'Semestral'
        ANUAL = 'anual', 'Anual'
    
    class Categoria(models.TextChoices):
        VENTAS = 'ventas', 'Ventas'
        PRODUCTIVIDAD = 'productividad', 'Productividad'
        CALIDAD = 'calidad', 'Calidad'
        SERVICIO = 'servicio', 'Servicio al Cliente'
        FINANCIERO = 'financiero', 'Financiero'
        OPERATIVO = 'operativo', 'Operativo'
        DESARROLLO = 'desarrollo', 'Desarrollo Personal'
        OTRO = 'otro', 'Otro'
    
    # Relaciones
    empresa = models.ForeignKey(
        'empresas.Empresa', on_delete=models.CASCADE,
        null=True, blank=True, related_name='catalogo_kpis',
        help_text='Si es nulo, es un KPI global disponible para todas las empresas'
    )
    creado_por = models.ForeignKey(
        'usuarios.Usuario', on_delete=models.SET_NULL,
        null=True, related_name='kpis_creados'
    )
    
    # Datos del KPI
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    categoria = models.CharField(max_length=20, choices=Categoria.choices, default=Categoria.OTRO)
    tipo_medicion = models.CharField(max_length=20, choices=TipoMedicion.choices)
    unidad = models.CharField(max_length=50, blank=True, help_text='Ej: pesos, unidades, %, etc.')
    frecuencia = models.CharField(max_length=20, choices=Frecuencia.choices, default=Frecuencia.MENSUAL)
    
    # Valores de referencia
    valor_minimo = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    valor_objetivo = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    valor_excelente = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    
    # Configuración
    es_mayor_mejor = models.BooleanField(default=True, help_text='Si es True, mayor valor = mejor desempeño')
    activo = models.BooleanField(default=True)
    
    # Puestos a los que aplica (opcional)
    aplica_a_puestos = models.JSONField(default=list, blank=True, help_text='Lista de puestos a los que aplica')
    aplica_a_departamentos = models.JSONField(default=list, blank=True)

    class Meta:
        db_table = 'desempeno_catalogo_kpis'
        ordering = ['categoria', 'nombre']
        verbose_name = 'KPI del Catálogo'
        verbose_name_plural = 'Catálogo de KPIs'

    def __str__(self):
        return f"{self.nombre} ({self.get_tipo_medicion_display()})"


class AsignacionKPI(BaseModel, AuditMixin):
    """
    KPI asignado a un empleado específico con meta y periodo.
    """
    
    class Estado(models.TextChoices):
        BORRADOR = 'borrador', 'Borrador'
        ACTIVO = 'activo', 'Activo'
        PENDIENTE_APROBACION = 'pendiente', 'Pendiente de Aprobación'
        EVALUADO = 'evaluado', 'Evaluado'
        CANCELADO = 'cancelado', 'Cancelado'
    
    # Relaciones
    empleado = models.ForeignKey(
        'empleados.Empleado', on_delete=models.CASCADE, related_name='kpis_asignados'
    )
    kpi_catalogo = models.ForeignKey(
        CatalogoKPI, on_delete=models.PROTECT, related_name='asignaciones',
        null=True, blank=True, help_text='Opcional si es KPI personalizado'
    )
    asignado_por = models.ForeignKey(
        'empleados.Empleado', on_delete=models.SET_NULL,
        null=True, related_name='kpis_asignados_a_otros'
    )
    
    # Si no viene del catálogo, datos personalizados
    nombre_personalizado = models.CharField(max_length=200, blank=True)
    descripcion_personalizada = models.TextField(blank=True)
    tipo_medicion = models.CharField(max_length=20, choices=CatalogoKPI.TipoMedicion.choices, blank=True)
    unidad = models.CharField(max_length=50, blank=True)
    
    # Periodo
    periodo = models.CharField(max_length=20, help_text='Ej: 2024-Q4, 2024-12, 2024')
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    
    # Meta
    meta = models.DecimalField(max_digits=15, decimal_places=2)
    peso = models.DecimalField(max_digits=5, decimal_places=2, default=100, 
                               help_text='Peso porcentual en la evaluación total (0-100)')
    es_mayor_mejor = models.BooleanField(default=True)
    
    # Estado y resultado
    estado = models.CharField(max_length=20, choices=Estado.choices, default=Estado.ACTIVO)
    valor_logrado = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    porcentaje_cumplimiento = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    # Cambios pendientes (cuando empleado solicita modificación)
    cambios_pendientes = models.JSONField(null=True, blank=True, 
        help_text='Cambios propuestos por el empleado pendientes de aprobación')
    fecha_solicitud_cambio = models.DateTimeField(null=True, blank=True)
    motivo_cambio = models.TextField(blank=True)

    class Meta:
        db_table = 'desempeno_asignacion_kpis'
        ordering = ['-fecha_inicio', 'empleado']
        verbose_name = 'KPI Asignado'
        verbose_name_plural = 'KPIs Asignados'

    def __str__(self):
        nombre = self.nombre_personalizado or (self.kpi_catalogo.nombre if self.kpi_catalogo else 'KPI')
        return f"{nombre} - {self.empleado.nombre_completo} ({self.periodo})"
    
    @property
    def nombre_kpi(self):
        return self.nombre_personalizado or (self.kpi_catalogo.nombre if self.kpi_catalogo else 'Sin nombre')
    
    def calcular_cumplimiento(self):
        """Calcula el porcentaje de cumplimiento"""
        if self.valor_logrado is None or self.meta == 0:
            return None
        
        if self.es_mayor_mejor:
            porcentaje = (self.valor_logrado / self.meta) * 100
        else:
            # Para métricas donde menor es mejor (ej: tiempo de respuesta)
            porcentaje = (self.meta / self.valor_logrado) * 100 if self.valor_logrado > 0 else 0
        
        return min(porcentaje, 150)  # Tope en 150%
    
    def actualizar_valor(self, nuevo_valor):
        """Actualiza el valor logrado y recalcula cumplimiento"""
        from decimal import Decimal
        self.valor_logrado = Decimal(str(nuevo_valor))
        self.porcentaje_cumplimiento = self.calcular_cumplimiento()
        self.save()


class RegistroAvanceKPI(BaseModel):
    """
    Registro de avances en un KPI (histórico de valores).
    """
    asignacion = models.ForeignKey(
        AsignacionKPI, on_delete=models.CASCADE, related_name='avances'
    )
    registrado_por = models.ForeignKey(
        'empleados.Empleado', on_delete=models.SET_NULL, null=True
    )
    
    fecha = models.DateField(default=timezone.now)
    valor = models.DecimalField(max_digits=15, decimal_places=2)
    valor_anterior = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    comentarios = models.TextField(blank=True)
    evidencia = models.FileField(upload_to='desempeno/evidencias/', blank=True, null=True)

    class Meta:
        db_table = 'desempeno_registro_avances'
        ordering = ['-fecha', '-created_at']
        verbose_name = 'Registro de Avance'
        verbose_name_plural = 'Registros de Avance'

    def __str__(self):
        return f"{self.asignacion.nombre_kpi}: {self.valor} ({self.fecha})"


class Evaluacion(BaseModel, AuditMixin):
    """
    Evaluación de desempeño de un empleado para un periodo.
    """
    
    class Estado(models.TextChoices):
        BORRADOR = 'borrador', 'Borrador'
        EN_PROGRESO = 'en_progreso', 'En Progreso'
        PENDIENTE_REVISION = 'pendiente_revision', 'Pendiente de Revisión'
        COMPLETADA = 'completada', 'Completada'
        CERRADA = 'cerrada', 'Cerrada'
    
    class TipoEvaluacion(models.TextChoices):
        MENSUAL = 'mensual', 'Mensual'
        TRIMESTRAL = 'trimestral', 'Trimestral'
        SEMESTRAL = 'semestral', 'Semestral'
        ANUAL = 'anual', 'Anual'
        PERIODO_PRUEBA = 'prueba', 'Periodo de Prueba'
    
    # Relaciones
    empleado = models.ForeignKey(
        'empleados.Empleado', on_delete=models.CASCADE, related_name='evaluaciones'
    )
    evaluador = models.ForeignKey(
        'empleados.Empleado', on_delete=models.SET_NULL, 
        null=True, related_name='evaluaciones_realizadas'
    )
    
    # Periodo
    tipo = models.CharField(max_length=20, choices=TipoEvaluacion.choices)
    periodo = models.CharField(max_length=20, help_text='Ej: 2024-Q4, 2024')
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    
    # Puntuaciones
    puntuacion_kpis = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True,
                                          help_text='Promedio ponderado de KPIs (0-100)')
    puntuacion_competencias = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True,
                                                  help_text='Evaluación de competencias (0-100)')
    puntuacion_final = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    # Retroalimentación
    logros = models.TextField(blank=True, help_text='Principales logros del periodo')
    areas_mejora = models.TextField(blank=True, help_text='Áreas de oportunidad')
    retroalimentacion_evaluador = models.TextField(blank=True)
    retroalimentacion_empleado = models.TextField(blank=True)
    plan_desarrollo = models.TextField(blank=True, help_text='Plan de desarrollo para siguiente periodo')
    
    # Objetivos siguiente periodo
    objetivos_siguientes = models.JSONField(default=list, blank=True)
    
    # Estado
    estado = models.CharField(max_length=20, choices=Estado.choices, default=Estado.BORRADOR)
    fecha_envio = models.DateTimeField(null=True, blank=True)
    fecha_aceptacion = models.DateTimeField(null=True, blank=True)

    # Firmas
    firmado_evaluador = models.BooleanField(default=False)
    firmado_empleado = models.BooleanField(default=False)
    fecha_firma_evaluador = models.DateTimeField(null=True, blank=True)
    fecha_firma_empleado = models.DateTimeField(null=True, blank=True)

    # Tipo de evaluación (90, 180, 360)
    modalidad = models.CharField(max_length=20, default='90',
        help_text='90=solo jefe, 180=jefe+auto, 360=todos')
    incluye_autoevaluacion = models.BooleanField(default=False)
    incluye_pares = models.BooleanField(default=False)
    incluye_subordinados = models.BooleanField(default=False)

    # Autoevaluación
    autoevaluacion_puntuacion = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True)
    autoevaluacion_comentarios = models.TextField(blank=True)
    autoevaluacion_fecha = models.DateTimeField(null=True, blank=True)

    # Clasificación 9-Box (Matriz de Talento)
    clasificacion_desempeno = models.CharField(max_length=10, blank=True,
        help_text='bajo/medio/alto')
    clasificacion_potencial = models.CharField(max_length=10, blank=True,
        help_text='bajo/medio/alto')

    # Comparativa
    ranking_departamento = models.PositiveIntegerField(null=True, blank=True)
    percentil = models.PositiveSmallIntegerField(null=True, blank=True)

    class Meta:
        db_table = 'desempeno_evaluaciones'
        ordering = ['-fecha_fin', 'empleado']
        verbose_name = 'Evaluación de Desempeño'
        verbose_name_plural = 'Evaluaciones de Desempeño'
        unique_together = ['empleado', 'tipo', 'periodo']

    def __str__(self):
        return f"Evaluación {self.periodo} - {self.empleado.nombre_completo}"
    
    def calcular_puntuacion_kpis(self):
        """Calcula la puntuación promedio ponderada de los KPIs"""
        from django.db.models import Sum
        
        kpis = AsignacionKPI.objects.filter(
            empleado=self.empleado,
            periodo=self.periodo,
            estado__in=['activo', 'evaluado']
        )
        
        if not kpis.exists():
            return None
        
        total_peso = kpis.aggregate(total=Sum('peso'))['total'] or 0
        if total_peso == 0:
            return None
        
        suma_ponderada = sum(
            (kpi.porcentaje_cumplimiento or 0) * float(kpi.peso)
            for kpi in kpis
        )
        
        return round(suma_ponderada / float(total_peso), 2)
    
    def calcular_puntuacion_final(self, peso_kpis=70, peso_competencias=30):
        """Calcula la puntuación final combinando KPIs y competencias"""
        if self.puntuacion_kpis is None:
            return self.puntuacion_competencias

        if self.puntuacion_competencias is None:
            return self.puntuacion_kpis

        return round(
            (float(self.puntuacion_kpis) * peso_kpis / 100) +
            (float(self.puntuacion_competencias) * peso_competencias / 100),
            2
        )

    @property
    def clasificacion_9box(self):
        """Retorna la clasificación 9-box"""
        if not self.clasificacion_desempeno or not self.clasificacion_potencial:
            return None

        matriz = {
            ('alto', 'alto'): 'Estrella',
            ('alto', 'medio'): 'Alto Desempeno',
            ('alto', 'bajo'): 'Experto Tecnico',
            ('medio', 'alto'): 'Futuro Lider',
            ('medio', 'medio'): 'Colaborador Clave',
            ('medio', 'bajo'): 'Efectivo',
            ('bajo', 'alto'): 'Enigma',
            ('bajo', 'medio'): 'En Desarrollo',
            ('bajo', 'bajo'): 'Accion Requerida',
        }
        return matriz.get((self.clasificacion_desempeno, self.clasificacion_potencial))

    def calcular_promedio_competencias(self):
        """Calcula el promedio de competencias evaluadas"""
        competencias = self.competencias_evaluadas.filter(nivel_obtenido__isnull=False)
        if not competencias.exists():
            return None

        total = sum(c.nivel_obtenido for c in competencias)
        promedio = (total / competencias.count()) * 20  # Convertir 1-5 a 0-100
        return round(promedio, 2)

    def obtener_brechas_competencias(self):
        """Retorna competencias con brecha negativa (a mejorar)"""
        return self.competencias_evaluadas.filter(
            nivel_obtenido__isnull=False,
            nivel_obtenido__lt=models.F('nivel_esperado')
        ).select_related('competencia')


# ============================================================
# CATÁLOGO DE COMPETENCIAS
# ============================================================

class CatalogoCompetencia(BaseModel, AuditMixin):
    """Catalogo de competencias evaluables"""

    class Categoria(models.TextChoices):
        LIDERAZGO = 'liderazgo', 'Liderazgo'
        COMUNICACION = 'comunicacion', 'Comunicacion'
        TRABAJO_EQUIPO = 'trabajo_equipo', 'Trabajo en Equipo'
        ORIENTACION_RESULTADOS = 'resultados', 'Orientacion a Resultados'
        INNOVACION = 'innovacion', 'Innovacion y Creatividad'
        ADAPTABILIDAD = 'adaptabilidad', 'Adaptabilidad'
        TECNICA = 'tecnica', 'Competencia Tecnica'
        SERVICIO = 'servicio', 'Servicio al Cliente'
        ETICA = 'etica', 'Etica e Integridad'
        OTRO = 'otro', 'Otro'

    empresa = models.ForeignKey(
        'empresas.Empresa', on_delete=models.CASCADE,
        null=True, blank=True, related_name='catalogo_competencias',
        help_text='Si es nulo, es global'
    )

    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    categoria = models.CharField(max_length=20, choices=Categoria.choices)

    # Niveles de dominio con descripciones
    nivel_1_descripcion = models.TextField(blank=True, help_text='Basico/En desarrollo')
    nivel_2_descripcion = models.TextField(blank=True, help_text='Competente')
    nivel_3_descripcion = models.TextField(blank=True, help_text='Avanzado')
    nivel_4_descripcion = models.TextField(blank=True, help_text='Experto')
    nivel_5_descripcion = models.TextField(blank=True, help_text='Referente/Mentor')

    # A quien aplica
    aplica_a_puestos = models.JSONField(default=list, blank=True)
    aplica_a_niveles = models.JSONField(default=list, blank=True, help_text='Niveles jerarquicos')
    es_obligatoria = models.BooleanField(default=False)
    activo = models.BooleanField(default=True)

    class Meta:
        db_table = 'desempeno_catalogo_competencias'
        ordering = ['categoria', 'nombre']
        verbose_name = 'Competencia'
        verbose_name_plural = 'Catalogo de Competencias'

    def __str__(self):
        return f"{self.nombre} ({self.get_categoria_display()})"


class EvaluacionCompetencia(BaseModel):
    """Evaluacion de una competencia especifica dentro de una evaluacion"""

    evaluacion = models.ForeignKey(
        Evaluacion, on_delete=models.CASCADE, related_name='competencias_evaluadas'
    )
    competencia = models.ForeignKey(
        CatalogoCompetencia, on_delete=models.PROTECT, related_name='evaluaciones'
    )

    # Calificacion 1-5
    nivel_esperado = models.PositiveSmallIntegerField(default=3, help_text='Nivel esperado 1-5')
    nivel_obtenido = models.PositiveSmallIntegerField(null=True, blank=True, help_text='Nivel logrado 1-5')

    comentarios = models.TextField(blank=True)
    ejemplos_conducta = models.TextField(blank=True, help_text='Ejemplos observados')

    # Para evaluacion 360
    evaluador_tipo = models.CharField(max_length=20, blank=True,
        help_text='jefe/par/subordinado/autoevaluacion')
    evaluador = models.ForeignKey(
        'empleados.Empleado', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='competencias_evaluadas_a_otros'
    )

    class Meta:
        db_table = 'desempeno_evaluacion_competencias'
        verbose_name = 'Evaluacion de Competencia'
        verbose_name_plural = 'Evaluaciones de Competencias'

    def __str__(self):
        return f"{self.competencia.nombre}: {self.nivel_obtenido or 'Pendiente'}"

    @property
    def brecha(self):
        """Diferencia entre nivel esperado y obtenido"""
        if self.nivel_obtenido is None:
            return None
        return self.nivel_obtenido - self.nivel_esperado


class RetroalimentacionContinua(BaseModel):
    """Feedback continuo fuera de evaluaciones formales"""

    class Tipo(models.TextChoices):
        RECONOCIMIENTO = 'reconocimiento', 'Reconocimiento'
        MEJORA = 'mejora', 'Area de Mejora'
        COACHING = 'coaching', 'Coaching'
        OBJETIVO = 'objetivo', 'Seguimiento de Objetivo'
        GENERAL = 'general', 'General'

    empleado = models.ForeignKey(
        'empleados.Empleado', on_delete=models.CASCADE, related_name='retroalimentaciones'
    )
    autor = models.ForeignKey(
        'empleados.Empleado', on_delete=models.SET_NULL, null=True,
        related_name='retroalimentaciones_dadas'
    )

    tipo = models.CharField(max_length=20, choices=Tipo.choices)
    contenido = models.TextField()
    es_privado = models.BooleanField(default=False, help_text='Solo visible para RRHH y jefe')

    # Puede vincularse a una competencia o KPI
    competencia = models.ForeignKey(
        CatalogoCompetencia, on_delete=models.SET_NULL, null=True, blank=True
    )
    kpi = models.ForeignKey(
        AsignacionKPI, on_delete=models.SET_NULL, null=True, blank=True
    )

    # Seguimiento
    requiere_seguimiento = models.BooleanField(default=False)
    seguimiento_completado = models.BooleanField(default=False)
    fecha_seguimiento = models.DateField(null=True, blank=True)

    class Meta:
        db_table = 'desempeno_retroalimentacion'
        ordering = ['-created_at']
        verbose_name = 'Retroalimentacion'
        verbose_name_plural = 'Retroalimentaciones'

    def __str__(self):
        return f"{self.get_tipo_display()} para {self.empleado.nombre_completo}"
