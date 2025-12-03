"""
Validadores para documentos fiscales mexicanos.

Incluye validaciones para:
- RFC (Persona Física y Moral)
- CURP
- NSS (Número de Seguro Social IMSS)
- CLABE (Cuenta Bancaria)
"""
import re
from typing import Tuple, Optional
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


# ============================================================
# PATRONES REGEX
# ============================================================

# RFC Persona Física: 4 letras + 6 dígitos fecha + 3 homoclave
RFC_FISICA_PATTERN = re.compile(
    r'^[A-ZÑ&]{4}'           # 4 letras (incluye Ñ y &)
    r'\d{2}'                  # Año (2 dígitos)
    r'(0[1-9]|1[0-2])'        # Mes (01-12)
    r'(0[1-9]|[12]\d|3[01])'  # Día (01-31)
    r'[A-Z0-9]{3}$',          # Homoclave (3 caracteres)
    re.IGNORECASE
)

# RFC Persona Moral: 3 letras + 6 dígitos fecha + 3 homoclave
RFC_MORAL_PATTERN = re.compile(
    r'^[A-ZÑ&]{3}'           # 3 letras
    r'\d{2}'                  # Año
    r'(0[1-9]|1[0-2])'        # Mes
    r'(0[1-9]|[12]\d|3[01])'  # Día
    r'[A-Z0-9]{3}$',          # Homoclave
    re.IGNORECASE
)

# CURP: 18 caracteres alfanuméricos
CURP_PATTERN = re.compile(
    r'^[A-Z]{4}'              # 4 letras del nombre
    r'\d{2}'                  # Año nacimiento
    r'(0[1-9]|1[0-2])'        # Mes nacimiento
    r'(0[1-9]|[12]\d|3[01])'  # Día nacimiento
    r'[HM]'                   # Sexo (H/M)
    r'(AS|BC|BS|CC|CL|CM|CS|CH|DF|DG|GT|GR|HG|JC|MC|MN|MS|NT|NL|OC|PL|QT|QR|SP|SL|SR|TC|TS|TL|VZ|YN|ZS|NE)'  # Entidad
    r'[B-DF-HJ-NP-TV-Z]{3}'   # Consonantes internas
    r'[A-Z0-9]'               # Dígito verificador u homoclave
    r'\d$',                   # Dígito verificador
    re.IGNORECASE
)

# NSS: 11 dígitos
NSS_PATTERN = re.compile(r'^\d{11}$')

# CLABE: 18 dígitos
CLABE_PATTERN = re.compile(r'^\d{18}$')


# ============================================================
# ENTIDADES FEDERATIVAS (para CURP)
# ============================================================
ENTIDADES_FEDERATIVAS = {
    'AS': 'Aguascalientes',
    'BC': 'Baja California',
    'BS': 'Baja California Sur',
    'CC': 'Campeche',
    'CL': 'Coahuila',
    'CM': 'Colima',
    'CS': 'Chiapas',
    'CH': 'Chihuahua',
    'DF': 'Ciudad de México',
    'DG': 'Durango',
    'GT': 'Guanajuato',
    'GR': 'Guerrero',
    'HG': 'Hidalgo',
    'JC': 'Jalisco',
    'MC': 'Estado de México',
    'MN': 'Michoacán',
    'MS': 'Morelos',
    'NT': 'Nayarit',
    'NL': 'Nuevo León',
    'OC': 'Oaxaca',
    'PL': 'Puebla',
    'QT': 'Querétaro',
    'QR': 'Quintana Roo',
    'SP': 'San Luis Potosí',
    'SL': 'Sinaloa',
    'SR': 'Sonora',
    'TC': 'Tabasco',
    'TS': 'Tamaulipas',
    'TL': 'Tlaxcala',
    'VZ': 'Veracruz',
    'YN': 'Yucatán',
    'ZS': 'Zacatecas',
    'NE': 'Nacido en el Extranjero',
}


# ============================================================
# FUNCIONES DE VALIDACIÓN
# ============================================================

