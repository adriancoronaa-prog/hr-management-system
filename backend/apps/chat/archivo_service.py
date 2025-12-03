"""
Servicio para procesar archivos adjuntos en el chat
"""
import os
import base64
from pathlib import Path
from typing import Dict, Optional, Tuple
from django.core.files.uploadedfile import UploadedFile


# Tipos de imagen soportados por Claude Vision
TIPOS_IMAGEN = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
EXTENSIONES_IMAGEN = ['.jpg', '.jpeg', '.png', '.gif', '.webp']


class ProcesadorArchivoChat:
    """Procesa archivos subidos en el chat"""

    TIPOS_PERMITIDOS = {
        'pdf': ['application/pdf'],
        'jpg': ['image/jpeg'],
        'jpeg': ['image/jpeg'],
        'png': ['image/png'],
        'gif': ['image/gif'],
        'webp': ['image/webp'],
        'docx': ['application/vnd.openxmlformats-officedocument.wordprocessingml.document'],
        'doc': ['application/msword'],
        'txt': ['text/plain'],
        'csv': ['text/csv'],
    }

    MAX_SIZE_MB = 10

    @classmethod
    def validar_archivo(cls, archivo: UploadedFile) -> Tuple[bool, str]:
        """Valida tipo y tamaño del archivo"""
        # Validar tamaño
        max_bytes = cls.MAX_SIZE_MB * 1024 * 1024
        if archivo.size > max_bytes:
            return False, f"Archivo muy grande. Máximo: {cls.MAX_SIZE_MB}MB"

        # Validar tipo por extensión
        nombre = archivo.name.lower()
        extension = nombre.split('.')[-1] if '.' in nombre else ''

        if extension not in cls.TIPOS_PERMITIDOS:
            tipos = ', '.join(cls.TIPOS_PERMITIDOS.keys())
            return False, f"Tipo no permitido. Usa: {tipos}"

        return True, "OK"

    @classmethod
    def extraer_texto(cls, archivo_path: str, tipo: str) -> str:
        """Extrae texto del archivo para que la IA lo lea"""
        try:
            from apps.documentos.services import ExtractorTexto
            return ExtractorTexto.extraer(archivo_path, tipo)
        except ImportError:
            # Si no está disponible el extractor, intentar básico
            return cls._extraer_texto_basico(archivo_path, tipo)
        except Exception as e:
            print(f"Error extrayendo texto: {e}")
            return ""

    @classmethod
    def _extraer_texto_basico(cls, archivo_path: str, tipo: str) -> str:
        """Extracción básica de texto"""
        try:
            if tipo == 'txt':
                with open(archivo_path, 'r', encoding='utf-8', errors='replace') as f:
                    return f.read()

            elif tipo == 'pdf':
                try:
                    from PyPDF2 import PdfReader
                    reader = PdfReader(archivo_path)
                    texto = []
                    for page in reader.pages[:20]:  # Máximo 20 páginas
                        texto.append(page.extract_text() or '')
                    return '\n'.join(texto)
                except Exception:
                    return ""

            elif tipo in ['docx', 'doc']:
                try:
                    from docx import Document
                    doc = Document(archivo_path)
                    return '\n'.join([p.text for p in doc.paragraphs])
                except Exception:
                    return ""

        except Exception as e:
            print(f"Error en extracción básica: {e}")
            return ""

        return ""

    @classmethod
    def procesar(cls, archivo: UploadedFile) -> Dict:
        """Procesa archivo: valida, guarda, extrae texto"""
        # Validar
        valido, mensaje = cls.validar_archivo(archivo)
        if not valido:
            return {'success': False, 'error': mensaje}

        nombre = archivo.name
        extension = nombre.split('.')[-1].lower() if '.' in nombre else 'bin'

        # Determinar si es imagen
        es_imagen = extension in ['jpg', 'jpeg', 'png', 'gif', 'webp']

        return {
            'success': True,
            'nombre': nombre,
            'tipo': extension,
            'tamaño': archivo.size,
            'es_imagen': es_imagen,
            'content_type': getattr(archivo, 'content_type', None),
        }

    @classmethod
    def imagen_a_base64(cls, ruta_archivo: str) -> Tuple[str, str]:
        """
        Convierte una imagen a base64 para enviar a Claude Vision.
        Retorna (base64_string, media_type)
        """
        ruta = Path(ruta_archivo)

        # Determinar media type
        extension = ruta.suffix.lower()
        media_types = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.webp': 'image/webp',
        }
        media_type = media_types.get(extension, 'image/jpeg')

        # Leer y convertir a base64
        with open(ruta_archivo, 'rb') as f:
            imagen_bytes = f.read()

        base64_string = base64.b64encode(imagen_bytes).decode('utf-8')

        return base64_string, media_type

    @classmethod
    def imagen_bytes_a_base64(cls, archivo: UploadedFile) -> Tuple[str, str]:
        """
        Convierte imagen desde UploadedFile a base64.
        Retorna (base64_string, media_type)
        """
        # Determinar media type
        nombre = archivo.name.lower()
        extension = '.' + nombre.split('.')[-1] if '.' in nombre else '.jpg'

        media_types = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.webp': 'image/webp',
        }
        media_type = media_types.get(extension, 'image/jpeg')

        # Leer y convertir a base64
        archivo.seek(0)
        imagen_bytes = archivo.read()
        archivo.seek(0)  # Reset para uso posterior

        base64_string = base64.b64encode(imagen_bytes).decode('utf-8')

        return base64_string, media_type

    @classmethod
    def detectar_tipo_documento(cls, nombre_archivo: str, contenido: str, contexto_flujo: str = '') -> str:
        """Detecta automáticamente el tipo de documento basado en nombre y contenido"""
        nombre_lower = nombre_archivo.lower()
        contenido_lower = contenido.lower() if contenido else ''

        # Por nombre de archivo
        if 'renuncia' in nombre_lower:
            return 'carta_renuncia'
        elif 'despido' in nombre_lower:
            return 'carta_despido'
        elif 'incapacidad' in nombre_lower:
            return 'incapacidad'
        elif 'contrato' in nombre_lower:
            return 'contrato'
        elif 'ine' in nombre_lower or 'credencial' in nombre_lower:
            return 'ine'
        elif 'curp' in nombre_lower:
            return 'curp'
        elif 'rfc' in nombre_lower or 'constancia_sat' in nombre_lower:
            return 'rfc'
        elif 'comprobante' in nombre_lower or 'domicilio' in nombre_lower:
            return 'comprobante_domicilio'
        elif 'finiquito' in nombre_lower:
            return 'finiquito'
        elif 'permiso' in nombre_lower or 'justificante' in nombre_lower:
            return 'permiso'
        elif 'acta' in nombre_lower and 'nacimiento' in nombre_lower:
            return 'acta_nacimiento'
        elif 'nss' in nombre_lower or 'seguro_social' in nombre_lower:
            return 'nss'
        elif 'alta_imss' in nombre_lower:
            return 'alta_imss'
        elif 'recibo' in nombre_lower or 'nomina' in nombre_lower:
            return 'recibo'
        elif 'cfdi' in nombre_lower:
            return 'cfdi'
        elif 'evaluacion' in nombre_lower or 'desempeno' in nombre_lower:
            return 'evaluacion'
        elif 'capacitacion' in nombre_lower or 'certificado' in nombre_lower:
            return 'capacitacion'

        # Por contenido del documento
        if contenido_lower:
            if 'renuncia voluntaria' in contenido_lower or 'presento mi renuncia' in contenido_lower:
                return 'carta_renuncia'
            elif 'incapacidad temporal' in contenido_lower or 'instituto mexicano del seguro social' in contenido_lower:
                return 'incapacidad'
            elif 'contrato individual de trabajo' in contenido_lower:
                return 'contrato'
            elif 'finiquito' in contenido_lower and 'liquidación' in contenido_lower:
                return 'finiquito'
            elif 'clave única de registro de población' in contenido_lower:
                return 'curp'
            elif 'registro federal de contribuyentes' in contenido_lower:
                return 'rfc'

        # Por contexto del flujo activo
        if contexto_flujo:
            contexto_map = {
                'baja_empleado': 'carta_renuncia',
                'registrar_incidencia': 'permiso',
                'crear_empleado': 'otro',
                'incapacidad': 'incapacidad',
            }
            if contexto_flujo in contexto_map:
                return contexto_map[contexto_flujo]

        return 'otro'

    @classmethod
    def obtener_icono_tipo(cls, tipo: str) -> str:
        """Retorna emoji según tipo de documento"""
        iconos = {
            'ine': '🪪',
            'curp': '📋',
            'rfc': '📄',
            'comprobante_domicilio': '🏠',
            'acta_nacimiento': '📜',
            'nss': '🏥',
            'foto': '📷',
            'contrato': '📝',
            'alta_imss': '🏥',
            'mod_salario': '💰',
            'carta_renuncia': '✉️',
            'carta_despido': '📤',
            'finiquito': '💵',
            'constancia': '📃',
            'incapacidad': '🏥',
            'permiso': '📋',
            'acta_admin': '⚠️',
            'recibo': '🧾',
            'cfdi': '🧾',
            'evaluacion': '📊',
            'capacitacion': '🎓',
            'otro': '📎',
        }
        return iconos.get(tipo, '📎')
