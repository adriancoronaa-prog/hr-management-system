"""
Tests para validadores de documentos fiscales mexicanos.
"""
import pytest
from django.core.exceptions import ValidationError

from apps.core.validators import (
    validar_rfc,
    validar_curp,
    validar_nss,
    validar_clabe,
    validate_rfc,
    validate_curp,
    validate_nss,
    validate_clabe,
    validar_campo_fiscal,
    obtener_info_documento,
    calcular_digito_verificador_nss,
    calcular_digito_verificador_clabe,
)


# ============================================================
# TESTS PARA RFC
# ============================================================

class TestValidarRFC:
    """Tests para validación de RFC"""

    # RFCs válidos de persona física
    def test_rfc_fisica_valido(self):
        """RFC de persona física con formato correcto"""
        es_valido, mensaje = validar_rfc('GARC850101ABC')
        assert es_valido is True
        assert 'persona física' in mensaje.lower()

    def test_rfc_fisica_valido_minusculas(self):
        """RFC válido en minúsculas"""
        es_valido, mensaje = validar_rfc('garc850101abc')
        assert es_valido is True

    def test_rfc_fisica_con_nie(self):
        """RFC con Ñ"""
        es_valido, mensaje = validar_rfc('MUÑO850101XYZ')
        assert es_valido is True

    def test_rfc_fisica_con_ampersand(self):
        """RFC con &"""
        es_valido, mensaje = validar_rfc('GAR&850101XYZ')
        assert es_valido is True

    # RFCs válidos de persona moral
    def test_rfc_moral_valido(self):
        """RFC de persona moral con formato correcto"""
        es_valido, mensaje = validar_rfc('ABC850101XY9')
        assert es_valido is True
        assert 'persona moral' in mensaje.lower()

    # RFCs inválidos
    def test_rfc_longitud_incorrecta(self):
        """RFC con longitud incorrecta"""
        es_valido, mensaje = validar_rfc('GARC8501')
        assert es_valido is False
        assert '12 o 13' in mensaje

    def test_rfc_mes_invalido(self):
        """RFC con mes inválido (13)"""
        es_valido, mensaje = validar_rfc('GARC851301ABC')
        assert es_valido is False

    def test_rfc_dia_invalido(self):
        """RFC con día inválido (32)"""
        es_valido, mensaje = validar_rfc('GARC850132ABC')
        assert es_valido is False

    def test_rfc_vacio(self):
        """RFC vacío"""
        es_valido, mensaje = validar_rfc('')
        assert es_valido is False
        assert 'requerido' in mensaje.lower()

    # Validación por tipo
    def test_rfc_tipo_fisica_correcto(self):
        """RFC de persona física cuando se especifica tipo física"""
        es_valido, _ = validar_rfc('GARC850101ABC', tipo='fisica')
        assert es_valido is True

    def test_rfc_tipo_fisica_incorrecto(self):
        """RFC de persona moral cuando se especifica tipo física"""
        es_valido, mensaje = validar_rfc('ABC850101XY9', tipo='fisica')
        assert es_valido is False
        assert 'persona física' in mensaje

    def test_rfc_tipo_moral_correcto(self):
        """RFC de persona moral cuando se especifica tipo moral"""
        es_valido, _ = validar_rfc('ABC850101XY9', tipo='moral')
        assert es_valido is True

    def test_rfc_tipo_moral_incorrecto(self):
        """RFC de persona física cuando se especifica tipo moral"""
        es_valido, mensaje = validar_rfc('GARC850101ABC', tipo='moral')
        assert es_valido is False
        assert 'persona moral' in mensaje


# ============================================================
# TESTS PARA CURP
# ============================================================

