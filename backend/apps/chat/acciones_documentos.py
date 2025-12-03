"""
Acciones IA para generacion de documentos Word
"""
import base64
from typing import Dict
from datetime import datetime


def accion_generar_constancia_laboral(usuario, params: Dict, contexto: Dict) -> Dict:
    """Genera constancia laboral en Word"""
    from apps.empleados.models import Empleado
    from .generador_documentos import GeneradorDocumentos

    empleado_id = params.get('empleado_id')
    incluir_salario = params.get('incluir_salario', False)

    # Si no se especifica, usar el empleado del usuario
    if not empleado_id:
        if hasattr(usuario, 'empleado') and usuario.empleado:
            empleado = usuario.empleado
        else:
            return {'success': False, 'error': 'Especifica el empleado para la constancia'}
    else:
        try:
            empleado = Empleado.objects.get(id=empleado_id)
        except Empleado.DoesNotExist:
            return {'success': False, 'error': 'Empleado no encontrado'}

    # Verificar permisos
    es_admin = usuario.rol == 'admin'
    es_rrhh = usuario.rol in ['empleador', 'rrhh']
    es_propio = hasattr(usuario, 'empleado') and usuario.empleado == empleado

    if not es_admin and not es_rrhh and not es_propio:
        return {'success': False, 'error': 'No tienes permiso para generar esta constancia'}

    try:
        buffer = GeneradorDocumentos.generar_constancia_laboral(empleado, incluir_salario)
        contenido_base64 = base64.b64encode(buffer.getvalue()).decode()

        return {
            'success': True,
            'mensaje': f'Constancia laboral generada para {empleado.nombre_completo}',
            'archivo': {
                'nombre': f'constancia_laboral_{empleado.apellido_paterno}_{empleado.nombre}.docx',
                'contenido_base64': contenido_base64,
                'tipo': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            }
        }
    except Exception as e:
        return {'success': False, 'error': f'Error generando documento: {str(e)}'}


def accion_generar_carta_recomendacion(usuario, params: Dict, contexto: Dict) -> Dict:
    """Genera carta de recomendacion en Word"""
    from apps.empleados.models import Empleado
    from .generador_documentos import GeneradorDocumentos

    empleado_id = params.get('empleado_id')
    empleado_nombre = params.get('empleado_nombre')
    destinatario = params.get('destinatario', 'A quien corresponda')

    # Buscar empleado por ID o nombre
    if empleado_id:
        try:
            empleado = Empleado.objects.get(id=empleado_id)
        except Empleado.DoesNotExist:
            return {'success': False, 'error': 'Empleado no encontrado'}
    elif empleado_nombre:
        empresa = contexto.get('empresa_contexto')
        qs = Empleado.objects.filter(estado='activo')
        if empresa:
            qs = qs.filter(empresa=empresa)
        empleado = qs.filter(nombre__icontains=empleado_nombre).first()
        if not empleado:
            return {'success': False, 'error': f'No se encontro empleado con nombre "{empleado_nombre}"'}
    else:
        return {'success': False, 'error': 'Especifica el empleado para la carta'}

    # Solo admin/rrhh
    es_admin = usuario.rol == 'admin'
    es_rrhh = usuario.rol in ['empleador', 'rrhh']

    if not es_admin and not es_rrhh:
        return {'success': False, 'error': 'Solo RRHH puede generar cartas de recomendacion'}

    try:
        buffer = GeneradorDocumentos.generar_carta_recomendacion(empleado, destinatario)
        contenido_base64 = base64.b64encode(buffer.getvalue()).decode()

        return {
            'success': True,
            'mensaje': f'Carta de recomendacion generada para {empleado.nombre_completo}',
            'archivo': {
                'nombre': f'carta_recomendacion_{empleado.apellido_paterno}_{empleado.nombre}.docx',
                'contenido_base64': contenido_base64,
                'tipo': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            }
        }
    except Exception as e:
        return {'success': False, 'error': f'Error generando documento: {str(e)}'}


def accion_generar_carta_amonestacion(usuario, params: Dict, contexto: Dict) -> Dict:
    """Genera carta de amonestacion en Word"""
    from apps.empleados.models import Empleado
    from .generador_documentos import GeneradorDocumentos

    empleado_id = params.get('empleado_id')
    empleado_nombre = params.get('empleado_nombre')
    motivo = params.get('motivo')
    fecha_incidente = params.get('fecha_incidente')

    # Buscar empleado
    if empleado_id:
        try:
            empleado = Empleado.objects.get(id=empleado_id)
        except Empleado.DoesNotExist:
            return {'success': False, 'error': 'Empleado no encontrado'}
    elif empleado_nombre:
        empresa = contexto.get('empresa_contexto')
        qs = Empleado.objects.filter(estado='activo')
        if empresa:
            qs = qs.filter(empresa=empresa)
        empleado = qs.filter(nombre__icontains=empleado_nombre).first()
        if not empleado:
            return {'success': False, 'error': f'No se encontro empleado con nombre "{empleado_nombre}"'}
    else:
        return {'success': False, 'error': 'Especifica el empleado'}

    if not motivo:
        return {'success': False, 'error': 'Especifica el motivo de la amonestacion'}

    es_admin = usuario.rol == 'admin'
    es_rrhh = usuario.rol in ['empleador', 'rrhh']

    if not es_admin and not es_rrhh:
        return {'success': False, 'error': 'Solo RRHH puede generar cartas de amonestacion'}

    fecha_inc = None
    if fecha_incidente:
        try:
            fecha_inc = datetime.strptime(fecha_incidente, '%Y-%m-%d').date()
        except:
            pass

    try:
        buffer = GeneradorDocumentos.generar_carta_amonestacion(empleado, motivo, fecha_inc)
        contenido_base64 = base64.b64encode(buffer.getvalue()).decode()

        return {
            'success': True,
            'mensaje': f'Carta de amonestacion generada para {empleado.nombre_completo}',
            'archivo': {
                'nombre': f'carta_amonestacion_{empleado.apellido_paterno}_{empleado.nombre}.docx',
                'contenido_base64': contenido_base64,
                'tipo': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            }
        }
    except Exception as e:
        return {'success': False, 'error': f'Error generando documento: {str(e)}'}