def validar_rfc(rfc: str, tipo: str = 'cualquiera') -> Tuple[bool, str]:
    """
    Valida un RFC mexicano.

    Args:
        rfc: El RFC a validar
        tipo: 'fisica', 'moral', o 'cualquiera'

    Returns:
        Tuple (es_valido, mensaje)
    """
    if not rfc:
        return False, "RFC es requerido"

    rfc = rfc.upper().strip().replace(' ', '').replace('-', '')

    # Validar longitud
    if len(rfc) == 13:
        es_persona_fisica = True
    elif len(rfc) == 12:
        es_persona_fisica = False
    else:
        return False, f"RFC debe tener 12 o 13 caracteres, tiene {len(rfc)}"

    # Validar según tipo
    if tipo == 'fisica' and not es_persona_fisica:
        return False, "Se esperaba RFC de persona física (13 caracteres)"

    if tipo == 'moral' and es_persona_fisica:
        return False, "Se esperaba RFC de persona moral (12 caracteres)"

    # Validar formato
    if es_persona_fisica:
        if not RFC_FISICA_PATTERN.match(rfc):
            return False, "Formato de RFC persona física inválido"
    else:
        if not RFC_MORAL_PATTERN.match(rfc):
            return False, "Formato de RFC persona moral inválido"

    # Validar fecha
    try:
        ano = int(rfc[4:6] if es_persona_fisica else rfc[3:5])
        mes = int(rfc[6:8] if es_persona_fisica else rfc[5:7])
        dia = int(rfc[8:10] if es_persona_fisica else rfc[7:9])

        # Validación básica de fecha
        if mes < 1 or mes > 12:
            return False, f"Mes inválido en RFC: {mes}"

        dias_por_mes = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        if dia < 1 or dia > dias_por_mes[mes - 1]:
            return False, f"Día inválido para el mes {mes}: {dia}"

    except (ValueError, IndexError):
        return False, "Fecha inválida en RFC"

    tipo_str = "persona física" if es_persona_fisica else "persona moral"
    return True, f"RFC válido ({tipo_str})"


def validar_curp(curp: str) -> Tuple[bool, str]:
    """
    Valida una CURP mexicana.

    Returns:
        Tuple (es_valido, mensaje)
    """
    if not curp:
        return False, "CURP es requerida"

    curp = curp.upper().strip().replace(' ', '')

    if len(curp) != 18:
        return False, f"CURP debe tener 18 caracteres, tiene {len(curp)}"

    if not CURP_PATTERN.match(curp):
        return False, "Formato de CURP inválido"

    # Extraer y validar entidad federativa
    entidad = curp[11:13]
    if entidad not in ENTIDADES_FEDERATIVAS:
        return False, f"Entidad federativa inválida: {entidad}"

    # Validar fecha de nacimiento
    try:
        ano = int(curp[4:6])
        mes = int(curp[6:8])
        dia = int(curp[8:10])

        if mes < 1 or mes > 12:
            return False, f"Mes de nacimiento inválido: {mes}"

        dias_por_mes = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        if dia < 1 or dia > dias_por_mes[mes - 1]:
            return False, f"Día de nacimiento inválido: {dia}"

    except ValueError:
        return False, "Fecha de nacimiento inválida en CURP"

    # Validar sexo
    sexo = curp[10]
    sexo_str = "Masculino" if sexo == 'H' else "Femenino"

    return True, f"CURP válida ({sexo_str}, {ENTIDADES_FEDERATIVAS[entidad]})"


def calcular_digito_verificador_nss(nss: str) -> int:
    """
    Calcula el dígito verificador de un NSS usando el algoritmo de Luhn modificado del IMSS.
    """
    if len(nss) < 10:
        return -1

    nss_sin_verificador = nss[:10]
    suma = 0

    for i, digito in enumerate(nss_sin_verificador):
        valor = int(digito)
        if i % 2 == 0:  # Posiciones pares (0, 2, 4, ...)
            valor *= 1
        else:  # Posiciones impares
            valor *= 2
            if valor > 9:
                valor -= 9
        suma += valor

    digito_verificador = (10 - (suma % 10)) % 10
    return digito_verificador


def validar_nss(nss: str) -> Tuple[bool, str]:
    """
    Valida un Número de Seguro Social (NSS) del IMSS.

    Returns:
        Tuple (es_valido, mensaje)
    """
    if not nss:
        return False, "NSS es requerido"

    nss = nss.strip().replace(' ', '').replace('-', '')

    if len(nss) != 11:
        return False, f"NSS debe tener 11 dígitos, tiene {len(nss)}"

    if not NSS_PATTERN.match(nss):
        return False, "NSS debe contener solo dígitos"

    # Validar subdelegación (primeros 2 dígitos: 01-97)
    subdelegacion = int(nss[:2])
    if subdelegacion < 1 or subdelegacion > 97:
        return False, f"Subdelegación inválida: {subdelegacion}"

    # Validar año de alta (dígitos 3-4)
    # No hay restricción específica, cualquier valor 00-99 es válido

    # Validar año de nacimiento (dígitos 5-6)
    # No hay restricción específica, cualquier valor 00-99 es válido

    # Validar dígito verificador
    digito_esperado = calcular_digito_verificador_nss(nss)
    digito_actual = int(nss[10])

    if digito_esperado != digito_actual:
        return False, f"Dígito verificador inválido: esperado {digito_esperado}, encontrado {digito_actual}"

    return True, "NSS válido"


