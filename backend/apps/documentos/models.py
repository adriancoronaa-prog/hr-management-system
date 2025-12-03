from django.db import models
from django.core.validators import FileExtensionValidator
from apps.core.models import BaseModel, AuditMixin


class TipoDocumento(models.TextChoices):
    """Tipos de documentos para RAG"""
    POLITICA = 'politica', 'Política'
    REGLAMENTO = 'reglamento', 'Reglamento'
    MANUAL = 'manual', 'Manual'
    PROCEDIMIENTO = 'procedimiento', 'Procedimiento'
    FORMATO = 'formato', 'Formato'
    CONTRATO_PLANTILLA = 'contrato_plantilla', 'Plantilla de Contrato'
    COMUNICADO = 'comunicado', 'Comunicado'
    OTRO = 'otro', 'Otro'


class NivelAcceso(models.TextChoices):
    """Niveles de acceso para documentos"""
    PUBLICO = 'publico', 'Público (todos)'
    EMPRESA = 'empresa', 'Empresa (empleados de la empresa)'
    RRHH = 'rrhh', 'Solo RRHH/Admin'
    PRIVADO = 'privado', 'Privado (solo quien subió)'


class CategoriaDocumento(BaseModel):
    """Categorías de documentos configurables"""
    
    empresa = models.ForeignKey(
        'empresas.Empresa',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='categorias_documento'
    )  # NULL = categoría global
    
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    requiere_vencimiento = models.BooleanField(default=False)
    es_obligatorio = models.BooleanField(default=False)
    activo = models.BooleanField(default=True)
    orden = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'categorias_documento'
        ordering = ['orden', 'nombre']

    def __str__(self):
        return self.nombre


class DocumentoEmpleado(BaseModel, AuditMixin):
    """Documentos del expediente del empleado"""
    
    empleado = models.ForeignKey(
        'empleados.Empleado',
        on_delete=models.CASCADE,
        related_name='documentos'
    )
    categoria = models.ForeignKey(
        CategoriaDocumento,
        on_delete=models.SET_NULL,
        null=True,
        related_name='documentos'
    )
    
    nombre = models.CharField(max_length=255)
    archivo = models.FileField(upload_to='documentos/%Y/%m/')
    tipo_mime = models.CharField(max_length=100, blank=True)
    tamaño_bytes = models.PositiveBigIntegerField(default=0)
    
    fecha_vencimiento = models.DateField(null=True, blank=True)
    notas = models.TextField(blank=True)
    
    # Versionado
    version = models.PositiveIntegerField(default=1)
    documento_padre = models.ForeignKey(
        'self', on_delete=models.SET_NULL, null=True, blank=True, related_name='versiones'
    )
    
    activo = models.BooleanField(default=True)

    class Meta:
        db_table = 'documentos_empleado'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.empleado} - {self.nombre}"


# ============ MODELOS PARA RAG (Documentos de empresa) ============

class Documento(BaseModel, AuditMixin):
    """
    Documentos de empresa para búsqueda RAG.
    Políticas, reglamentos, manuales, etc. que la IA puede consultar.
    """

    empresa = models.ForeignKey(
        'empresas.Empresa',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='documentos_rag'
    )  # NULL = documento global (todas las empresas)

    # Metadatos
    titulo = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True)
    tipo = models.CharField(
        max_length=30,
        choices=TipoDocumento.choices,
        default=TipoDocumento.OTRO
    )

    # Archivo
    archivo = models.FileField(
        upload_to='documentos_rag/%Y/%m/',
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'docx', 'doc', 'txt'])]
    )
    tipo_mime = models.CharField(max_length=100, blank=True)
    tamaño_bytes = models.PositiveBigIntegerField(default=0)

    # Contenido extraído
    contenido_texto = models.TextField(blank=True, help_text='Texto extraído del documento')

    # Control de acceso
    tipo_acceso = models.CharField(
        max_length=20,
        choices=NivelAcceso.choices,
        default=NivelAcceso.EMPRESA
    )

    # Estado de procesamiento
    procesado = models.BooleanField(default=False)
    fecha_procesado = models.DateTimeField(null=True, blank=True)
    error_procesamiento = models.TextField(blank=True)

    # Metadatos adicionales
    version = models.CharField(max_length=20, blank=True, help_text='Ej: v1.0, 2024-01')
    fecha_vigencia = models.DateField(null=True, blank=True)
    tags = models.CharField(max_length=500, blank=True, help_text='Tags separados por coma')

    activo = models.BooleanField(default=True)

    class Meta:
        db_table = 'documentos_rag'
        ordering = ['-created_at']
        verbose_name = 'Documento RAG'
        verbose_name_plural = 'Documentos RAG'

    def __str__(self):
        return self.titulo

    @property
    def esta_procesado(self):
        """Indica si el documento fue procesado correctamente"""
        return self.procesado and not self.error_procesamiento

    @property
    def total_fragmentos(self):
        """Número de fragmentos generados"""
        return self.fragmentos.count()

    def puede_ver(self, usuario) -> bool:
        """
        Verifica si un usuario puede ver este documento.

        Los documentos RAG son para uso interno de RRHH. Los empleados
        no acceden directamente - la IA busca y les da la información.

        Solo Admin y RRHH pueden ver/gestionar documentos.
        """
        # Solo Admin y RRHH pueden ver documentos RAG
        if usuario.rol not in ['administrador', 'empleador']:
            return False

        # Verificar acceso a la empresa del documento
        if self.empresa is None:
            # Documento global - solo super admin
            return usuario.rol == 'administrador'

        # RRHH solo ve documentos de sus empresas asignadas
        return self.empresa in usuario.empresas.all()


class FragmentoDocumento(BaseModel):
    """
    Fragmento de texto de un documento para búsqueda semántica.
    Cada documento se divide en fragmentos para generar embeddings.
    """

    documento = models.ForeignKey(
        Documento,
        on_delete=models.CASCADE,
        related_name='fragmentos'
    )

    # Contenido del fragmento
    contenido = models.TextField()

    # Posición en el documento
    numero_fragmento = models.PositiveIntegerField(default=0)
    pagina = models.PositiveIntegerField(null=True, blank=True)

    # Embedding como JSON (lista de floats)
    embedding = models.JSONField(null=True, blank=True, help_text='Vector embedding del fragmento')

    # Metadatos
    num_tokens = models.PositiveIntegerField(default=0)
    num_caracteres = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'fragmentos_documento'
        ordering = ['documento', 'numero_fragmento']
        verbose_name = 'Fragmento de Documento'
        verbose_name_plural = 'Fragmentos de Documentos'

    def __str__(self):
        return f"{self.documento.titulo} - Fragmento {self.numero_fragmento}"

    @property
    def preview(self):
        """Vista previa del contenido (primeros 100 caracteres)"""
        if len(self.contenido) > 100:
            return self.contenido[:100] + "..."
        return self.contenido
