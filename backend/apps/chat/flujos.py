"""
Flujos conversacionales guiados con soporte para archivos
"""
from typing import Dict, List, Optional

FLUJOS = {
    'baja_empleado': {
        'nombre': 'Baja de Empleado',
        'triggers': ['dar de baja', 'baja de', 'despedir', 'renuncia de', 'terminar relación', 'liquidar a'],
        'pasos': [
            {
                'campo': 'empleado_confirmado',
                'pregunta': '¿Confirmas que deseas dar de baja a este empleado?',
                'tipo': 'confirmacion',
                'mostrar_info': True,
            },
            {
                'campo': 'tipo_baja',
                'pregunta': '¿Cuál es el motivo de la baja?',
                'tipo': 'opcion',
                'opciones': [
                    'Renuncia voluntaria',
                    'Despido justificado',
                    'Despido injustificado',
                    'Término de contrato',
                    'Jubilación',
                    'Mutuo acuerdo',
                    'Fallecimiento'
                ],
            },
            {
                'campo': 'fecha_ultimo_dia',
                'pregunta': '¿Cuál fue o será el último día laborado? (formato: dd/mm/yyyy o "hoy")',
                'tipo': 'fecha',
            },
            {
                'campo': 'motivo_detalle',
                'pregunta': '¿Puedes darme más detalles del motivo? (escribe "omitir" si no aplica)',
                'tipo': 'texto',
                'requerido': False,
            },
            {
                'campo': 'documento_soporte',
                'pregunta': '📎 ¿Tienes la carta de renuncia o documento soporte? Puedes subirlo ahora como archivo adjunto, o escribe "no tengo" para continuar.',
                'tipo': 'archivo',
                'tipos_esperados': ['carta_renuncia', 'carta_despido'],
                'requerido': False,
            },
            {
                'campo': 'confirmar_liquidacion',
                'pregunta': 'Te muestro el cálculo de liquidación. ¿Los montos son correctos?',
                'tipo': 'confirmacion',
                'calcular': 'liquidacion',
            },
            {
                'campo': 'generar_finiquito',
                'pregunta': '¿Deseas que genere el documento de finiquito en PDF?',
                'tipo': 'si_no',
                'accion_si': 'generar_pdf_finiquito',
            },
            {
                'campo': 'confirmar_baja',
                'pregunta': '✅ ¿Confirmas la baja del empleado con todos los datos capturados?',
                'tipo': 'confirmacion_final',
                'accion': 'dar_baja_empleado',
            },
        ],
        'documentos_requeridos': [],
        'documentos_opcionales': ['carta_renuncia', 'finiquito'],
        'siguientes_acciones': [
            {'texto': 'Generar constancia laboral', 'accion': 'generar_constancia'},
            {'texto': 'Ver extrabajadores', 'accion': 'ver_extrabajadores'},
        ],
    },

    'crear_empleado': {
        'nombre': 'Alta de Empleado',
        'triggers': ['nuevo empleado', 'crear empleado', 'contratar', 'registrar empleado', 'alta de empleado', 'dar de alta'],
        'pasos': [
            {
                'campo': 'nombre',
                'pregunta': '¿Cuál es el nombre completo del empleado? (Nombre Apellido Paterno Apellido Materno)',
                'tipo': 'texto',
            },
            {
                'campo': 'rfc',
                'pregunta': '¿Cuál es su RFC? (13 caracteres, escribe "pendiente" si no lo tienes)',
                'tipo': 'texto',
                'validacion': 'rfc',
                'requerido': False,
            },
            {
                'campo': 'curp',
                'pregunta': '¿Cuál es su CURP? (18 caracteres, escribe "pendiente" si no lo tienes)',
                'tipo': 'texto',
                'validacion': 'curp',
                'requerido': False,
            },
            {
                'campo': 'nss',
                'pregunta': '¿Cuál es su NSS (Número de Seguro Social)? (11 dígitos, escribe "pendiente" si no lo tiene)',
                'tipo': 'texto',
                'validacion': 'nss',
                'requerido': False,
            },
            {
                'campo': 'fecha_nacimiento',
                'pregunta': '¿Cuál es su fecha de nacimiento? (dd/mm/yyyy)',
                'tipo': 'fecha',
                'requerido': False,
            },
            {
                'campo': 'fecha_ingreso',
                'pregunta': '¿Cuál es la fecha de ingreso? (dd/mm/yyyy o "hoy")',
                'tipo': 'fecha',
            },
            {
                'campo': 'puesto',
                'pregunta': '¿Qué puesto ocupará?',
                'tipo': 'texto',
            },
            {
                'campo': 'departamento',
                'pregunta': '¿En qué departamento trabajará?',
                'tipo': 'texto',
            },
            {
                'campo': 'salario_diario',
                'pregunta': '¿Cuál será su salario diario? (en pesos, solo el número)',
                'tipo': 'numero',
            },
            {
                'campo': 'tipo_contrato',
                'pregunta': '¿Qué tipo de contrato?',
                'tipo': 'opcion',
                'opciones': ['Indefinido', 'Temporal', 'Por obra', 'Capacitación', 'Periodo de prueba'],
            },
            {
                'campo': 'jefe_directo',
                'pregunta': '¿Quién será su jefe directo? (nombre o "sin jefe")',
                'tipo': 'texto',
                'requerido': False,
            },
            {
                'campo': 'documentos_personales',
                'pregunta': '📎 Puedes subir los documentos del empleado (INE, CURP, comprobante domicilio). Sube uno a la vez o escribe "después" para hacerlo más tarde.',
                'tipo': 'archivos_multiple',
                'tipos_esperados': ['ine', 'curp', 'comprobante_domicilio', 'rfc', 'nss'],
                'requerido': False,
            },
            {
                'campo': 'confirmar',
                'pregunta': '✅ ¿Confirmas el alta del empleado con estos datos?',
                'tipo': 'confirmacion_final',
                'accion': 'crear_empleado',
            },
        ],
        'documentos_requeridos': [],
        'documentos_opcionales': ['ine', 'curp', 'comprobante_domicilio', 'rfc', 'acta_nacimiento'],
        'siguientes_acciones': [
            {'texto': 'Generar contrato', 'accion': 'generar_contrato'},
            {'texto': 'Asignar KPIs', 'accion': 'asignar_kpi'},
            {'texto': 'Subir más documentos', 'accion': 'subir_documento'},
        ],
    },

    'registrar_incidencia': {
        'nombre': 'Registrar Incidencia',
        'triggers': ['registrar incidencia', 'falta de', 'permiso de', 'horas extra', 'incapacidad de', 'justificante',
                     'registrar falta', 'registrar una incapacidad', 'reportar incapacidad', 'reportar falta',
                     'registrar permiso', 'meter incidencia', 'capturar incidencia'],
        'pasos': [
            {
                'campo': 'empleado_nombre',
                'pregunta': '¿Para qué empleado es la incidencia?',
                'tipo': 'texto',
            },
            {
                'campo': 'tipo',
                'pregunta': '¿Qué tipo de incidencia es?',
                'tipo': 'opcion',
                'opciones': [
                    'Falta justificada',
                    'Falta injustificada',
                    'Hora extra',
                    'Permiso con goce',
                    'Permiso sin goce',
                    'Incapacidad',
                    'Vacaciones'
                ],
            },
            {
                'campo': 'fecha_inicio',
                'pregunta': '¿En qué fecha inicia? (dd/mm/yyyy)',
                'tipo': 'fecha',
            },
            {
                'campo': 'fecha_fin',
                'pregunta': '¿En qué fecha termina? (dd/mm/yyyy, si es un solo día pon la misma fecha)',
                'tipo': 'fecha',
            },
            {
                'campo': 'cantidad',
                'pregunta': '¿Cuántos días/horas son?',
                'tipo': 'numero',
            },
            {
                'campo': 'documento_soporte',
                'pregunta': '📎 ¿Tienes documento soporte? (incapacidad IMSS, permiso firmado, justificante). Puedes subirlo ahora o escribe "no tengo".',
                'tipo': 'archivo',
                'tipos_esperados': ['incapacidad', 'permiso'],
                'requerido': False,
            },
            {
                'campo': 'folio_imss',
                'pregunta': '¿Cuál es el folio de la incapacidad IMSS? (escribe "no aplica" si no es incapacidad)',
                'tipo': 'texto',
                'condicion': 'tipo == Incapacidad',
                'requerido': False,
            },
            {
                'campo': 'motivo',
                'pregunta': '¿Cuál es el motivo? (breve descripción o "sin motivo")',
                'tipo': 'texto',
                'requerido': False,
            },
            {
                'campo': 'confirmar',
                'pregunta': '✅ ¿Registro la incidencia con estos datos?',
                'tipo': 'confirmacion_final',
                'accion': 'registrar_incidencia',
            },
        ],
        'siguientes_acciones': [
            {'texto': 'Registrar otra incidencia', 'accion': 'registrar_incidencia'},
            {'texto': 'Ver incidencias del mes', 'accion': 'ver_incidencias'},
        ],
    },

    'subir_documento': {
        'nombre': 'Subir Documento al Expediente',
        'triggers': ['subir documento', 'agregar documento', 'cargar archivo', 'subir al expediente'],
        'pasos': [
            {
                'campo': 'empleado_nombre',
                'pregunta': '¿A qué empleado pertenece el documento?',
                'tipo': 'texto',
            },
            {
                'campo': 'archivo',
                'pregunta': '📎 Sube el archivo ahora (arrastra o selecciona el documento)',
                'tipo': 'archivo',
                'tipos_esperados': ['ine', 'curp', 'rfc', 'comprobante_domicilio', 'contrato', 'otro'],
                'requerido': True,
            },
            {
                'campo': 'tipo_documento',
                'pregunta': 'Detecté que es un documento tipo "{tipo_detectado}". ¿Es correcto? Si no, indica el tipo correcto.',
                'tipo': 'confirmacion_tipo',
            },
            {
                'campo': 'confirmar',
                'pregunta': '✅ ¿Guardo el documento en el expediente del empleado?',
                'tipo': 'confirmacion_final',
                'accion': 'guardar_documento_expediente',
            },
        ],
        'siguientes_acciones': [
            {'texto': 'Subir otro documento', 'accion': 'subir_documento'},
            {'texto': 'Ver expediente', 'accion': 'ver_expediente'},
        ],
    },
}


