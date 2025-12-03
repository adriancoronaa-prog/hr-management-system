"""
Management command para enviar alertas de contratos por vencer.
Debe ejecutarse diariamente via cron o programador de tareas.

Uso:
    python manage.py alertar_contratos_vencimiento
    python manage.py alertar_contratos_vencimiento --dias 30 --enviar-email
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from apps.contratos.models import Contrato


class Command(BaseCommand):
    help = 'Envia alertas de contratos que estan por vencer'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dias',
            type=int,
            default=30,
            help='Dias de anticipacion para alertar (default: 30)'
        )
        parser.add_argument(
            '--enviar-email',
            action='store_true',
            help='Envia emails de alerta a RH'
        )
        parser.add_argument(
            '--actualizar-estados',
            action='store_true',
            help='Actualiza estados de contratos vencidos'
        )

    def handle(self, *args, **options):
        dias = options['dias']
        enviar_email = options['enviar_email']
        actualizar_estados = options['actualizar_estados']

        hoy = timezone.now().date()
        fecha_limite = hoy + timedelta(days=dias)

        self.stdout.write(
            self.style.NOTICE(f'Buscando contratos que vencen antes del {fecha_limite}...')
        )

        # Contratos vigentes que vencen pronto
        contratos_por_vencer = Contrato.objects.filter(
            estado=Contrato.Estado.VIGENTE,
            fecha_fin__isnull=False,
            fecha_fin__lte=fecha_limite,
            fecha_fin__gte=hoy
        ).select_related('empleado', 'empleado__empresa')

        # Contratos ya vencidos pero no actualizados
        contratos_vencidos = Contrato.objects.filter(
            estado=Contrato.Estado.VIGENTE,
            fecha_fin__isnull=False,
            fecha_fin__lt=hoy
        ).select_related('empleado', 'empleado__empresa')

        # Actualizar estados si se solicita
        if actualizar_estados:
            count = 0
            for contrato in contratos_vencidos:
                contrato.actualizar_estado()
                count += 1
            self.stdout.write(
                self.style.SUCCESS(f'Se actualizaron {count} contratos a estado VENCIDO')
            )

        # Procesar alertas
        alertas_30 = []
        alertas_15 = []
        alertas_7 = []

        for contrato in contratos_por_vencer:
            dias_para_vencer = contrato.dias_para_vencer

            # Alerta de 30 dias
            if dias_para_vencer <= 30 and not contrato.alerta_enviada_30:
                alertas_30.append(contrato)
                contrato.alerta_enviada_30 = True
                contrato.save(update_fields=['alerta_enviada_30'])

            # Alerta de 15 dias
            if dias_para_vencer <= 15 and not contrato.alerta_enviada_15:
                alertas_15.append(contrato)
                contrato.alerta_enviada_15 = True
                contrato.save(update_fields=['alerta_enviada_15'])

            # Alerta de 7 dias
            if dias_para_vencer <= 7 and not contrato.alerta_enviada_7:
                alertas_7.append(contrato)
                contrato.alerta_enviada_7 = True
                contrato.save(update_fields=['alerta_enviada_7'])

        # Mostrar resumen
        self.stdout.write('\n' + '=' * 60)
        self.stdout.write(self.style.WARNING('RESUMEN DE ALERTAS DE CONTRATOS'))
        self.stdout.write('=' * 60)

        if alertas_30:
            self.stdout.write(self.style.WARNING(f'\n🔔 Alertas de 30 dias ({len(alertas_30)}):'))
            for c in alertas_30:
                self.stdout.write(
                    f'  - {c.empleado.nombre_completo} ({c.empleado.empresa.razon_social})'
                    f' - Vence: {c.fecha_fin} ({c.dias_para_vencer} dias)'
                )

        if alertas_15:
            self.stdout.write(self.style.WARNING(f'\n⚠️  Alertas de 15 dias ({len(alertas_15)}):'))
            for c in alertas_15:
                self.stdout.write(
                    f'  - {c.empleado.nombre_completo} ({c.empleado.empresa.razon_social})'
                    f' - Vence: {c.fecha_fin} ({c.dias_para_vencer} dias)'
                )

        if alertas_7:
            self.stdout.write(self.style.ERROR(f'\n🚨 Alertas URGENTES de 7 dias ({len(alertas_7)}):'))
            for c in alertas_7:
                self.stdout.write(
                    f'  - {c.empleado.nombre_completo} ({c.empleado.empresa.razon_social})'
                    f' - Vence: {c.fecha_fin} ({c.dias_para_vencer} dias)'
                )

        if not (alertas_30 or alertas_15 or alertas_7):
            self.stdout.write(self.style.SUCCESS('\n✅ No hay nuevas alertas de vencimiento'))

        # Enviar emails si se solicita
        if enviar_email and (alertas_30 or alertas_15 or alertas_7):
            self._enviar_emails(alertas_30, alertas_15, alertas_7)

        # Mostrar contratos vencidos pendientes
        if contratos_vencidos.exists() and not actualizar_estados:
            self.stdout.write(self.style.ERROR(
                f'\n⚠️  Hay {contratos_vencidos.count()} contratos vencidos sin actualizar.'
                f' Usa --actualizar-estados para actualizarlos.'
            ))

        self.stdout.write('\n' + '=' * 60)
        total_alertas = len(alertas_30) + len(alertas_15) + len(alertas_7)
        self.stdout.write(
            self.style.SUCCESS(f'Proceso completado. Total alertas nuevas: {total_alertas}')
        )

    def _enviar_emails(self, alertas_30, alertas_15, alertas_7):
        """Envia emails de alerta a los responsables de RH"""
        try:
            from django.core.mail import send_mail
            from django.conf import settings

            # Agrupar por empresa
            empresas = {}
            for contrato in alertas_30 + alertas_15 + alertas_7:
                empresa = contrato.empleado.empresa
                if empresa.id not in empresas:
                    empresas[empresa.id] = {
                        'empresa': empresa,
                        'contratos': []
                    }
                empresas[empresa.id]['contratos'].append(contrato)

            for empresa_id, data in empresas.items():
                empresa = data['empresa']
                contratos = data['contratos']

                # Buscar email de RH de la empresa
                email_rh = getattr(empresa, 'email_rh', None) or getattr(settings, 'EMAIL_RH_DEFAULT', None)

                if not email_rh:
                    self.stdout.write(
                        self.style.WARNING(f'No hay email de RH para {empresa.razon_social}')
                    )
                    continue

                # Construir mensaje
                mensaje = f"ALERTA DE VENCIMIENTO DE CONTRATOS - {empresa.razon_social}\n\n"
                mensaje += f"Los siguientes contratos estan por vencer:\n\n"

                for c in sorted(contratos, key=lambda x: x.fecha_fin):
                    urgencia = "🚨 URGENTE" if c.dias_para_vencer <= 7 else "⚠️" if c.dias_para_vencer <= 15 else "🔔"
                    mensaje += f"{urgencia} {c.empleado.nombre_completo}\n"
                    mensaje += f"   Tipo: {c.get_tipo_contrato_display()}\n"
                    mensaje += f"   Vence: {c.fecha_fin} ({c.dias_para_vencer} dias)\n\n"

                mensaje += "\nPor favor tome las acciones necesarias.\n"
                mensaje += "\n--\nSistema de RRHH - Grupo CA"

                try:
                    send_mail(
                        subject=f'[ALERTA] Contratos por vencer - {empresa.razon_social}',
                        message=mensaje,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[email_rh],
                        fail_silently=False,
                    )
                    self.stdout.write(
                        self.style.SUCCESS(f'Email enviado a {email_rh} para {empresa.razon_social}')
                    )
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'Error enviando email a {email_rh}: {e}')
                    )

        except ImportError:
            self.stdout.write(
                self.style.ERROR('No se pudo importar send_mail. Verifica la configuracion de email.')
            )