def calcular_digito_verificador_clabe(clabe: str) -> int:
    """
    Calcula el dígito verificador de una CLABE usando el algoritmo estándar.
    """
    if len(clabe) < 17:
        return -1

    pesos = [3, 7, 1, 3, 7, 1, 3, 7, 1, 3, 7, 1, 3, 7, 1, 3, 7]
    suma = 0

    for i, digito in enumerate(clabe[:17]):
        valor = int(digito) * pesos[i]
        suma += valor % 10

    digito_verificador = (10 - (suma % 10)) % 10
    return digito_verificador


def validar_clabe(clabe: str) -> Tuple[bool, str]:
    """
    Valida una Clave Bancaria Estandarizada (CLABE).

    Returns:
        Tuple (es_valido, mensaje)
    """
    if not clabe:
        return False, "CLABE es requerida"

    clabe = clabe.strip().replace(' ', '').replace('-', '')

    if len(clabe) != 18:
        return False, f"CLABE debe tener 18 dígitos, tiene {len(clabe)}"

    if not CLABE_PATTERN.match(clabe):
        return False, "CLABE debe contener solo dígitos"

    # Validar código de banco (primeros 3 dígitos)
    # Los códigos válidos son asignados por Banxico
    codigo_banco = clabe[:3]

    # Validar dígito verificador
    digito_esperado = calcular_digito_verificador_clabe(clabe)
    digito_actual = int(clabe[17])

    if digito_esperado != digito_actual:
        return False, f"Dígito verificador inválido: esperado {digito_esperado}, encontrado {digito_actual}"

    return True, f"CLABE válida (Banco: {codigo_banco})"


# ============================================================
# VALIDADORES DJANGO
# ============================================================

def validate_rfc(value: str) -> None:
    """Validador Django para RFC."""
    if not value:
        return

    # Permitir valores especiales
    if value.lower() in ['pendiente', 'no tiene', 'n/a', 'na', '-']:
        return

    es_valido, mensaje = validar_rfc(value)
    if not es_valido:
        raise ValidationError(_(mensaje), code='invalid_rfc')


def validate_rfc_fisica(value: str) -> None:
    """Validador Django para RFC de persona física."""
    if not value:
        return

    if value.lower() in ['pendiente', 'no tiene', 'n/a', 'na', '-']:
        return

    es_valido, mensaje = validar_rfc(value, tipo='fisica')
    if not es_valido:
        raise ValidationError(_(mensaje), code='invalid_rfc')


def validate_rfc_moral(value: str) -> None:
    """Validador Django para RFC de persona moral."""
    if not value:
        return

    if value.lower() in ['pendiente', 'no tiene', 'n/a', 'na', '-']:
        return

    es_valido, mensaje = validar_rfc(value, tipo='moral')
    if not es_valido:
        raise ValidationError(_(mensaje), code='invalid_rfc')


def validate_curp(value: str) -> None:
    """Validador Django para CURP."""
    if not value:
        return

    if value.lower() in ['pendiente', 'no tiene', 'n/a', 'na', '-']:
        return

    es_valido, mensaje = validar_curp(value)
    if not es_valido:
        raise ValidationError(_(mensaje), code='invalid_curp')


def validate_nss(value: str) -> None:
    """Validador Django para NSS."""
    if not value:
        return

    if value.lower() in ['pendiente', 'no tiene', 'n/a', 'na', '-']:
        return

    es_valido, mensaje = validar_nss(value)
    if not es_valido:
        raise ValidationError(_(mensaje), code='invalid_nss')


def validate_clabe(value: str) -> None:
    """Validador Django para CLABE."""
    if not value:
        return

    if value.lower() in ['pendiente', 'no tiene', 'n/a', 'na', '-']:
        return

    es_valido, mensaje = validar_clabe(value)
    if not es_valido:
        raise ValidationError(_(mensaje), code='invalid_clabe')


