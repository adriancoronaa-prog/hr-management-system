"""
Comando para cargar tablas fiscales de México (ISR, IMSS, Subsidio)
Datos actualizados para 2024-2025
"""
from decimal import Decimal
from django.core.management.base import BaseCommand
from apps.nomina.models import TablaISR, TablaSubsidio, ParametrosIMSS, ConceptoNomina


class Command(BaseCommand):
    help = 'Carga las tablas fiscales de ISR, subsidio y parámetros IMSS'

    def handle(self, *args, **options):
        self.stdout.write('Cargando datos fiscales...')
        
        self._cargar_tabla_isr_2024()
        self._cargar_subsidio_2024()
        self._cargar_parametros_imss_2024()
        self._cargar_conceptos_nomina()
        
        self.stdout.write(self.style.SUCCESS('Datos fiscales cargados exitosamente'))

    def _cargar_tabla_isr_2024(self):
        """Tabla ISR 2024 - Tarifa mensual Art. 96 LISR"""
        self.stdout.write('  - Tabla ISR mensual 2024...')
        
        # Datos de la tabla mensual 2024
        datos_mensuales = [
            (Decimal('0.01'), Decimal('746.04'), Decimal('0'), Decimal('1.92')),
            (Decimal('746.05'), Decimal('6332.05'), Decimal('14.32'), Decimal('6.40')),
            (Decimal('6332.06'), Decimal('11128.01'), Decimal('371.83'), Decimal('10.88')),
            (Decimal('11128.02'), Decimal('12935.82'), Decimal('893.63'), Decimal('16.00')),
            (Decimal('12935.83'), Decimal('15487.71'), Decimal('1182.88'), Decimal('17.92')),
            (Decimal('15487.72'), Decimal('31236.49'), Decimal('1640.18'), Decimal('21.36')),
            (Decimal('31236.50'), Decimal('49233.00'), Decimal('5004.12'), Decimal('23.52')),
            (Decimal('49233.01'), Decimal('93993.90'), Decimal('9236.89'), Decimal('30.00')),
            (Decimal('93993.91'), Decimal('125325.20'), Decimal('22665.17'), Decimal('32.00')),
            (Decimal('125325.21'), Decimal('375975.61'), Decimal('32691.18'), Decimal('34.00')),
            (Decimal('375975.62'), Decimal('999999999'), Decimal('117912.32'), Decimal('35.00')),
        ]
        
        for lim_inf, lim_sup, cuota, pct in datos_mensuales:
            TablaISR.objects.update_or_create(
                año=2024,
                periodicidad='mensual',
                limite_inferior=lim_inf,
                defaults={
                    'limite_superior': lim_sup,
                    'cuota_fija': cuota,
                    'porcentaje_excedente': pct
                }
            )
        
        # Convertir a quincenal (dividir entre 2)
        self.stdout.write('  - Tabla ISR quincenal 2024...')
        for lim_inf, lim_sup, cuota, pct in datos_mensuales:
            TablaISR.objects.update_or_create(
                año=2024,
                periodicidad='quincenal',
                limite_inferior=(lim_inf / 2).quantize(Decimal('0.01')),
                defaults={
                    'limite_superior': (lim_sup / 2).quantize(Decimal('0.01')) if lim_sup < 999999999 else lim_sup,
                    'cuota_fija': (cuota / 2).quantize(Decimal('0.01')),
                    'porcentaje_excedente': pct
                }
            )
        
        self.stdout.write(self.style.SUCCESS('    Tabla ISR cargada'))

    def _cargar_subsidio_2024(self):
        """Tabla de subsidio al empleo 2024 mensual"""
        self.stdout.write('  - Tabla subsidio al empleo 2024...')
        
        datos_subsidio = [
            (Decimal('0.01'), Decimal('1768.96'), Decimal('407.02')),
            (Decimal('1768.97'), Decimal('2653.38'), Decimal('406.83')),
            (Decimal('2653.39'), Decimal('3472.84'), Decimal('406.62')),
            (Decimal('3472.85'), Decimal('3537.87'), Decimal('392.77')),
            (Decimal('3537.88'), Decimal('4446.15'), Decimal('382.46')),
            (Decimal('4446.16'), Decimal('4717.18'), Decimal('354.23')),
            (Decimal('4717.19'), Decimal('5335.42'), Decimal('324.87')),
            (Decimal('5335.43'), Decimal('6224.67'), Decimal('294.63')),
            (Decimal('6224.68'), Decimal('7113.90'), Decimal('253.54')),
            (Decimal('7113.91'), Decimal('7382.33'), Decimal('217.61')),
            (Decimal('7382.34'), Decimal('999999999'), Decimal('0')),
        ]
        
        for lim_inf, lim_sup, subsidio in datos_subsidio:
            TablaSubsidio.objects.update_or_create(
                año=2024,
                periodicidad='mensual',
                limite_inferior=lim_inf,
                defaults={
                    'limite_superior': lim_sup,
                    'subsidio': subsidio
                }
            )
        
        # Quincenal
        for lim_inf, lim_sup, subsidio in datos_subsidio:
            TablaSubsidio.objects.update_or_create(
                año=2024,
                periodicidad='quincenal',
                limite_inferior=(lim_inf / 2).quantize(Decimal('0.01')),
                defaults={
                    'limite_superior': (lim_sup / 2).quantize(Decimal('0.01')) if lim_sup < 999999999 else lim_sup,
                    'subsidio': (subsidio / 2).quantize(Decimal('0.01'))
                }
            )
        
        self.stdout.write(self.style.SUCCESS('    Tabla subsidio cargada'))

    def _cargar_parametros_imss_2024(self):
        """Parámetros IMSS 2024"""
        self.stdout.write('  - Parámetros IMSS 2024...')
        
        ParametrosIMSS.objects.update_or_create(
            año=2024,
            defaults={
                'uma_diaria': Decimal('108.57'),
                'uma_mensual': Decimal('3300.53'),
                'uma_anual': Decimal('39636.40'),
                'salario_minimo_general': Decimal('248.93'),
                'salario_minimo_frontera': Decimal('374.89'),
                'tope_sbc_veces_uma': 25,
                # Cuotas obreras
                'porc_enf_mat_obrera': Decimal('0.0040'),
                'porc_invalidez_vida_obrera': Decimal('0.00625'),
                'porc_cesantia_vejez_obrera': Decimal('0.01125'),
                # Cuotas patronales
                'porc_riesgo_trabajo': Decimal('0.0054355'),  # Clase II promedio
                'porc_enf_mat_patronal': Decimal('0.0105'),
                'porc_invalidez_vida_patronal': Decimal('0.0175'),
                'porc_cesantia_vejez_patronal': Decimal('0.03150'),
                'porc_guarderias': Decimal('0.01'),
                'porc_infonavit': Decimal('0.05'),
                'cuota_fija_enf_mat': Decimal('0.204'),
                'vigente': True
            }
        )
        
        self.stdout.write(self.style.SUCCESS('    Parámetros IMSS cargados'))

    def _cargar_conceptos_nomina(self):
        """Catálogo de conceptos de nómina estándar"""
        self.stdout.write('  - Conceptos de nómina...')
        
        percepciones = [
            ('P001', '001', 'Sueldo', True, True),
            ('P002', '002', 'Gratificación anual (aguinaldo)', True, True),
            ('P003', '003', 'Participación de utilidades PTU', True, False),
            ('P004', '004', 'Reembolso de gastos médicos', False, False),
            ('P005', '005', 'Fondo de ahorro', False, True),
            ('P006', '019', 'Horas extra', True, True),
            ('P007', '020', 'Prima dominical', True, True),
            ('P008', '021', 'Prima vacacional', True, True),
            ('P009', '022', 'Prima por antigüedad', True, True),
            ('P010', '023', 'Pagos por separación', True, False),
            ('P011', '028', 'Comisiones', True, True),
            ('P012', '029', 'Vales de despensa', False, True),
            ('P013', '038', 'Otros ingresos', True, True),
            ('P014', '039', 'Jubilaciones, pensiones', False, False),
        ]
        
        deducciones = [
            ('D001', '002', 'ISR', True),
            ('D002', '001', 'Seguridad social (IMSS)', True),
            ('D003', '003', 'Aportaciones a retiro', True),
            ('D004', '004', 'Otros', False),
            ('D005', '005', 'Aportaciones INFONAVIT', True),
            ('D006', '006', 'Descuento INFONAVIT', False),
            ('D007', '007', 'Fondo de ahorro', False),
            ('D008', '008', 'Pensión alimenticia', False),
            ('D009', '009', 'Préstamos personales', False),
            ('D010', '010', 'Adelanto de salarios', False),
            ('D011', '014', 'Cuotas sindicales', False),
        ]
        
        for codigo, sat, nombre, gravable, integrable in percepciones:
            ConceptoNomina.objects.update_or_create(
                codigo_interno=codigo,
                defaults={
                    'codigo_sat': sat,
                    'nombre': nombre,
                    'tipo': 'percepcion',
                    'es_gravable': gravable,
                    'es_integrable_sbc': integrable,
                    'activo': True
                }
            )
        
        for codigo, sat, nombre, obligatorio in deducciones:
            ConceptoNomina.objects.update_or_create(
                codigo_interno=codigo,
                defaults={
                    'codigo_sat': sat,
                    'nombre': nombre,
                    'tipo': 'deduccion',
                    'es_obligatorio': obligatorio,
                    'activo': True
                }
            )
        
        self.stdout.write(self.style.SUCCESS('    Conceptos de nómina cargados'))