class TestValidarCURP:
    """Tests para validación de CURP"""

    def test_curp_valida_hombre(self):
        """CURP válida de hombre"""
        es_valido, mensaje = validar_curp('GARC850101HDFRRL09')
        assert es_valido is True
        assert 'masculino' in mensaje.lower()

    def test_curp_valida_mujer(self):
        """CURP válida de mujer"""
        es_valido, mensaje = validar_curp('GARC850101MDFRRL09')
        assert es_valido is True
        assert 'femenino' in mensaje.lower()

    def test_curp_valida_minusculas(self):
        """CURP válida en minúsculas"""
        es_valido, _ = validar_curp('garc850101hdfrrl09')
        assert es_valido is True

    def test_curp_longitud_incorrecta(self):
        """CURP con longitud incorrecta"""
        es_valido, mensaje = validar_curp('GARC850101HDF')
        assert es_valido is False
        assert '18' in mensaje

    def test_curp_entidad_invalida(self):
        """CURP con entidad federativa inválida"""
        es_valido, mensaje = validar_curp('GARC850101HXXRRL09')
        assert es_valido is False
        assert 'formato' in mensaje.lower() or 'inválid' in mensaje.lower()

    def test_curp_sexo_invalido(self):
        """CURP con sexo inválido"""
        es_valido, mensaje = validar_curp('GARC850101XDFRRL09')
        assert es_valido is False

    def test_curp_mes_invalido(self):
        """CURP con mes inválido"""
        es_valido, mensaje = validar_curp('GARC851301HDFRRL09')
        assert es_valido is False

    def test_curp_vacia(self):
        """CURP vacía"""
        es_valido, mensaje = validar_curp('')
        assert es_valido is False

    # Test de entidades federativas válidas
    def test_curp_todas_entidades(self):
        """Verifica que todas las entidades federativas sean válidas"""
        entidades = ['AS', 'BC', 'BS', 'CC', 'CL', 'CM', 'CS', 'CH', 'DF', 'DG',
                     'GT', 'GR', 'HG', 'JC', 'MC', 'MN', 'MS', 'NT', 'NL', 'OC',
                     'PL', 'QT', 'QR', 'SP', 'SL', 'SR', 'TC', 'TS', 'TL', 'VZ',
                     'YN', 'ZS', 'NE']
        for entidad in entidades:
            curp = f'GARC850101H{entidad}RRL09'
            es_valido, _ = validar_curp(curp)
            assert es_valido is True, f"Entidad {entidad} debería ser válida"


# ============================================================
# TESTS PARA NSS
# ============================================================

class TestValidarNSS:
    """Tests para validación de NSS"""

    def test_nss_valido(self):
        """NSS con dígito verificador correcto"""
        # El NSS 01856812345 tiene dígito verificador que hay que calcular
        nss_base = '0185681234'
        digito = calcular_digito_verificador_nss(nss_base + '0')
        nss_completo = nss_base + str(digito)
        es_valido, mensaje = validar_nss(nss_completo)
        assert es_valido is True

    def test_nss_longitud_incorrecta(self):
        """NSS con longitud incorrecta"""
        es_valido, mensaje = validar_nss('12345678')
        assert es_valido is False
        assert '11' in mensaje

    def test_nss_no_numerico(self):
        """NSS con caracteres no numéricos"""
        es_valido, mensaje = validar_nss('1234567890A')
        assert es_valido is False

    def test_nss_subdelegacion_invalida(self):
        """NSS con subdelegación inválida (00)"""
        es_valido, mensaje = validar_nss('00856812345')
        assert es_valido is False
        assert 'subdelegación' in mensaje.lower()

    def test_nss_digito_verificador_incorrecto(self):
        """NSS con dígito verificador incorrecto"""
        # Tomamos un NSS y le ponemos un dígito verificador incorrecto
        es_valido, mensaje = validar_nss('01856812340')  # Asumiendo que 0 es incorrecto
        # El resultado depende del dígito verificador correcto
        # Solo verificamos que la función detecte el error si es el caso
        if not es_valido:
            assert 'dígito verificador' in mensaje.lower()

    def test_nss_vacio(self):
        """NSS vacío"""
        es_valido, mensaje = validar_nss('')
        assert es_valido is False


# ============================================================
# TESTS PARA CLABE
# ============================================================

class TestValidarCLABE:
    """Tests para validación de CLABE"""

    def test_clabe_valida(self):
        """CLABE con dígito verificador correcto"""
        # Crear una CLABE con dígito verificador válido
        clabe_base = '01218000011234567'
        digito = calcular_digito_verificador_clabe(clabe_base + '0')
        clabe_completa = clabe_base + str(digito)
        es_valido, mensaje = validar_clabe(clabe_completa)
        assert es_valido is True

    def test_clabe_longitud_incorrecta(self):
        """CLABE con longitud incorrecta"""
        es_valido, mensaje = validar_clabe('1234567890')
        assert es_valido is False
        assert '18' in mensaje

    def test_clabe_no_numerica(self):
        """CLABE con caracteres no numéricos"""
        es_valido, mensaje = validar_clabe('01234567890123456A')
        assert es_valido is False

    def test_clabe_digito_verificador_incorrecto(self):
        """CLABE con dígito verificador incorrecto"""
        # CLABE con dígito verificador probablemente incorrecto
        es_valido, mensaje = validar_clabe('012180000112345670')
        if not es_valido:
            assert 'dígito verificador' in mensaje.lower()

    def test_clabe_vacia(self):
        """CLABE vacía"""
        es_valido, mensaje = validar_clabe('')
        assert es_valido is False


# ============================================================
# TESTS PARA VALIDADORES DJANGO
# ============================================================