def detectar_flujo(mensaje: str) -> Optional[str]:
    """Detecta si el mensaje inicia un flujo conocido"""
    mensaje_lower = mensaje.lower()
    for flujo_id, flujo in FLUJOS.items():
        for trigger in flujo['triggers']:
            if trigger in mensaje_lower:
                return flujo_id
    return None


def obtener_flujo(flujo_id: str) -> Optional[Dict]:
    """Obtiene la definición de un flujo"""
    return FLUJOS.get(flujo_id)


def obtener_paso_actual(flujo_id: str, paso_num: int) -> Optional[Dict]:
    """Obtiene el paso actual de un flujo"""
    flujo = FLUJOS.get(flujo_id)
    if flujo and 0 <= paso_num < len(flujo['pasos']):
        return flujo['pasos'][paso_num]
    return None


def validar_respuesta_paso(paso: Dict, respuesta: str) -> tuple[bool, str, any]:
    """
    Valida la respuesta del usuario para un paso
    Retorna: (es_valida, mensaje_error, valor_parseado)
    """
    tipo = paso.get('tipo', 'texto')
    requerido = paso.get('requerido', True)

    # Verificar si es opcional y usuario quiere omitir
    respuesta_lower = respuesta.lower().strip()
    if respuesta_lower in ['omitir', 'no tengo', 'pendiente', 'después', 'despues', 'sin jefe', 'no aplica', 'sin motivo']:
        if not requerido:
            return True, '', None
        else:
            return False, 'Este campo es requerido', None

    if tipo == 'confirmacion' or tipo == 'confirmacion_final':
        if respuesta_lower in ['sí', 'si', 'yes', 'confirmo', 'correcto', 'ok']:
            return True, '', True
        elif respuesta_lower in ['no', 'cancelar', 'incorrecto']:
            return True, '', False
        return False, 'Responde "sí" para confirmar o "no" para cancelar', None

    elif tipo == 'si_no':
        if respuesta_lower in ['sí', 'si', 'yes']:
            return True, '', True
        elif respuesta_lower in ['no']:
            return True, '', False
        return False, 'Responde "sí" o "no"', None

    elif tipo == 'opcion':
        opciones = paso.get('opciones', [])
        # Buscar coincidencia parcial
        for i, opcion in enumerate(opciones):
            if respuesta_lower in opcion.lower() or opcion.lower() in respuesta_lower:
                return True, '', opcion
        return False, f'Selecciona una opción válida: {", ".join(opciones)}', None

    elif tipo == 'fecha':
        from datetime import datetime, date
        if respuesta_lower == 'hoy':
            return True, '', date.today().isoformat()
        # Intentar varios formatos
        formatos = ['%d/%m/%Y', '%Y-%m-%d', '%d-%m-%Y', '%d.%m.%Y']
        for fmt in formatos:
            try:
                fecha = datetime.strptime(respuesta.strip(), fmt).date()
                return True, '', fecha.isoformat()
            except ValueError:
                continue
        return False, 'Formato de fecha inválido. Usa dd/mm/yyyy', None

    elif tipo == 'numero':
        try:
            # Limpiar caracteres no numéricos excepto punto
            limpio = ''.join(c for c in respuesta if c.isdigit() or c == '.')
            valor = float(limpio)
            return True, '', valor
        except ValueError:
            return False, 'Ingresa un número válido', None

    elif tipo == 'texto':
        validacion = paso.get('validacion')
        if validacion == 'rfc' and len(respuesta.strip()) not in [12, 13]:
            if respuesta_lower != 'pendiente':
                return False, 'El RFC debe tener 12 o 13 caracteres', None
        elif validacion == 'curp' and len(respuesta.strip()) != 18:
            if respuesta_lower != 'pendiente':
                return False, 'El CURP debe tener 18 caracteres', None
        elif validacion == 'nss' and len(respuesta.strip()) != 11:
            if respuesta_lower not in ['pendiente', 'no tiene']:
                return False, 'El NSS debe tener 11 dígitos', None
        return True, '', respuesta.strip()

    elif tipo in ['archivo', 'archivos_multiple']:
        # Los archivos se manejan aparte
        return True, '', None

    return True, '', respuesta.strip()


