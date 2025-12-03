#!/usr/bin/env python
"""
Script de pruebas completas del backend RRHH
Verifica:
1. Modelos y migraciones
2. Acciones IA registradas
3. Permisos y contexto
4. Integración RAG
5. Flujo de chat
"""
import os
import sys
from datetime import date, timedelta
from decimal import Decimal

# Configurar Django ANTES de importar
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'
os.environ['USE_SQLITE'] = 'True'
os.environ['DEBUG'] = 'True'
os.environ['SECRET_KEY'] = 'test-key-for-testing'

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import django
django.setup()

# Imports después de django.setup()
from django.db import connection
from django.core.exceptions import ValidationError

# ============ CONFIGURACIÓN DE PRUEBAS ============

class TestResult:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []

    def ok(self, msg):
        self.passed += 1
        print(f"  [OK] {msg}")

    def fail(self, msg, error=None):
        self.failed += 1
        self.errors.append((msg, error))
        print(f"  [FAIL] {msg}")
        if error:
            print(f"         Error: {error}")

    def summary(self):
        total = self.passed + self.failed
        print(f"\n{'='*60}")
        print(f"RESUMEN: {self.passed}/{total} pruebas pasaron")
        if self.failed > 0:
            print(f"\nErrores encontrados:")
            for msg, err in self.errors:
                print(f"  - {msg}: {err}")
        print(f"{'='*60}")
        return self.failed == 0

results = TestResult()

# ============ PRUEBA 1: MODELOS Y MIGRACIONES ============

def test_modelos():
    print("\n" + "="*60)
    print("1. PRUEBA DE MODELOS Y MIGRACIONES")
    print("="*60)

    # Verificar que todas las tablas existen
    from django.db import connection
    tables = connection.introspection.table_names()

    tablas_requeridas = [
        'usuarios', 'empresas', 'empleados', 'nomina_periodos',
        'nomina_recibos', 'documentos_rag', 'fragmentos_documento',
        'chat_conversaciones', 'chat_mensajes'
    ]

    for tabla in tablas_requeridas:
        if tabla in tables:
            results.ok(f"Tabla '{tabla}' existe")
        else:
            results.fail(f"Tabla '{tabla}' no encontrada")

    # Verificar campos de baja en empleados
    try:
        from apps.empleados.models import Empleado

        # Verificar que TipoBaja existe
        tipos = [t[0] for t in Empleado.TipoBaja.choices]
        expected_tipos = ['renuncia_voluntaria', 'despido_justificado', 'despido_injustificado']

        for tipo in expected_tipos:
            if tipo in tipos:
                results.ok(f"TipoBaja '{tipo}' disponible")
            else:
                results.fail(f"TipoBaja '{tipo}' no encontrado")

        # Verificar campos nuevos
        campos_baja = ['tipo_baja', 'liquidacion_pagada', 'monto_liquidacion', 'fecha_ultimo_dia_laborado']
        for campo in campos_baja:
            if hasattr(Empleado, campo) or campo in [f.name for f in Empleado._meta.get_fields()]:
                results.ok(f"Campo '{campo}' existe en Empleado")
            else:
                results.fail(f"Campo '{campo}' no existe en Empleado")

    except Exception as e:
        results.fail("Error verificando modelo Empleado", str(e))

    # Verificar modelos RAG
    try:
        from apps.documentos.models import Documento, FragmentoDocumento, TipoDocumento, NivelAcceso
        results.ok("Modelos RAG (Documento, FragmentoDocumento) importados")

        # Verificar TipoDocumento
        tipos_doc = [t[0] for t in TipoDocumento.choices]
        if 'reglamento' in tipos_doc:
            results.ok("TipoDocumento tiene opciones correctas")
        else:
            results.fail("TipoDocumento sin opciones esperadas")

    except Exception as e:
        results.fail("Error importando modelos RAG", str(e))

# ============ PRUEBA 2: ACCIONES IA ============

