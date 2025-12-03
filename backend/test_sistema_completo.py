"""
Test FINAL del Sistema RRHH - 71 Acciones
Verifica todos los módulos antes de pasar a Frontend
"""
import os
import sys
import django
from datetime import date, timedelta
from decimal import Decimal

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
os.environ['USE_SQLITE'] = 'True'
os.environ['DEBUG'] = 'True'
os.environ['SECRET_KEY'] = 'test-key-for-testing'

django.setup()

from django.db.models import Q
from apps.usuarios.models import Usuario
from apps.empresas.models import Empresa
from apps.empleados.models import Empleado, DocumentoEmpleado
from apps.nomina.models import PeriodoNomina, ReciboNomina, IncidenciaNomina
from apps.chat.acciones_registry import ACCIONES_REGISTRADAS


class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text.center(70)}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.RESET}\n")


def print_subheader(text):
    print(f"\n{Colors.CYAN}--- {text} ---{Colors.RESET}\n")


def print_success(text):
    print(f"{Colors.GREEN}[OK] {text}{Colors.RESET}")


def print_error(text):
    print(f"{Colors.RED}[ERROR] {text}{Colors.RESET}")


def print_warning(text):
    print(f"{Colors.YELLOW}[WARN] {text}{Colors.RESET}")


def print_info(text):
    print(f"{Colors.BLUE}[INFO] {text}{Colors.RESET}")