# ============================================================
# HELPER PARA CHAT/FLUJOS
# ============================================================

def validar_campo_fiscal(valor: str, tipo: str) -> Tuple[bool, str, Optional[str]]:
    """
    Valida un campo fiscal permitiendo valores especiales.

    Args:
        valor: El valor a validar
        tipo: 'rfc', 'rfc_fisica', 'rfc_moral', 'curp', 'nss', 'clabe'

    Returns:
        Tuple (es_valido, mensaje, valor_normalizado)
        - valor_normalizado es None si es inválido
        - valor_normalizado es el valor en mayúsculas si es válido
        - valor_normalizado es el valor original si es un valor especial
    """
    if not valor:
        return False, "El valor es requerido", None

    valor_lower = valor.lower().strip()

    # Valores especiales aceptados
    valores_especiales = ['pendiente', 'no tiene', 'n/a', 'na', '-', 'en tramite', 'en trámite']
    if valor_lower in valores_especiales:
        return True, "Valor especial aceptado", valor

    # Normalizar valor
    valor_normalizado = valor.upper().strip().replace(' ', '').replace('-', '')

    # Validar según tipo
    validadores = {
        'rfc': validar_rfc,
        'rfc_fisica': lambda v: validar_rfc(v, 'fisica'),
        'rfc_moral': lambda v: validar_rfc(v, 'moral'),
        'curp': validar_curp,
        'nss': validar_nss,
        'clabe': validar_clabe,
    }

    if tipo not in validadores:
        return False, f"Tipo de validación desconocido: {tipo}", None

    es_valido, mensaje = validadores[tipo](valor_normalizado)

    if es_valido:
        return True, mensaje, valor_normalizado
    else:
        return False, mensaje, None


def obtener_info_documento(valor: str, tipo: str) -> dict:
    """
    Obtiene información detallada de un documento fiscal.

    Returns:
        Dict con información del documento o error
    """
    es_valido, mensaje, valor_normalizado = validar_campo_fiscal(valor, tipo)

    if not es_valido:
        return {
            'valido': False,
            'error': mensaje,
            'tipo': tipo,
            'valor_original': valor
        }

    resultado = {
        'valido': True,
        'mensaje': mensaje,
        'tipo': tipo,
        'valor_original': valor,
        'valor_normalizado': valor_normalizado
    }

    # Agregar información adicional según el tipo
    if tipo in ['rfc', 'rfc_fisica', 'rfc_moral'] and valor_normalizado and len(valor_normalizado) >= 10:
        es_fisica = len(valor_normalizado) == 13
        idx_offset = 4 if es_fisica else 3
        resultado['info'] = {
            'tipo_persona': 'Física' if es_fisica else 'Moral',
            'año_registro': valor_normalizado[idx_offset:idx_offset+2],
            'mes_registro': valor_normalizado[idx_offset+2:idx_offset+4],
            'dia_registro': valor_normalizado[idx_offset+4:idx_offset+6],
            'homoclave': valor_normalizado[-3:]
        }

    elif tipo == 'curp' and valor_normalizado and len(valor_normalizado) == 18:
        entidad = valor_normalizado[11:13]
        resultado['info'] = {
            'sexo': 'Masculino' if valor_normalizado[10] == 'H' else 'Femenino',
            'entidad_codigo': entidad,
            'entidad_nombre': ENTIDADES_FEDERATIVAS.get(entidad, 'Desconocida'),
            'año_nacimiento': valor_normalizado[4:6],
            'mes_nacimiento': valor_normalizado[6:8],
            'dia_nacimiento': valor_normalizado[8:10]
        }

    elif tipo == 'nss' and valor_normalizado and len(valor_normalizado) == 11:
        resultado['info'] = {
            'subdelegacion': valor_normalizado[:2],
            'año_alta': valor_normalizado[2:4],
            'año_nacimiento': valor_normalizado[4:6],
            'numero_asignacion': valor_normalizado[6:10],
            'digito_verificador': valor_normalizado[10]
        }

    elif tipo == 'clabe' and valor_normalizado and len(valor_normalizado) == 18:
        resultado['info'] = {
            'codigo_banco': valor_normalizado[:3],
            'codigo_plaza': valor_normalizado[3:6],
            'numero_cuenta': valor_normalizado[6:17],
            'digito_verificador': valor_normalizado[17]
        }

    return resultado