def test_acciones_ia():
    print("\n" + "="*60)
    print("2. PRUEBA DE ACCIONES IA")
    print("="*60)

    from apps.chat.acciones_registry import ACCIONES_REGISTRADAS

    total_acciones = len(ACCIONES_REGISTRADAS)
    results.ok(f"Total acciones registradas: {total_acciones}")

    if total_acciones >= 39:
        results.ok(f"Cantidad esperada de acciones (>= 39)")
    else:
        results.fail(f"Faltan acciones. Esperadas: 39, Encontradas: {total_acciones}")

    # Verificar acciones de bajas (nuevas)
    acciones_bajas = ['dar_baja_empleado', 'ver_extrabajadores', 'ver_historial_empleado', 'reactivar_empleado']
    for accion in acciones_bajas:
        if accion in ACCIONES_REGISTRADAS:
            results.ok(f"Accion '{accion}' registrada")
        else:
            results.fail(f"Accion '{accion}' NO registrada")

    # Verificar acciones RAG
    acciones_rag = ['buscar_en_documentos', 'listar_documentos', 'consultar_documento']
    for accion in acciones_rag:
        if accion in ACCIONES_REGISTRADAS:
            results.ok(f"Accion RAG '{accion}' registrada")
        else:
            results.fail(f"Accion RAG '{accion}' NO registrada")

    # Verificar estructura de acciones
    for nombre, accion in list(ACCIONES_REGISTRADAS.items())[:5]:
        required_keys = ['nombre', 'descripcion', 'permisos', 'parametros', 'funcion']
        missing = [k for k in required_keys if k not in accion]
        if not missing:
            results.ok(f"Estructura correcta para '{nombre}'")
        else:
            results.fail(f"Faltan keys en '{nombre}'", f"Missing: {missing}")

# ============ PRUEBA 3: DATOS DE PRUEBA ============

def test_datos_prueba():
    print("\n" + "="*60)
    print("3. PRUEBA DE DATOS EXISTENTES")
    print("="*60)

    from apps.empresas.models import Empresa
    from apps.usuarios.models import Usuario
    from apps.empleados.models import Empleado

    # Verificar empresa
    empresa = Empresa.objects.first()
    if empresa:
        results.ok(f"Empresa encontrada: {empresa.razon_social}")
    else:
        results.fail("No hay empresas en la BD")
        return None, None, None

    # Verificar usuario admin
    admin = Usuario.objects.filter(rol='administrador').first()
    if admin:
        results.ok(f"Usuario admin encontrado: {admin.email}")
    else:
        results.fail("No hay usuario administrador")
        return empresa, None, None

    # Verificar empleados
    empleados_count = Empleado.objects.filter(empresa=empresa).count()
    if empleados_count > 0:
        results.ok(f"Empleados encontrados: {empleados_count}")
    else:
        results.fail("No hay empleados en la empresa")

    # Verificar empleados activos vs baja
    activos = Empleado.objects.filter(empresa=empresa, estado='activo').count()
    bajas = Empleado.objects.filter(empresa=empresa, estado='baja').count()
    results.ok(f"Empleados activos: {activos}, En baja: {bajas}")

    empleado = Empleado.objects.filter(empresa=empresa, estado='activo').first()

    return empresa, admin, empleado

# ============ PRUEBA 4: EJECUTAR ACCIONES ============

def test_ejecutar_acciones(empresa, usuario, empleado):
    print("\n" + "="*60)
    print("4. PRUEBA DE EJECUCIÓN DE ACCIONES")
    print("="*60)

    if not empresa or not usuario:
        results.fail("No hay datos suficientes para probar acciones")
        return

    from apps.chat.acciones_registry import ejecutar_accion

    contexto = {
        'empresa_contexto': empresa,
        'empleado_contexto': empleado
    }

    # Test 1: Dashboard empresa
    try:
        resultado = ejecutar_accion('dashboard_empresa', usuario, {}, contexto)
        if resultado.get('success'):
            results.ok(f"dashboard_empresa ejecutado correctamente")
        else:
            results.fail(f"dashboard_empresa falló", resultado.get('error'))
    except Exception as e:
        results.fail("Error ejecutando dashboard_empresa", str(e))

    # Test 2: Buscar empleado
    try:
        if empleado:
            resultado = ejecutar_accion('buscar_empleado', usuario, {'query': empleado.nombre[:3]}, contexto)
            if resultado.get('success'):
                results.ok(f"buscar_empleado ejecutado correctamente")
            else:
                results.fail(f"buscar_empleado falló", resultado.get('error'))
    except Exception as e:
        results.fail("Error ejecutando buscar_empleado", str(e))

    # Test 3: Ver extrabajadores (nueva acción)
    try:
        resultado = ejecutar_accion('ver_extrabajadores', usuario, {}, contexto)
        if resultado.get('success'):
            results.ok(f"ver_extrabajadores ejecutado correctamente")
        else:
            results.fail(f"ver_extrabajadores falló", resultado.get('error'))
    except Exception as e:
        results.fail("Error ejecutando ver_extrabajadores", str(e))

    # Test 4: Listar documentos RAG
    try:
        resultado = ejecutar_accion('listar_documentos', usuario, {}, contexto)
        if resultado.get('success'):
            results.ok(f"listar_documentos ejecutado correctamente")
        else:
            results.fail(f"listar_documentos falló", resultado.get('error'))
    except Exception as e:
        results.fail("Error ejecutando listar_documentos", str(e))

    # Test 5: Ver historial empleado (nueva acción)
    try:
        if empleado:
            resultado = ejecutar_accion('ver_historial_empleado', usuario,
                                       {'empleado_nombre': empleado.nombre}, contexto)
            if resultado.get('success'):
                results.ok(f"ver_historial_empleado ejecutado correctamente")
            else:
                results.fail(f"ver_historial_empleado falló", resultado.get('error'))
    except Exception as e:
        results.fail("Error ejecutando ver_historial_empleado", str(e))

