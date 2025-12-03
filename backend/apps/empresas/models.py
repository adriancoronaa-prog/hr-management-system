from django.db import models
from apps.core.models import BaseModel, AuditMixin


class Empresa(BaseModel, AuditMixin):
    """Empresa registrada en el sistema"""
    
    # Datos fiscales
    rfc = models.CharField(max_length=13, unique=True)
    razon_social = models.CharField(max_length=255)
    nombre_comercial = models.CharField(max_length=255, blank=True)
    regimen_fiscal = models.CharField(max_length=100, blank=True)
    
    # Domicilio fiscal
    calle = models.CharField(max_length=255, blank=True)
    numero_exterior = models.CharField(max_length=20, blank=True)
    numero_interior = models.CharField(max_length=20, blank=True)
    colonia = models.CharField(max_length=100, blank=True)
    codigo_postal = models.CharField(max_length=5, blank=True)
    municipio = models.CharField(max_length=100, blank=True)
    estado = models.CharField(max_length=50, blank=True)
    
    # Contacto
    representante_legal = models.CharField(max_length=255, blank=True)
    telefono = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    
    # Config
    logo = models.ImageField(upload_to='empresas/logos/', blank=True, null=True)
    activa = models.BooleanField(default=True)

    class Meta:
        db_table = 'empresas'
        verbose_name = 'Empresa'
        verbose_name_plural = 'Empresas'
        ordering = ['razon_social']

    def __str__(self):
        return self.razon_social
    
    @property
    def direccion_completa(self):
        partes = filter(None, [
            f"{self.calle} {self.numero_exterior}".strip(),
            self.numero_interior and f"Int. {self.numero_interior}",
            self.colonia,
            self.codigo_postal and f"C.P. {self.codigo_postal}",
            self.municipio,
            self.estado
        ])
        return ', '.join(partes)