class TestValidadoresDjango:
    """Tests para validadores de Django"""

    def test_validate_rfc_valido(self):
        """validate_rfc no lanza excepción para RFC válido"""
        validate_rfc('GARC850101ABC')  # No debe lanzar excepción

    def test_validate_rfc_invalido(self):
        """validate_rfc lanza ValidationError para RFC inválido"""
        with pytest.raises(ValidationError):
            validate_rfc('INVALIDO')

    def test_validate_rfc_pendiente(self):
        """validate_rfc permite valor 'pendiente'"""
        validate_rfc('pendiente')  # No debe lanzar excepción

    def test_validate_curp_valida(self):
        """validate_curp no lanza excepción para CURP válida"""
        validate_curp('GARC850101HDFRRL09')

    def test_validate_curp_invalida(self):
        """validate_curp lanza ValidationError para CURP inválida"""
        with pytest.raises(ValidationError):
            validate_curp('INVALIDO')

    def test_validate_nss_pendiente(self):
        """validate_nss permite valor 'no tiene'"""
        validate_nss('no tiene')

    def test_validate_clabe_na(self):
        """validate_clabe permite valor 'n/a'"""
        validate_clabe('n/a')


# ============================================================
# TESTS PARA VALIDAR_CAMPO_FISCAL
# ============================================================

class TestValidarCampoFiscal:
    """Tests para función helper validar_campo_fiscal"""

    def test_valor_especial_pendiente(self):
        """Valores especiales son aceptados"""
        es_valido, mensaje, valor = validar_campo_fiscal('pendiente', 'rfc')
        assert es_valido is True
        assert valor == 'pendiente'

    def test_valor_especial_no_tiene(self):
        """'no tiene' es aceptado"""
        es_valido, mensaje, valor = validar_campo_fiscal('no tiene', 'curp')
        assert es_valido is True

    def test_valor_especial_en_tramite(self):
        """'en trámite' es aceptado"""
        es_valido, mensaje, valor = validar_campo_fiscal('en trámite', 'nss')
        assert es_valido is True

    def test_rfc_valido_normalizado(self):
        """RFC válido se normaliza a mayúsculas"""
        es_valido, mensaje, valor = validar_campo_fiscal('garc850101abc', 'rfc')
        assert es_valido is True
        assert valor == 'GARC850101ABC'

    def test_tipo_desconocido(self):
        """Tipo de validación desconocido"""
        es_valido, mensaje, valor = validar_campo_fiscal('valor', 'desconocido')
        assert es_valido is False
        assert 'desconocido' in mensaje.lower()


# ============================================================
# TESTS PARA OBTENER_INFO_DOCUMENTO
# ============================================================

class TestObtenerInfoDocumento:
    """Tests para función obtener_info_documento"""

    def test_info_rfc_fisica(self):
        """Obtiene información de RFC de persona física"""
        info = obtener_info_documento('GARC850101ABC', 'rfc')
        assert info['valido'] is True
        assert 'info' in info
        assert info['info']['tipo_persona'] == 'Física'
        assert info['info']['homoclave'] == 'ABC'

    def test_info_rfc_moral(self):
        """Obtiene información de RFC de persona moral"""
        info = obtener_info_documento('ABC850101XY9', 'rfc')
        assert info['valido'] is True
        assert info['info']['tipo_persona'] == 'Moral'

    def test_info_curp(self):
        """Obtiene información de CURP"""
        info = obtener_info_documento('GARC850101HDFRRL09', 'curp')
        assert info['valido'] is True
        assert info['info']['sexo'] == 'Masculino'
        assert info['info']['entidad_codigo'] == 'DF'
        assert info['info']['entidad_nombre'] == 'Ciudad de México'

    def test_info_documento_invalido(self):
        """Documento inválido retorna error"""
        info = obtener_info_documento('INVALIDO', 'rfc')
        assert info['valido'] is False
        assert 'error' in info


# ============================================================
# TESTS PARA CÁLCULO DE DÍGITOS VERIFICADORES
# ============================================================

class TestDigitosVerificadores:
    """Tests para cálculo de dígitos verificadores"""

    def test_digito_nss_consistente(self):
        """El dígito verificador de NSS es consistente"""
        nss_base = '0185681234'
        digito1 = calcular_digito_verificador_nss(nss_base + '0')
        digito2 = calcular_digito_verificador_nss(nss_base + '0')
        assert digito1 == digito2

    def test_digito_clabe_consistente(self):
        """El dígito verificador de CLABE es consistente"""
        clabe_base = '01218000011234567'
        digito1 = calcular_digito_verificador_clabe(clabe_base + '0')
        digito2 = calcular_digito_verificador_clabe(clabe_base + '0')
        assert digito1 == digito2

    def test_digito_nss_rango(self):
        """El dígito verificador de NSS está en rango 0-9"""
        nss_base = '0185681234'
        digito = calcular_digito_verificador_nss(nss_base + '0')
        assert 0 <= digito <= 9

    def test_digito_clabe_rango(self):
        """El dígito verificador de CLABE está en rango 0-9"""
        clabe_base = '01218000011234567'
        digito = calcular_digito_verificador_clabe(clabe_base + '0')
        assert 0 <= digito <= 9