# ============ PRUEBA 5: SERVICIOS RAG ============

def test_servicios_rag(empresa, usuario):
    print("\n" + "="*60)
    print("5. PRUEBA DE SERVICIOS RAG")
    print("="*60)

    if not empresa or not usuario:
        results.fail("No hay datos suficientes para probar RAG")
        return

    # Test ProcesadorDocumentos
    try:
        from apps.documentos.services import ProcesadorDocumentos
        procesador = ProcesadorDocumentos()
        results.ok("ProcesadorDocumentos instanciado")
    except Exception as e:
        results.fail("Error instanciando ProcesadorDocumentos", str(e))

    # Verificar documentos existentes
    try:
        from apps.documentos.models import Documento, FragmentoDocumento

        docs_count = Documento.objects.filter(empresa=empresa).count()
        results.ok(f"Documentos en empresa: {docs_count}")

        if docs_count > 0:
            doc = Documento.objects.filter(empresa=empresa).first()
            frags = FragmentoDocumento.objects.filter(documento=doc).count()
            results.ok(f"Documento '{doc.titulo}' tiene {frags} fragmentos")

            # Verificar si tiene embeddings
            if frags > 0:
                frag = FragmentoDocumento.objects.filter(documento=doc).first()
                if frag.embedding:
                    results.ok(f"Fragmentos tienen embeddings")
                else:
                    results.fail("Fragmentos sin embeddings")
    except Exception as e:
        results.fail("Error verificando documentos RAG", str(e))

    # Test BuscadorSemantico (si hay documentos procesados)
    try:
        from apps.documentos.services import BuscadorSemantico

        # Intentar búsqueda
        resultados = BuscadorSemantico.buscar(
            query="vacaciones",
            usuario=usuario,
            empresa_id=str(empresa.id),
            top_k=3,
            umbral_similitud=0.2
        )

        if resultados is not None:
            results.ok(f"BuscadorSemantico funcionando, {len(resultados)} resultados")
        else:
            results.ok("BuscadorSemantico funcionando (sin resultados)")

    except ImportError as e:
        results.fail("sentence-transformers no instalado", str(e))
    except Exception as e:
        results.fail("Error en BuscadorSemantico", str(e))

# ============ PRUEBA 6: CHAT SERVICE ============

def test_chat_service(empresa, usuario):
    print("\n" + "="*60)
    print("6. PRUEBA DE SERVICIO DE CHAT")
    print("="*60)

    if not empresa or not usuario:
        results.fail("No hay datos suficientes para probar chat")
        return

    try:
        from apps.chat.services import AsistenteRRHH

        # Instanciar sin API key (solo para probar estructura)
        chat = AsistenteRRHH(usuario=usuario, empresa_contexto=empresa)
        results.ok("AsistenteRRHH instanciado")

        # Verificar que tiene los métodos RAG
        if hasattr(chat, '_intentar_respuesta_rag'):
            results.ok("Método _intentar_respuesta_rag existe")
        else:
            results.fail("Método _intentar_respuesta_rag NO existe")

        if hasattr(chat, '_buscar_en_documentos'):
            results.ok("Método _buscar_en_documentos existe")
        else:
            results.fail("Método _buscar_en_documentos NO existe")

        if hasattr(chat, '_responder_con_contexto_rag'):
            results.ok("Método _responder_con_contexto_rag existe")
        else:
            results.fail("Método _responder_con_contexto_rag NO existe")

        # Verificar empresa_contexto
        if chat.empresa_contexto:
            results.ok(f"Empresa contexto establecida: {chat.empresa_contexto.razon_social}")
        else:
            results.fail("Empresa contexto NO establecida")

    except Exception as e:
        results.fail("Error en ChatService", str(e))

# ============ PRUEBA 7: VIEWS Y URLS ============

def test_views_urls():
    print("\n" + "="*60)
    print("7. PRUEBA DE VIEWS Y URLs")
    print("="*60)

    # Verificar DocumentoViewSet
    try:
        from apps.documentos.views import DocumentoViewSet
        results.ok("DocumentoViewSet importado")

        # Verificar acciones
        if hasattr(DocumentoViewSet, 'procesar'):
            results.ok("Acción 'procesar' existe en DocumentoViewSet")
        else:
            results.fail("Acción 'procesar' NO existe")

        if hasattr(DocumentoViewSet, 'estadisticas'):
            results.ok("Acción 'estadisticas' existe en DocumentoViewSet")
        else:
            results.fail("Acción 'estadisticas' NO existe")

    except Exception as e:
        results.fail("Error importando DocumentoViewSet", str(e))

    # Verificar URLs
    try:
        from django.urls import reverse, get_resolver

        # Obtener todas las URLs
        resolver = get_resolver()
        url_names = [pattern.name for pattern in resolver.url_patterns if hasattr(pattern, 'name') and pattern.name]

        results.ok(f"URLs registradas en sistema")

    except Exception as e:
        results.fail("Error verificando URLs", str(e))