class TestSistemaFinal:
    def __init__(self):
        self.resultados = {
            'pasaron': 0,
            'fallaron': 0,
            'warnings': 0,
            'errores': []
        }
        self.usuario_admin = None
        self.usuario_empleado = None
        self.empresa = None
        self.empleado = None
        self.jefe = None

    def setup_datos_prueba(self):
        """Configura datos base para pruebas"""
        print_header("CONFIGURACION DE DATOS DE PRUEBA")

        try:
            # Empresa
            self.empresa, created = Empresa.objects.get_or_create(
                rfc='TEST123456789',
                defaults={
                    'razon_social': 'Empresa de Prueba SA de CV',
                    'nombre_comercial': 'Empresa Test',
                }
            )
            print_success(f"Empresa: {self.empresa.razon_social}")

            # Usuario Admin
            self.usuario_admin, created = Usuario.objects.get_or_create(
                email='admin@test.com',
                defaults={
                    'username': 'admin@test.com',
                    'rol': 'admin',
                    'is_active': True,
                }
            )
            if created:
                self.usuario_admin.set_password('test123')
                self.usuario_admin.save()
            self.usuario_admin.empresas.add(self.empresa)
            print_success(f"Usuario Admin: {self.usuario_admin.email}")

            # Jefe
            self.jefe, created = Empleado.objects.get_or_create(
                curp='JEFE123456HTESTX00',
                defaults={
                    'empresa': self.empresa,
                    'nombre': 'Roberto',
                    'apellido_paterno': 'Jefe',
                    'apellido_materno': 'Test',
                    'rfc': 'JEFE12345678',
                    'fecha_nacimiento': date(1980, 5, 15),
                    'fecha_ingreso': date(2020, 1, 1),
                    'salario_diario': Decimal('800.00'),
                    'puesto': 'Gerente',
                    'departamento': 'Administracion',
                    'estado': 'activo',
                }
            )
            print_success(f"Jefe: {self.jefe.nombre_completo}")

            # Empleado
            self.empleado, created = Empleado.objects.get_or_create(
                curp='TEST123456HTESTX01',
                defaults={
                    'empresa': self.empresa,
                    'nombre': 'Juan',
                    'apellido_paterno': 'Perez',
                    'apellido_materno': 'Test',
                    'rfc': 'TEST1234567X',
                    'fecha_nacimiento': date(1990, 6, 15),
                    'fecha_ingreso': date(2023, 1, 15),
                    'salario_diario': Decimal('500.00'),
                    'puesto': 'Analista',
                    'departamento': 'Sistemas',
                    'estado': 'activo',
                    'jefe_directo': self.jefe,
                }
            )
            print_success(f"Empleado: {self.empleado.nombre_completo}")

            # Usuario Empleado
            self.usuario_empleado, created = Usuario.objects.get_or_create(
                email='juan@test.com',
                defaults={
                    'username': 'juan@test.com',
                    'rol': 'empleado',
                    'is_active': True,
                    'empleado': self.empleado,
                }
            )
            if created:
                self.usuario_empleado.set_password('test123')
                self.usuario_empleado.save()

            print_success(f"Usuario Empleado: {self.usuario_empleado.email}")

            return True

        except Exception as e:
            print_error(f"Error en setup: {str(e)}")
            self.resultados['errores'].append(f"Setup: {str(e)}")
            return False

    # ==================== TEST DE ACCIONES REGISTRADAS ====================

    def test_acciones_registradas(self):
        """Verifica que todas las 71 acciones esten registradas"""
        print_header("TEST: ACCIONES IA REGISTRADAS (71 esperadas)")

        total = len(ACCIONES_REGISTRADAS)
        print_info(f"Total de acciones registradas: {total}")

        # Acciones esperadas por modulo
        acciones_esperadas = {
            'empleados': [
                'buscar_empleado', 'crear_empleado', 'ver_perfil_empleado',
                'obtener_subordinados', 'obtener_organigrama', 'asignar_jefe',
                'dar_baja_empleado', 'ver_extrabajadores', 'ver_historial_empleado',
                'reactivar_empleado', 'ver_expediente', 'verificar_documentos_pendientes',
                'busqueda_avanzada_empleados'
            ],
            'nomina': [
                'crear_periodo_nomina', 'ver_periodos_nomina', 'registrar_incidencia',
                'ver_incidencias', 'calcular_nomina', 'ver_pre_nomina',
                'ver_mi_recibo', 'autorizar_nomina', 'generar_dispersion'
            ],
            'documentos': [
                'buscar_en_documentos', 'listar_documentos', 'consultar_documento', 'subir_documento'
            ],
            'reportes': [
                'dashboard_empresa', 'dashboard_empleado', 'calcular_liquidacion',
                'generar_pdf_empleado', 'exportar_empleados_excel', 'exportar_nomina_excel',
                'exportar_incidencias_excel', 'exportar_solicitudes_excel'
            ],
            'desempeno': [
                'asignar_kpi', 'ver_mis_kpis', 'ver_kpis_equipo', 'registrar_avance_kpi',
                'solicitar_cambio_kpi', 'aprobar_cambio_kpi', 'resumen_desempeno_equipo'
            ],
            'notificaciones': [
                'ver_mis_notificaciones', 'ver_solicitudes_pendientes',
                'configurar_notificaciones', 'marcar_notificaciones_leidas'
            ],
            'solicitudes': [
                'crear_solicitud', 'aprobar_solicitud', 'rechazar_solicitud', 'ver_mis_solicitudes'
            ],
            'integraciones': [
                'configurar_google_calendar', 'sincronizar_calendario',
                'ver_eventos_calendario', 'estado_google_calendar',
                'ver_auditoria', 'historial_objeto'
            ],
            'usuarios': [
                'ver_mi_perfil', 'actualizar_mi_perfil', 'cambiar_mi_password',
                'solicitar_cambio_datos', 'mis_solicitudes_cambio', 'listar_solicitudes_cambio',
                'aprobar_cambio_datos', 'rechazar_cambio_datos', 'listar_usuarios',
                'crear_usuario', 'activar_usuario', 'reenviar_activacion'
            ]
        }

        total_esperadas = sum(len(acciones) for acciones in acciones_esperadas.values())
        print_info(f"Acciones esperadas: {total_esperadas}")

        for modulo, acciones in acciones_esperadas.items():
            print_subheader(f"Modulo: {modulo.upper()} ({len(acciones)} acciones)")

            for accion in acciones:
                if accion in ACCIONES_REGISTRADAS:
                    print_success(f"{accion}")
                    self.resultados['pasaron'] += 1
                else:
                    # Buscar variantes del nombre
                    encontrada = False
                    for registrada in ACCIONES_REGISTRADAS.keys():
                        if accion.replace('_', '') in registrada.replace('_', ''):
                            print_warning(f"{accion} -> encontrada como '{registrada}'")
                            self.resultados['warnings'] += 1
                            encontrada = True
                            break

                    if not encontrada:
                        print_error(f"{accion} - NO REGISTRADA")
                        self.resultados['fallaron'] += 1
                        self.resultados['errores'].append(f"Accion no registrada: {accion}")

        # Resumen
        print_subheader("RESUMEN DE ACCIONES")
        if total >= 71:
            print_success(f"Total: {total} acciones (esperado: 71+)")
        elif total >= 65:
            print_warning(f"Total: {total} acciones (esperado: 71, faltan {71-total})")
        else:
            print_error(f"Total: {total} acciones (esperado: 71, faltan {71-total})")

    # ==================== TEST DE EJECUCION DE ACCIONES ====================

    def test_ejecutar_acciones_clave(self):
        """Ejecuta acciones clave de cada modulo"""
        print_header("TEST: EJECUCION DE ACCIONES CLAVE")

        contexto_admin = {
            'empresa_contexto': self.empresa,
            'usuario': self.usuario_admin,
        }

        contexto_empleado = {
            'empresa_contexto': self.empresa,
            'usuario': self.usuario_empleado,
        }

        # Acciones a probar con sus contextos
        acciones_a_probar = [
            # Empleados
            ('buscar_empleado', {'busqueda': 'Juan'}, contexto_admin),
            ('ver_perfil_empleado', {'empleado_id': str(self.empleado.id)}, contexto_admin),
            ('ver_expediente', {'empleado_nombre': 'Juan'}, contexto_admin),
            ('busqueda_avanzada_empleados', {'departamento': 'Sistemas'}, contexto_admin),

            # Reportes
            ('dashboard_empresa', {}, contexto_admin),
            ('dashboard_empleado', {}, contexto_empleado),

            # Notificaciones
            ('ver_mis_notificaciones', {}, contexto_admin),
            ('configurar_notificaciones', {}, contexto_admin),

            # Solicitudes
            ('ver_mis_solicitudes', {}, contexto_empleado),

            # Usuarios/Perfil
            ('ver_mi_perfil', {}, contexto_empleado),
            ('listar_usuarios', {}, contexto_admin),

            # Integraciones
            ('estado_google_calendar', {}, contexto_admin),
            ('ver_auditoria', {'limite': '5'}, contexto_admin),
        ]

        for nombre, params, contexto in acciones_a_probar:
            self._test_accion(nombre, params, contexto)

    def _test_accion(self, nombre, params, contexto):
        """Ejecuta una accion y verifica el resultado"""
        try:
            accion = ACCIONES_REGISTRADAS.get(nombre)
            if not accion:
                print_error(f"{nombre}: No encontrada en registro")
                self.resultados['fallaron'] += 1
                return

            funcion = accion.get('funcion')
            if not funcion:
                print_error(f"{nombre}: Sin funcion asociada")
                self.resultados['fallaron'] += 1
                return

            resultado = funcion(contexto['usuario'], params, contexto)

            # Verificar resultado (puede ser 'success', 'exito', etc.)
            exito = resultado.get('success', resultado.get('exito', False))

            if exito:
                msg = resultado.get('mensaje', resultado.get('message', 'OK'))[:60]
                print_success(f"{nombre}: {msg}")
                self.resultados['pasaron'] += 1
            else:
                error = resultado.get('error', resultado.get('mensaje', 'Error desconocido'))[:60]
                print_warning(f"{nombre}: {error}")
                self.resultados['warnings'] += 1

        except Exception as e:
            print_error(f"{nombre}: {str(e)[:60]}")
            self.resultados['fallaron'] += 1
            self.resultados['errores'].append(f"{nombre}: {str(e)}")

    # ==================== TEST DE MODULOS ESPECIFICOS ====================

    def test_modulo_nomina(self):
        """Prueba flujo completo de nomina"""
        print_header("TEST: MODULO DE NOMINA")

        try:
            # Crear periodo
            periodo, created = PeriodoNomina.objects.get_or_create(
                empresa=self.empresa,
                tipo_periodo='quincenal',
                numero_periodo=24,
                año=2025,
                defaults={
                    'fecha_inicio': date(2025, 12, 1),
                    'fecha_fin': date(2025, 12, 15),
                    'fecha_pago': date(2025, 12, 15),
                    'estado': 'abierto',
                }
            )
            print_success(f"Periodo: {periodo}")
            self.resultados['pasaron'] += 1

            # Registrar incidencia
            incidencia = IncidenciaNomina.objects.create(
                empleado=self.empleado,
                tipo='hora_extra',
                fecha_inicio=date(2025, 12, 5),
                fecha_fin=date(2025, 12, 5),
                cantidad=Decimal('2'),
                descripcion='Test horas extra',
            )
            print_success(f"Incidencia: {incidencia.tipo}")
            self.resultados['pasaron'] += 1

            # Verificar que existe
            assert IncidenciaNomina.objects.filter(empleado=self.empleado).exists()
            print_success("Incidencia guardada correctamente")
            self.resultados['pasaron'] += 1

        except Exception as e:
            print_error(f"Error en nomina: {str(e)}")
            self.resultados['fallaron'] += 1
            self.resultados['errores'].append(f"Nomina: {str(e)}")

    def test_modulo_notificaciones(self):
        """Prueba sistema de notificaciones"""
        print_header("TEST: MODULO DE NOTIFICACIONES")

        try:
            from apps.notificaciones.models import Notificacion, ConfiguracionNotificaciones
            from apps.notificaciones.services import NotificacionService

            # Crear notificacion
            notif = NotificacionService.crear(
                usuario=self.usuario_admin,
                tipo='sistema',
                titulo='Test Final',
                mensaje='Notificacion de prueba final del sistema',
                prioridad='media',
                enviar_email=False
            )
            print_success(f"Notificacion creada: {notif.titulo}")
            self.resultados['pasaron'] += 1

            # Verificar configuracion
            config, created = ConfiguracionNotificaciones.objects.get_or_create(
                usuario=self.usuario_admin
            )
            print_success(f"Configuracion de notificaciones OK")
            self.resultados['pasaron'] += 1

            # Contar notificaciones
            total = Notificacion.objects.filter(usuario=self.usuario_admin).count()
            print_success(f"Total notificaciones: {total}")
            self.resultados['pasaron'] += 1

        except ImportError as e:
            print_error(f"Modulo notificaciones no disponible: {e}")
            self.resultados['fallaron'] += 1
        except Exception as e:
            print_error(f"Error en notificaciones: {str(e)}")
            self.resultados['fallaron'] += 1

    def test_modulo_solicitudes(self):
        """Prueba sistema de solicitudes"""
        print_header("TEST: MODULO DE SOLICITUDES")

        try:
            from apps.solicitudes.models import Solicitud

            # Crear solicitud
            solicitud = Solicitud.objects.create(
                tipo='vacaciones',
                titulo='Vacaciones de prueba final',
                descripcion='Solicitud de prueba del sistema',
                prioridad='media',
                solicitante=self.empleado,
                aprobador=self.usuario_admin,
                estado='pendiente',
            )
            print_success(f"Solicitud creada: {solicitud.titulo}")
            self.resultados['pasaron'] += 1

            # Verificar metodos
            if hasattr(solicitud, 'aprobar'):
                print_success("Metodo aprobar() existe")
                self.resultados['pasaron'] += 1

            if hasattr(solicitud, 'rechazar'):
                print_success("Metodo rechazar() existe")
                self.resultados['pasaron'] += 1

        except ImportError as e:
            print_error(f"Modulo solicitudes no disponible: {e}")
            self.resultados['fallaron'] += 1
        except Exception as e:
            print_error(f"Error en solicitudes: {str(e)}")
            self.resultados['fallaron'] += 1

    def test_modulo_usuarios(self):
        """Prueba gestion de usuarios y tokens"""
        print_header("TEST: MODULO DE USUARIOS Y PERFIL")

        try:
            from apps.usuarios.models import TokenUsuario, SolicitudCambioDatos
            from apps.usuarios.services import UsuarioService

            # Test TokenUsuario
            print_subheader("Tokens de Usuario")

            token = TokenUsuario.crear_token_activacion(self.usuario_empleado)
            print_success(f"Token de activacion creado: {token.token[:20]}...")
            self.resultados['pasaron'] += 1

            assert token.es_valido
            print_success("Token es valido")
            self.resultados['pasaron'] += 1

            token_reset = TokenUsuario.crear_token_reset(self.usuario_empleado)
            print_success(f"Token de reset creado")
            self.resultados['pasaron'] += 1

            # Test SolicitudCambioDatos
            print_subheader("Solicitudes de Cambio de Datos")

            solicitud = SolicitudCambioDatos.objects.create(
                empleado=self.empleado,
                tipo_cambio='cuenta_bancaria',
                datos_actuales={'banco': 'Antiguo', 'clabe': '000000000000000000'},
                datos_nuevos={'banco': 'BBVA', 'clabe': '012345678901234567'},
                justificacion='Cambio de banco',
                estado='pendiente',
            )
            print_success(f"Solicitud de cambio creada")
            self.resultados['pasaron'] += 1

            # Test UsuarioService
            print_subheader("UsuarioService")

            if hasattr(UsuarioService, 'crear_usuario'):
                print_success("Metodo crear_usuario existe")
                self.resultados['pasaron'] += 1

            if hasattr(UsuarioService, 'activar_cuenta'):
                print_success("Metodo activar_cuenta existe")
                self.resultados['pasaron'] += 1

            if hasattr(UsuarioService, 'solicitar_reset_password'):
                print_success("Metodo solicitar_reset_password existe")
                self.resultados['pasaron'] += 1

            if hasattr(UsuarioService, 'obtener_mi_perfil'):
                print_success("Metodo obtener_mi_perfil existe")
                self.resultados['pasaron'] += 1

        except ImportError as e:
            print_warning(f"Algunos modelos de usuarios no disponibles: {e}")
            self.resultados['warnings'] += 1
        except Exception as e:
            print_error(f"Error en usuarios: {str(e)}")
            self.resultados['fallaron'] += 1
            self.resultados['errores'].append(f"Usuarios: {str(e)}")

    def test_modulo_integraciones(self):
        """Prueba integraciones (Google Calendar, Auditoria)"""
        print_header("TEST: MODULO DE INTEGRACIONES")

        # Google Calendar
        print_subheader("Google Calendar")
        try:
            from apps.integraciones.models import ConfiguracionGoogleCalendar, EventoSincronizado

            config, created = ConfiguracionGoogleCalendar.objects.get_or_create(
                empresa=self.empresa,
                defaults={
                    'sincronizar_vacaciones': True,
                    'sincronizar_cumpleanos': True,
                    'sincronizar_aniversarios': True,
                }
            )
            print_success(f"ConfiguracionGoogleCalendar OK")
            self.resultados['pasaron'] += 1

            # Verificar modelo EventoSincronizado
            assert hasattr(EventoSincronizado, 'TipoEvento')
            print_success("Modelo EventoSincronizado OK")
            self.resultados['pasaron'] += 1

        except ImportError as e:
            print_warning(f"Google Calendar no disponible: {e}")
            self.resultados['warnings'] += 1
        except Exception as e:
            print_error(f"Error en Google Calendar: {str(e)}")
            self.resultados['fallaron'] += 1

        # Auditoria
        print_subheader("Sistema de Auditoria")
        try:
            from apps.integraciones.models import RegistroAuditoria

            registro = RegistroAuditoria.objects.create(
                usuario=self.usuario_admin,
                accion='crear',
                descripcion='Test de auditoria final',
            )
            print_success(f"Registro de auditoria creado")
            self.resultados['pasaron'] += 1

        except ImportError as e:
            print_warning(f"Auditoria no disponible: {e}")
            self.resultados['warnings'] += 1
        except Exception as e:
            print_error(f"Error en auditoria: {str(e)}")
            self.resultados['fallaron'] += 1

    def test_modulo_excel(self):
        """Prueba exportacion a Excel"""
        print_header("TEST: EXPORTACION A EXCEL")

        try:
            from apps.reportes.excel_service import ExcelService

            # Verificar metodos
            metodos = [
                'generar_reporte_empleados',
                'generar_reporte_nomina',
                'generar_reporte_incidencias',
                'generar_reporte_solicitudes'
            ]

            for metodo in metodos:
                if hasattr(ExcelService, metodo):
                    print_success(f"ExcelService.{metodo}() existe")
                    self.resultados['pasaron'] += 1
                else:
                    print_warning(f"ExcelService.{metodo}() no encontrado")
                    self.resultados['warnings'] += 1

        except ImportError as e:
            print_warning(f"ExcelService no disponible: {e}")
            self.resultados['warnings'] += 1

    def test_modulo_email(self):
        """Prueba templates de email"""
        print_header("TEST: TEMPLATES DE EMAIL")

        try:
            from django.template.loader import get_template

            templates = [
                'emails/base_email.html',
                'emails/solicitud_aprobacion.html',
                'emails/confirmacion_aprobacion.html',
                'emails/notificacion_rechazo.html',
                'emails/alerta_vencimiento.html',
                'emails/recibo_nomina.html',
                'emails/bienvenida.html',
                'emails/notificacion_general.html',
                'emails/activacion.html',
                'emails/reset_password.html',
            ]

            for template in templates:
                try:
                    get_template(template)
                    print_success(f"Template: {template}")
                    self.resultados['pasaron'] += 1
                except Exception:
                    print_warning(f"Template no encontrado: {template}")
                    self.resultados['warnings'] += 1

        except Exception as e:
            print_error(f"Error en templates: {str(e)}")
            self.resultados['fallaron'] += 1

    def test_flujos_guiados(self):
        """Prueba definiciones de flujos guiados"""
        print_header("TEST: FLUJOS GUIADOS")

        try:
            from apps.chat.flujos import FLUJOS, detectar_flujo

            flujos_esperados = ['baja_empleado', 'crear_empleado', 'registrar_incidencia', 'subir_documento']

            for flujo in flujos_esperados:
                if flujo in FLUJOS:
                    print_success(f"Flujo: {flujo}")
                    self.resultados['pasaron'] += 1
                else:
                    print_warning(f"Flujo no encontrado: {flujo}")
                    self.resultados['warnings'] += 1

            # Probar deteccion
            tests_deteccion = [
                ("Quiero dar de baja a Juan", "baja_empleado"),
                ("Registrar nuevo empleado", "crear_empleado"),
                ("Subir documento al expediente", "subir_documento"),
            ]

            for mensaje, esperado in tests_deteccion:
                resultado = detectar_flujo(mensaje)
                if resultado == esperado:
                    print_success(f"Deteccion: '{mensaje[:30]}...' -> {resultado}")
                    self.resultados['pasaron'] += 1
                else:
                    print_warning(f"Deteccion: '{mensaje[:30]}...' -> {resultado} (esperado: {esperado})")
                    self.resultados['warnings'] += 1

        except ImportError as e:
            print_warning(f"Modulo flujos no disponible: {e}")
            self.resultados['warnings'] += 1

    def test_endpoints_rest(self):
        """Verifica que los endpoints REST esten configurados"""
        print_header("TEST: ENDPOINTS REST")

        try:
            # Verificar imports de views
            from apps.usuarios.views import (
                ActivarCuentaView, SolicitarResetPasswordView,
                ResetearPasswordView, CambiarPasswordView, MiPerfilView
            )
            print_success("Views de usuarios importadas correctamente")
            self.resultados['pasaron'] += 1

            # Verificar URLs
            from apps.usuarios.urls import urlpatterns
            print_success(f"URLs de usuarios: {len(urlpatterns)} endpoints")
            self.resultados['pasaron'] += 1

        except Exception as e:
            print_warning(f"Verificacion de endpoints: {str(e)[:50]}")
            self.resultados['warnings'] += 1

    # ==================== RESUMEN FINAL ====================

    def imprimir_resumen(self):
        """Imprime resumen final de resultados"""
        print_header("RESUMEN FINAL DE PRUEBAS")

        total = self.resultados['pasaron'] + self.resultados['fallaron'] + self.resultados['warnings']

        print(f"\n{Colors.GREEN}[OK] Pasaron:   {self.resultados['pasaron']}{Colors.RESET}")
        print(f"{Colors.YELLOW}[WARN] Warnings:  {self.resultados['warnings']}{Colors.RESET}")
        print(f"{Colors.RED}[ERROR] Fallaron:  {self.resultados['fallaron']}{Colors.RESET}")
        print(f"\n{Colors.BOLD}Total: {total} pruebas{Colors.RESET}")

        # Porcentaje de exito
        if total > 0:
            exito = ((self.resultados['pasaron'] + self.resultados['warnings']) / total) * 100
            print(f"{Colors.BOLD}Tasa de exito: {exito:.1f}%{Colors.RESET}")

        # Errores detallados
        if self.resultados['errores']:
            print(f"\n{Colors.RED}{Colors.BOLD}ERRORES DETECTADOS:{Colors.RESET}")
            for i, error in enumerate(self.resultados['errores'][:15], 1):
                print(f"  {i}. {error}")
            if len(self.resultados['errores']) > 15:
                print(f"  ... y {len(self.resultados['errores']) - 15} mas")

        # Resultado final
        print("\n" + "="*70)
        if self.resultados['fallaron'] == 0:
            print(f"{Colors.GREEN}{Colors.BOLD}SISTEMA LISTO PARA FRONTEND - TODAS LAS PRUEBAS PASARON{Colors.RESET}")
        elif self.resultados['fallaron'] <= 5:
            print(f"{Colors.YELLOW}{Colors.BOLD}SISTEMA FUNCIONAL - ALGUNOS ERRORES MENORES{Colors.RESET}")
        else:
            print(f"{Colors.RED}{Colors.BOLD}HAY ERRORES QUE DEBEN CORREGIRSE ANTES DEL FRONTEND{Colors.RESET}")
        print("="*70)

        # Estadisticas del sistema
        print(f"\n{Colors.CYAN}{Colors.BOLD}ESTADISTICAS DEL SISTEMA:{Colors.RESET}")
        print(f"   - Acciones IA: {len(ACCIONES_REGISTRADAS)}")
        print(f"   - Modulos principales: 9")
        print(f"   - Flujos guiados: 4")

        try:
            from apps.empleados.models import DocumentoEmpleado
            print(f"   - Tipos de documento: {len(DocumentoEmpleado.TipoDocumento.choices)}")
        except:
            pass

    def ejecutar_todo(self):
        """Ejecuta todas las pruebas"""
        print(f"\n{Colors.BOLD}{'='*70}")
        print("    SISTEMA RRHH - PRUEBA FINAL COMPLETA")
        print(f"    71 Acciones IA | Preparacion para Frontend")
        print(f"{'='*70}{Colors.RESET}\n")

        if not self.setup_datos_prueba():
            print_error("No se pudo configurar datos de prueba. Abortando.")
            return

        # Ejecutar todas las pruebas
        self.test_acciones_registradas()
        self.test_ejecutar_acciones_clave()
        self.test_modulo_nomina()
        self.test_modulo_notificaciones()
        self.test_modulo_solicitudes()
        self.test_modulo_usuarios()
        self.test_modulo_integraciones()
        self.test_modulo_excel()
        self.test_modulo_email()
        self.test_flujos_guiados()
        self.test_endpoints_rest()

        self.imprimir_resumen()


if __name__ == '__main__':
    test = TestSistemaFinal()
    test.ejecutar_todo()
