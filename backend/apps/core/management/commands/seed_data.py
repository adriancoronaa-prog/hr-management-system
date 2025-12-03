"""
Management command para generar datos de prueba realistas.
Uso: python manage.py seed_data [--reset] [--minimal]
"""
import random
from datetime import date, timedelta
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.db import transaction


class Command(BaseCommand):
    help = 'Genera datos de prueba realistas para el sistema RRHH'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Elimina datos existentes antes de crear nuevos',
        )
        parser.add_argument(
            '--minimal',
            action='store_true',
            help='Crea solo datos mínimos (1 empresa, 5 empleados)',
        )

    def handle(self, *args, **options):
        if options['reset']:
            self.stdout.write(self.style.WARNING('Eliminando datos existentes...'))
            self._reset_data()

        self.stdout.write(self.style.NOTICE('Generando datos de prueba...'))

        with transaction.atomic():
            if options['minimal']:
                self._crear_datos_minimos()
            else:
                self._crear_datos_completos()

        self.stdout.write(self.style.SUCCESS('[OK] Datos de prueba generados exitosamente'))
        self._mostrar_resumen()

    def _reset_data(self):
        """Elimina datos existentes (excepto superusuario)"""
        from apps.empleados.models import Empleado
        from apps.empresas.models import Empresa
        from apps.usuarios.models import Usuario

        # Importar modelos que existan
        try:
            from apps.vacaciones.models import SolicitudVacaciones, PeriodoVacacional
            SolicitudVacaciones.objects.all().delete()
            PeriodoVacacional.objects.all().delete()
        except Exception:
            pass

        try:
            from apps.nomina.models import PeriodoNomina, ReciboNomina
            ReciboNomina.objects.all().delete()
            PeriodoNomina.objects.all().delete()
        except Exception:
            pass

        try:
            from apps.contratos.models import Contrato, Adenda
            Adenda.objects.all().delete()
            Contrato.objects.all().delete()
        except Exception:
            pass

        try:
            from apps.prestaciones.models import PlanPrestaciones, PrestacionAdicional
            PrestacionAdicional.objects.all().delete()
            PlanPrestaciones.objects.all().delete()
        except Exception:
            pass

        try:
            from apps.desempeno.models import AsignacionKPI, CatalogoKPI
            AsignacionKPI.objects.all().delete()
            CatalogoKPI.objects.all().delete()
        except Exception:
            pass

        Empleado.objects.all().delete()
        Empresa.objects.all().delete()
        Usuario.objects.filter(is_superuser=False).delete()

        self.stdout.write('  Datos eliminados')

    def _crear_datos_minimos(self):
        """Crea conjunto mínimo de datos"""
        empresa = self._crear_empresa_principal()
        usuarios = self._crear_usuarios_base(empresa)
        empleados = self._crear_empleados(empresa, cantidad=5)
        self._crear_contratos(empleados)
        self.stdout.write(f'  [OK] Creados: 1 empresa, {len(usuarios)} usuarios, {len(empleados)} empleados')

    def _crear_datos_completos(self):
        """Crea conjunto completo de datos de prueba"""
        # Empresas
        empresas = self._crear_empresas()
        self.stdout.write(f'  [OK] {len(empresas)} empresas creadas')

        # Usuarios
        usuarios = []
        for empresa in empresas:
            usuarios.extend(self._crear_usuarios_base(empresa))
        self.stdout.write(f'  [OK] {len(usuarios)} usuarios creados')

        # Empleados
        empleados_total = []
        for i, empresa in enumerate(empresas):
            cant = 10 if i == 0 else 6
            empleados = self._crear_empleados(empresa, cantidad=cant)
            empleados_total.extend(empleados)
        self.stdout.write(f'  [OK] {len(empleados_total)} empleados creados')

        # Contratos
        self._crear_contratos(empleados_total)
        self.stdout.write(f'  [OK] Contratos creados')

        # Periodos vacacionales
        self._crear_periodos_vacacionales(empleados_total)
        self.stdout.write(f'  [OK] Períodos vacacionales creados')

        # Vacaciones
        self._crear_vacaciones(empleados_total)
        self.stdout.write(f'  [OK] Solicitudes de vacaciones creadas')

        # Prestaciones
        self._crear_planes_prestaciones(empresas)
        self.stdout.write(f'  [OK] Planes de prestaciones creados')

        # Nómina
        self._crear_periodos_nomina(empresas)
        self.stdout.write(f'  [OK] Períodos de nómina creados')

        # KPIs
        self._crear_kpis(empleados_total[:10])
        self.stdout.write(f'  [OK] KPIs asignados')

    def _crear_empresas(self):
        """Crea las empresas de prueba"""
        from apps.empresas.models import Empresa

        datos_empresas = [
            {
                'razon_social': 'Tactika Soluciones Tecnológicas SA de CV',
                'nombre_comercial': 'Tactika',
                'rfc': 'TST200101ABC',
                'regimen_fiscal': '601',
                'calle': 'Av. Paseo de la Reforma',
                'numero_exterior': '250',
                'numero_interior': 'Piso 15',
                'colonia': 'Juárez',
                'codigo_postal': '06600',
                'municipio': 'Cuauhtémoc',
                'estado': 'CDMX',
                'telefono': '5555551234',
                'email': 'contacto@tactika.mx',
                'representante_legal': 'Juan Pérez López',
            },
            {
                'razon_social': 'Ansead Consultores SC',
                'nombre_comercial': 'Ansead',
                'rfc': 'ACO190515XYZ',
                'regimen_fiscal': '601',
                'calle': 'Insurgentes Sur',
                'numero_exterior': '1602',
                'colonia': 'Crédito Constructor',
                'codigo_postal': '03100',
                'municipio': 'Benito Juárez',
                'estado': 'CDMX',
                'telefono': '5555559876',
                'email': 'info@ansead.com.mx',
                'representante_legal': 'María González Hernández',
            },
            {
                'razon_social': 'CA Seguros y Fianzas SA de CV',
                'nombre_comercial': 'CASeguros',
                'rfc': 'CSF180301DEF',
                'regimen_fiscal': '601',
                'calle': 'Av. Presidente Masaryk',
                'numero_exterior': '101',
                'colonia': 'Polanco',
                'codigo_postal': '11000',
                'municipio': 'Miguel Hidalgo',
                'estado': 'CDMX',
                'telefono': '5555554567',
                'email': 'atencion@caseguros.mx',
                'representante_legal': 'Roberto Sánchez Torres',
            },
        ]

        empresas = []
        for datos in datos_empresas:
            empresa, created = Empresa.objects.get_or_create(
                rfc=datos['rfc'],
                defaults=datos
            )
            empresas.append(empresa)

        return empresas

    def _crear_empresa_principal(self):
        """Crea solo la empresa principal"""
        empresas = self._crear_empresas()
        return empresas[0]

    def _crear_usuarios_base(self, empresa):
        """Crea usuarios para una empresa"""
        from apps.usuarios.models import Usuario

        nombre_limpio = empresa.nombre_comercial.lower().replace(' ', '')

        usuarios_data = [
            {
                'email': f'admin@{nombre_limpio}.mx',
                'username': f'admin_{nombre_limpio}',
                'first_name': 'Administrador',
                'last_name': empresa.nombre_comercial,
                'rol': 'admin',
                'password': 'admin123',
            },
            {
                'email': f'rrhh@{nombre_limpio}.mx',
                'username': f'rrhh_{nombre_limpio}',
                'first_name': 'Recursos',
                'last_name': 'Humanos',
                'rol': 'empleador',
                'password': 'rrhh123',
            },
        ]

        usuarios = []
        for data in usuarios_data:
            password = data.pop('password')
            usuario, created = Usuario.objects.get_or_create(
                email=data['email'],
                defaults={**data, 'is_active': True}
            )
            if created:
                usuario.set_password(password)
                usuario.save()
            usuario.empresas.add(empresa)
            usuarios.append(usuario)

        return usuarios

    def _crear_empleados(self, empresa, cantidad=8):
        """Crea empleados para una empresa"""
        from apps.empleados.models import Empleado
        from apps.usuarios.models import Usuario

        nombres = [
            ('Juan Carlos', 'García', 'López'),
            ('María Fernanda', 'Martínez', 'Hernández'),
            ('Roberto', 'Rodríguez', 'Pérez'),
            ('Ana Sofía', 'González', 'Ramírez'),
            ('Luis Miguel', 'Hernández', 'Flores'),
            ('Patricia', 'López', 'García'),
            ('Carlos Eduardo', 'Pérez', 'Martínez'),
            ('Gabriela', 'Sánchez', 'Torres'),
            ('Miguel Ángel', 'Ramírez', 'Díaz'),
            ('Laura', 'Torres', 'Morales'),
            ('Fernando', 'Díaz', 'Vargas'),
            ('Alejandra', 'Morales', 'Castro'),
        ]

        puestos = [
            ('Director General', 'Dirección', Decimal('85000')),
            ('Gerente de Operaciones', 'Operaciones', Decimal('45000')),
            ('Contador Senior', 'Finanzas', Decimal('35000')),
            ('Desarrollador Full Stack', 'Tecnología', Decimal('40000')),
            ('Analista de RRHH', 'Recursos Humanos', Decimal('25000')),
            ('Ejecutivo de Ventas', 'Comercial', Decimal('22000')),
            ('Diseñador UX/UI', 'Tecnología', Decimal('32000')),
            ('Asistente Administrativo', 'Administración', Decimal('15000')),
            ('Project Manager', 'Operaciones', Decimal('38000')),
            ('Analista Financiero', 'Finanzas', Decimal('28000')),
            ('Soporte Técnico', 'Tecnología', Decimal('18000')),
            ('Recepcionista', 'Administración', Decimal('12000')),
        ]

        empleados = []
        base_date = date.today()
        nombre_limpio = empresa.nombre_comercial.lower().replace(' ', '')

        for i in range(min(cantidad, len(nombres))):
            nombre, ap_paterno, ap_materno = nombres[i]
            puesto, departamento, salario = puestos[i % len(puestos)]

            # Generar datos aleatorios pero válidos
            fecha_nac = base_date - timedelta(days=random.randint(25*365, 55*365))
            fecha_ingreso = base_date - timedelta(days=random.randint(90, 5*365))

            # RFC y CURP simulados (formato válido)
            iniciales = f"{ap_paterno[:2]}{ap_materno[0]}{nombre[0]}".upper()
            fecha_rfc = fecha_nac.strftime('%y%m%d')
            rfc = f"{iniciales}{fecha_rfc}AB{i}"

            sexo = 'M' if i % 2 == 0 else 'F'
            entidad = random.choice(['DF', 'MC', 'JC', 'NL', 'GR'])
            curp = f"{iniciales}{fecha_rfc}{'H' if sexo == 'M' else 'M'}{entidad}RRL{str(i).zfill(2)}"

            nss = f"{random.randint(10,97):02d}{fecha_nac.strftime('%y')}{random.randint(1000,9999):04d}{random.randint(0,9)}"

            email = f"{nombre.split()[0].lower()}.{ap_paterno.lower()}@{nombre_limpio}.mx"
            username = f"emp_{nombre_limpio}_{i}"

            # Crear usuario para el empleado
            usuario, _ = Usuario.objects.get_or_create(
                email=email,
                defaults={
                    'username': username,
                    'first_name': nombre,
                    'last_name': f"{ap_paterno} {ap_materno}",
                    'rol': 'empleado',
                    'is_active': True,
                }
            )
            if not usuario.has_usable_password():
                usuario.set_password('empleado123')
                usuario.save()
            usuario.empresas.add(empresa)

            empleado, created = Empleado.objects.get_or_create(
                empresa=empresa,
                email_corporativo=email,
                defaults={
                    'nombre': nombre,
                    'apellido_paterno': ap_paterno,
                    'apellido_materno': ap_materno,
                    'fecha_nacimiento': fecha_nac,
                    'genero': 'Masculino' if sexo == 'M' else 'Femenino',
                    'rfc': rfc,
                    'curp': curp,
                    'nss_imss': nss,
                    'email_personal': f"{nombre.split()[0].lower()}{random.randint(100,999)}@gmail.com",
                    'telefono_personal': f"55{random.randint(10000000, 99999999)}",
                    'fecha_ingreso': fecha_ingreso,
                    'puesto': puesto,
                    'departamento': departamento,
                    'salario_diario': salario / Decimal('30'),
                    'tipo_contrato': 'indefinido',
                    'estado': 'activo',
                }
            )

            empleados.append(empleado)

        # Asignar jefes
        if len(empleados) > 2:
            for emp in empleados[2:]:
                emp.jefe_directo = empleados[0] if emp.departamento == 'Dirección' else empleados[1]
                emp.save()

        return empleados

    def _crear_contratos(self, empleados):
        """Crea contratos para los empleados"""
        from apps.contratos.models import Contrato

        for empleado in empleados:
            Contrato.objects.get_or_create(
                empleado=empleado,
                estado='vigente',
                defaults={
                    'tipo_contrato': empleado.tipo_contrato or 'indefinido',
                    'fecha_inicio': empleado.fecha_ingreso,
                    'fecha_fin': None if empleado.tipo_contrato == 'indefinido' else empleado.fecha_ingreso + timedelta(days=365),
                    'puesto': empleado.puesto,
                    'salario_diario': empleado.salario_diario,
                    'departamento': empleado.departamento,
                    'jornada': 'completa',
                    'horario': 'Lunes a Viernes 9:00 - 18:00',
                }
            )

    def _crear_periodos_vacacionales(self, empleados):
        """Crea períodos vacacionales para los empleados"""
        from apps.vacaciones.models import PeriodoVacacional

        # Días de vacaciones según antigüedad (Ley Federal del Trabajo 2023)
        dias_por_ano = {1: 12, 2: 14, 3: 16, 4: 18, 5: 20, 6: 22}

        for empleado in empleados:
            fecha_ingreso = empleado.fecha_ingreso
            hoy = date.today()
            anos_trabajados = (hoy - fecha_ingreso).days // 365

            for ano in range(1, min(anos_trabajados + 1, 7)):
                inicio_periodo = fecha_ingreso + timedelta(days=(ano - 1) * 365)
                fin_periodo = fecha_ingreso + timedelta(days=ano * 365 - 1)
                dias_derecho = dias_por_ano.get(ano, 22 + ((ano - 6) // 5) * 2)

                # Algunos días tomados aleatoriamente
                dias_tomados = random.randint(0, min(dias_derecho, 8)) if ano < anos_trabajados else 0

                PeriodoVacacional.objects.get_or_create(
                    empleado=empleado,
                    numero_periodo=ano,
                    defaults={
                        'fecha_inicio_periodo': inicio_periodo,
                        'fecha_fin_periodo': fin_periodo,
                        'dias_derecho': dias_derecho,
                        'dias_tomados': dias_tomados,
                        'fecha_vencimiento': fin_periodo + timedelta(days=365),
                        'es_historico': ano < anos_trabajados,
                    }
                )

    def _crear_vacaciones(self, empleados):
        """Crea solicitudes de vacaciones de ejemplo"""
        from apps.vacaciones.models import SolicitudVacaciones

        estados = ['aprobada', 'aprobada', 'aprobada', 'pendiente', 'rechazada']

        for empleado in empleados[:8]:
            # Una solicitud pasada aprobada
            fecha_inicio = date.today() - timedelta(days=random.randint(60, 180))
            dias = random.randint(3, 7)

            SolicitudVacaciones.objects.get_or_create(
                empleado=empleado,
                fecha_inicio=fecha_inicio,
                defaults={
                    'fecha_fin': fecha_inicio + timedelta(days=dias - 1),
                    'dias_solicitados': dias,
                    'estado': random.choice(estados),
                    'notas': random.choice([
                        'Descanso familiar',
                        'Viaje personal',
                        'Asuntos personales',
                        'Vacaciones de verano',
                        'Dias de descanso',
                    ]),
                }
            )

    def _crear_planes_prestaciones(self, empresas):
        """Crea planes de prestaciones para las empresas"""
        from apps.prestaciones.models import PlanPrestaciones, PrestacionAdicional

        for empresa in empresas:
            # Plan básico
            plan_basico, _ = PlanPrestaciones.objects.get_or_create(
                empresa=empresa,
                nombre='Plan Básico',
                defaults={
                    'descripcion': 'Prestaciones de ley más beneficios básicos',
                    'es_default': True,
                    'activo': True,
                    'vacaciones_dias_extra': 0,
                    'prima_vacacional_porcentaje': 25,
                    'aguinaldo_dias': 15,
                }
            )

            # Agregar vales de despensa al básico
            PrestacionAdicional.objects.get_or_create(
                plan=plan_basico,
                tipo_prestacion='vales_despensa',
                defaults={
                    'nombre': 'Vales de Despensa',
                    'categoria': 'economica',
                    'tipo_valor': 'monto',
                    'valor': '1500',
                    'periodicidad': 'mensual',
                    'activo': True,
                }
            )

            # Plan ejecutivo
            plan_ejecutivo, _ = PlanPrestaciones.objects.get_or_create(
                empresa=empresa,
                nombre='Plan Ejecutivo',
                defaults={
                    'descripcion': 'Prestaciones superiores para mandos medios y altos',
                    'es_default': False,
                    'activo': True,
                    'vacaciones_dias_extra': 5,
                    'prima_vacacional_porcentaje': 35,
                    'aguinaldo_dias': 30,
                }
            )

            # Agregar múltiples prestaciones al ejecutivo
            prestaciones_ejecutivo = [
                ('vales_despensa', 'Vales de Despensa', 'economica', 'monto', '3000', 'mensual'),
                ('sgmm', 'Seguro Gastos Médicos', 'salud', 'texto', 'Cobertura hasta 2M', 'anual'),
                ('fondo_ahorro', 'Fondo de Ahorro', 'economica', 'porcentaje', '13', 'mensual'),
                ('home_office', 'Home Office', 'tiempo', 'texto', '2 días por semana', 'mensual'),
            ]

            for tipo, nombre, cat, tipo_val, valor, period in prestaciones_ejecutivo:
                PrestacionAdicional.objects.get_or_create(
                    plan=plan_ejecutivo,
                    tipo_prestacion=tipo,
                    defaults={
                        'nombre': nombre,
                        'categoria': cat,
                        'tipo_valor': tipo_val,
                        'valor': valor,
                        'periodicidad': period,
                        'activo': True,
                    }
                )

    def _crear_periodos_nomina(self, empresas):
        """Crea períodos de nómina de ejemplo"""
        from apps.nomina.models import PeriodoNomina

        for empresa in empresas:
            hoy = date.today()

            # Crear 3 períodos: anterior cerrado, actual abierto, siguiente pendiente
            for offset in [-1, 0, 1]:
                mes = hoy.month + offset
                ano = hoy.year

                if mes < 1:
                    mes = 12
                    ano -= 1
                elif mes > 12:
                    mes = 1
                    ano += 1

                # Primera quincena
                inicio_q1 = date(ano, mes, 1)
                fin_q1 = date(ano, mes, 15)
                numero_q1 = (mes - 1) * 2 + 1

                estado_q1 = 'pagado' if offset < 0 else ('borrador' if offset == 0 and hoy.day <= 15 else 'borrador')

                PeriodoNomina.objects.get_or_create(
                    empresa=empresa,
                    año=ano,
                    numero_periodo=numero_q1,
                    defaults={
                        'tipo_periodo': 'quincenal',
                        'fecha_inicio': inicio_q1,
                        'fecha_fin': fin_q1,
                        'fecha_pago': fin_q1 + timedelta(days=2),
                        'estado': estado_q1,
                    }
                )

                # Segunda quincena
                inicio_q2 = date(ano, mes, 16)
                if mes == 12:
                    fin_q2 = date(ano, mes, 31)
                else:
                    fin_q2 = date(ano, mes + 1, 1) - timedelta(days=1)
                numero_q2 = mes * 2

                estado_q2 = 'pagado' if offset < 0 else ('borrador' if offset == 0 and hoy.day > 15 else 'borrador')

                PeriodoNomina.objects.get_or_create(
                    empresa=empresa,
                    año=ano,
                    numero_periodo=numero_q2,
                    defaults={
                        'tipo_periodo': 'quincenal',
                        'fecha_inicio': inicio_q2,
                        'fecha_fin': fin_q2,
                        'fecha_pago': fin_q2 + timedelta(days=2),
                        'estado': estado_q2,
                    }
                )

    def _crear_kpis(self, empleados):
        """Crea KPIs de ejemplo"""
        from apps.desempeno.models import CatalogoKPI, AsignacionKPI

        # Crear catálogo de KPIs
        kpis_data = [
            ('Ventas Mensuales', 'ventas', 'moneda', 'Monto de ventas cerradas en el mes'),
            ('Satisfacción Cliente', 'servicio', 'porcentaje', 'Calificación promedio de clientes'),
            ('Tickets Resueltos', 'productividad', 'numero', 'Tickets de soporte resueltos'),
            ('Proyectos Completados', 'productividad', 'numero', 'Proyectos entregados a tiempo'),
            ('Código Revisado', 'calidad', 'numero', 'PRs revisados y aprobados'),
            ('Capacitaciones Impartidas', 'desarrollo', 'numero', 'Sesiones de capacitación'),
        ]

        kpis = []
        for nombre, categoria, tipo, descripcion in kpis_data:
            kpi, _ = CatalogoKPI.objects.get_or_create(
                nombre=nombre,
                defaults={
                    'categoria': categoria,
                    'tipo_medicion': tipo,
                    'descripcion': descripcion,
                    'activo': True,
                }
            )
            kpis.append(kpi)

        # Asignar KPIs a empleados
        hoy = date.today()
        trimestre = (hoy.month - 1) // 3 + 1
        periodo = f"Q{trimestre}-{hoy.year}"

        # Fecha inicio y fin del trimestre
        mes_inicio = (trimestre - 1) * 3 + 1
        fecha_inicio_trim = date(hoy.year, mes_inicio, 1)
        mes_fin = trimestre * 3
        if mes_fin == 12:
            fecha_fin_trim = date(hoy.year, 12, 31)
        else:
            fecha_fin_trim = date(hoy.year, mes_fin + 1, 1) - timedelta(days=1)

        for empleado in empleados[:8]:
            kpi = random.choice(kpis)
            meta = Decimal(str(random.randint(80, 150)))

            AsignacionKPI.objects.get_or_create(
                empleado=empleado,
                kpi_catalogo=kpi,
                periodo=periodo,
                defaults={
                    'meta': meta,
                    'peso': Decimal('100'),
                    'fecha_inicio': fecha_inicio_trim,
                    'fecha_fin': fecha_fin_trim,
                    'valor_logrado': meta * Decimal(str(random.uniform(0.7, 1.2))),
                    'estado': 'activo',
                }
            )

    def _mostrar_resumen(self):
        """Muestra resumen de datos creados"""
        from apps.empresas.models import Empresa
        from apps.empleados.models import Empleado
        from apps.usuarios.models import Usuario

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('======================================='))
        self.stdout.write(self.style.SUCCESS('         RESUMEN DE DATOS              '))
        self.stdout.write(self.style.SUCCESS('======================================='))
        self.stdout.write(f'  Empresas:  {Empresa.objects.count()}')
        self.stdout.write(f'  Usuarios:  {Usuario.objects.count()}')
        self.stdout.write(f'  Empleados: {Empleado.objects.count()}')

        try:
            from apps.contratos.models import Contrato
            self.stdout.write(f'  Contratos: {Contrato.objects.count()}')
        except Exception:
            pass

        try:
            from apps.prestaciones.models import PlanPrestaciones
            self.stdout.write(f'  Planes:    {PlanPrestaciones.objects.count()}')
        except Exception:
            pass

        try:
            from apps.nomina.models import PeriodoNomina
            self.stdout.write(f'  Nominas:   {PeriodoNomina.objects.count()}')
        except Exception:
            pass

        self.stdout.write('')
        self.stdout.write(self.style.WARNING('======================================='))
        self.stdout.write(self.style.WARNING('      CREDENCIALES DE PRUEBA           '))
        self.stdout.write(self.style.WARNING('======================================='))

        for usuario in Usuario.objects.filter(rol__in=['admin', 'empleador']).order_by('email')[:6]:
            pwd = 'admin123' if usuario.rol == 'admin' else 'rrhh123'
            self.stdout.write(f'  {usuario.email}')
            self.stdout.write(f'    Password: {pwd}')
            self.stdout.write(f'    Rol: {usuario.rol}')
            self.stdout.write('')