# ============ PRUEBA 8: PERMISOS ============

def test_permisos(empresa, usuario):
    print("\n" + "="*60)
    print("8. PRUEBA DE PERMISOS")
    print("="*60)

    if not usuario:
        results.fail("No hay usuario para probar permisos")
        return

    try:
        from apps.chat.permisos import usuario_tiene_permiso

        # Admin debe tener todos los permisos
        if usuario.rol == 'administrador':
            if usuario_tiene_permiso(usuario, ['es_admin']):
                results.ok("Admin tiene permiso es_admin")
            else:
                results.fail("Admin NO tiene permiso es_admin")

            if usuario_tiene_permiso(usuario, ['es_rrhh']):
                results.ok("Admin tiene permiso es_rrhh")
            else:
                results.fail("Admin NO tiene permiso es_rrhh")

        # Verificar obtener_acciones_disponibles
        from apps.chat.acciones_registry import obtener_acciones_disponibles

        acciones = obtener_acciones_disponibles(usuario)
        results.ok(f"Usuario tiene acceso a {len(acciones)} acciones")

        if 'dar_baja_empleado' in acciones:
            results.ok("Admin puede dar_baja_empleado")
        else:
            results.fail("Admin NO puede dar_baja_empleado")

    except Exception as e:
        results.fail("Error verificando permisos", str(e))

# ============ PRUEBA 9: FLUJO COMPLETO DE BAJA ============

def test_flujo_baja(empresa, usuario):
    print("\n" + "="*60)
    print("9. PRUEBA DE FLUJO DE BAJA (sin ejecutar)")
    print("="*60)

    if not empresa or not usuario:
        results.fail("No hay datos suficientes")
        return

    from apps.empleados.models import Empleado
    from apps.chat.acciones_registry import ACCIONES_REGISTRADAS

    # Verificar que la función dar_baja_empleado tiene los imports correctos
    try:
        accion = ACCIONES_REGISTRADAS.get('dar_baja_empleado')
        if accion:
            func = accion['funcion']
            # Verificar que la función existe y es callable
            if callable(func):
                results.ok("Función dar_baja_empleado es callable")
            else:
                results.fail("dar_baja_empleado no es callable")
        else:
            results.fail("dar_baja_empleado no está registrada")
    except Exception as e:
        results.fail("Error verificando dar_baja_empleado", str(e))

    # Verificar que calcular_liquidacion existe en MetricasEmpleado
    try:
        from apps.reportes.services import MetricasEmpleado
        results.ok("MetricasEmpleado disponible")

        # Verificar método calcular_liquidacion
        if hasattr(MetricasEmpleado, 'calcular_liquidacion'):
            results.ok("Método calcular_liquidacion existe en MetricasEmpleado")
        else:
            results.fail("Método calcular_liquidacion no existe")
    except ImportError as e:
        results.fail("MetricasEmpleado NO disponible", str(e))
    except Exception as e:
        results.fail("Error importando MetricasEmpleado", str(e))

    # Verificar flujo de reactivación
    try:
        accion = ACCIONES_REGISTRADAS.get('reactivar_empleado')
        if accion and accion.get('confirmacion_requerida'):
            results.ok("reactivar_empleado requiere confirmación")
        else:
            results.fail("reactivar_empleado debería requerir confirmación")
    except Exception as e:
        results.fail("Error verificando reactivar_empleado", str(e))

# ============ MAIN ============

def main():
    print("="*60)
    print("PRUEBAS COMPLETAS DEL BACKEND RRHH")
    print("="*60)
    print(f"Fecha: {date.today()}")
    print(f"Python: {sys.version}")

    # Ejecutar pruebas
    test_modelos()
    test_acciones_ia()
    empresa, usuario, empleado = test_datos_prueba()
    test_ejecutar_acciones(empresa, usuario, empleado)
    test_servicios_rag(empresa, usuario)
    test_chat_service(empresa, usuario)
    test_views_urls()
    test_permisos(empresa, usuario)
    test_flujo_baja(empresa, usuario)

    # Resumen final
    success = results.summary()

    if success:
        print("\n[SUCCESS] Todas las pruebas pasaron!")
    else:
        print(f"\n[WARNING] {results.failed} prueba(s) fallaron")

    return 0 if success else 1

if __name__ == '__main__':
    sys.exit(main())