def accion_generar_contrato_word(usuario, params: Dict, contexto: Dict) -> Dict:
    """Genera contrato laboral en Word"""
    from apps.empleados.models import Empleado
    from .generador_documentos import GeneradorDocumentos

    empleado_id = params.get('empleado_id')
    empleado_nombre = params.get('empleado_nombre')

    # Buscar empleado
    if empleado_id:
        try:
            empleado = Empleado.objects.get(id=empleado_id)
        except Empleado.DoesNotExist:
            return {'success': False, 'error': 'Empleado no encontrado'}
    elif empleado_nombre:
        empresa = contexto.get('empresa_contexto')
        qs = Empleado.objects.filter(estado='activo')
        if empresa:
            qs = qs.filter(empresa=empresa)
        empleado = qs.filter(nombre__icontains=empleado_nombre).first()
        if not empleado:
            return {'success': False, 'error': f'No se encontro empleado con nombre "{empleado_nombre}"'}
    else:
        return {'success': False, 'error': 'Especifica el empleado para el contrato'}

    es_admin = usuario.rol == 'admin'
    es_rrhh = usuario.rol in ['empleador', 'rrhh']

    if not es_admin and not es_rrhh:
        return {'success': False, 'error': 'Solo RRHH puede generar contratos'}

    datos_contrato = {
        'tipo': params.get('tipo_contrato', 'indeterminado'),
        'jornada': params.get('jornada', 'lunes a viernes de 9:00 a 18:00 horas'),
    }

    try:
        buffer = GeneradorDocumentos.generar_contrato_laboral(empleado, datos_contrato)
        contenido_base64 = base64.b64encode(buffer.getvalue()).decode()

        return {
            'success': True,
            'mensaje': f'Contrato laboral generado para {empleado.nombre_completo}',
            'archivo': {
                'nombre': f'contrato_{empleado.apellido_paterno}_{empleado.nombre}.docx',
                'contenido_base64': contenido_base64,
                'tipo': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            }
        }
    except Exception as e:
        return {'success': False, 'error': f'Error generando documento: {str(e)}'}


def registrar_acciones_documentos():
    """Registra las acciones de generacion de documentos"""
    from .acciones_registry import registrar_accion

    registrar_accion(
        nombre='generar_constancia_laboral',
        descripcion='Genera constancia laboral en Word para un empleado',
        permisos=['es_admin', 'es_rrhh', 'es_empleado'],
        parametros={
            'empleado_id': 'ID del empleado (opcional si es para uno mismo)',
            'incluir_salario': 'True/False para incluir salario en la constancia',
        },
        ejemplo='Genera mi constancia laboral',
        funcion=accion_generar_constancia_laboral
    )

    registrar_accion(
        nombre='generar_carta_recomendacion',
        descripcion='Genera carta de recomendacion en Word',
        permisos=['es_admin', 'es_rrhh'],
        parametros={
            'empleado_id': 'ID del empleado',
            'empleado_nombre': 'Nombre del empleado',
            'destinatario': 'A quien va dirigida (opcional)',
        },
        ejemplo='Genera carta de recomendacion para Juan Perez',
        funcion=accion_generar_carta_recomendacion
    )

    registrar_accion(
        nombre='generar_carta_amonestacion',
        descripcion='Genera carta de amonestacion en Word',
        permisos=['es_admin', 'es_rrhh'],
        parametros={
            'empleado_id': 'ID del empleado',
            'empleado_nombre': 'Nombre del empleado',
            'motivo': 'Motivo de la amonestacion',
            'fecha_incidente': 'Fecha del incidente (YYYY-MM-DD)',
        },
        ejemplo='Genera carta de amonestacion para empleado por faltas injustificadas',
        funcion=accion_generar_carta_amonestacion
    )

    registrar_accion(
        nombre='generar_contrato_word',
        descripcion='Genera contrato laboral en Word',
        permisos=['es_admin', 'es_rrhh'],
        parametros={
            'empleado_id': 'ID del empleado',
            'empleado_nombre': 'Nombre del empleado',
            'tipo_contrato': 'indeterminado/determinado/obra (opcional)',
            'jornada': 'Descripcion de la jornada (opcional)',
        },
        ejemplo='Genera contrato laboral para el nuevo empleado',
        funcion=accion_generar_contrato_word
    )

    print("[OK] Acciones de Documentos Word registradas (94-97)")