def formatear_opciones(opciones: List[str]) -> str:
    """Formatea las opciones para mostrar al usuario"""
    lineas = []
    for i, opcion in enumerate(opciones, 1):
        lineas.append(f"  {i}. {opcion}")
    return '\n'.join(lineas)


def mapear_tipo_baja(opcion: str) -> str:
    """Mapea la opción seleccionada al valor del enum TipoBaja"""
    mapa = {
        'Renuncia voluntaria': 'renuncia_voluntaria',
        'Despido justificado': 'despido_justificado',
        'Despido injustificado': 'despido_injustificado',
        'Término de contrato': 'termino_contrato',
        'Jubilación': 'jubilacion',
        'Mutuo acuerdo': 'mutuo_acuerdo',
        'Fallecimiento': 'fallecimiento',
    }
    return mapa.get(opcion, 'otro')


def mapear_tipo_contrato(opcion: str) -> str:
    """Mapea la opción de contrato al valor del enum"""
    mapa = {
        'Indefinido': 'indefinido',
        'Temporal': 'temporal',
        'Por obra': 'obra',
        'Capacitación': 'capacitacion',
        'Periodo de prueba': 'prueba',
    }
    return mapa.get(opcion, 'indefinido')


def mapear_tipo_incidencia(opcion: str) -> str:
    """Mapea la opción de incidencia al valor usado en el sistema"""
    mapa = {
        'Falta justificada': 'falta_justificada',
        'Falta injustificada': 'falta',
        'Hora extra': 'hora_extra',
        'Permiso con goce': 'permiso_con_goce',
        'Permiso sin goce': 'permiso_sin_goce',
        'Incapacidad': 'incapacidad',
        'Vacaciones': 'vacaciones',
    }
    return mapa.get(opcion, 'otro')
