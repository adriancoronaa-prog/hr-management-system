"""
Management command para enviar alertas diarias de documentos por vencer
Uso: python manage.py enviar_alertas_diarias

Configurar en cron para ejecutar diariamente:
0 9 * * * cd /path/to/project && python manage.py enviar_alertas_diarias
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta


class Command(BaseCommand):
    help = 'Envía alertas de documentos próximos a vencer'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dias',
            type=int,
            default=30,
            help='Días de anticipación para alertar (default: 30)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Solo mostrar qué se enviaría sin enviar'
        )

    def handle(self, *args, **options):
        from apps.empleados.models import DocumentoEmpleado
        from apps.notificaciones.services import NotificacionService

        dias = options['dias']
        dry_run = options['dry_run']

        self.stdout.write(f'Buscando documentos que vencen en los próximos {dias} días...')

        fecha_limite = timezone.now().date() + timedelta(days=dias)

        # Buscar documentos próximos a vencer
        documentos = DocumentoEmpleado.objects.filter(
            fecha_vencimiento__isnull=False,
            fecha_vencimiento__lte=fecha_limite,
            fecha_vencimiento__gte=timezone.now().date(),
            estatus='aprobado'
        ).select_related('empleado', 'empleado__empresa', 'empleado__jefe_directo')

        if not documentos.exists():
            self.stdout.write(self.style.SUCCESS('No hay documentos próximos a vencer.'))
            return

        self.stdout.write(f'Encontrados {documentos.count()} documentos por vencer.')

        alertas_enviadas = 0
        errores = 0

        for doc in documentos:
            dias_restantes = (doc.fecha_vencimiento - timezone.now().date()).days

            # Determinar destinatarios
            destinatarios = []

            # Notificar al jefe directo si existe
            if doc.empleado.jefe_directo and doc.empleado.jefe_directo.usuario:
                destinatarios.append(doc.empleado.jefe_directo.usuario)

            # Notificar a RH de la empresa (usuarios con rol rrhh)
            if doc.empleado.empresa:
                from apps.usuarios.models import Usuario
                usuarios_rh = Usuario.objects.filter(
                    empresa=doc.empleado.empresa,
                    rol__in=['rrhh', 'admin']
                )
                destinatarios.extend(list(usuarios_rh))

            # Eliminar duplicados
            destinatarios = list(set(destinatarios))

            if not destinatarios:
                self.stdout.write(
                    self.style.WARNING(
                        f'  Sin destinatarios para documento {doc.nombre} de {doc.empleado.nombre_completo}'
                    )
                )
                continue

            for destinatario in destinatarios:
                if dry_run:
                    self.stdout.write(
                        f'  [DRY-RUN] Enviaría alerta a {destinatario.email}: '
                        f'{doc.nombre} de {doc.empleado.nombre_completo} vence en {dias_restantes} días'
                    )
                else:
                    try:
                        NotificacionService.notificar_alerta_vencimiento(
                            destinatario=destinatario,
                            documento=doc,
                            dias_restantes=dias_restantes
                        )
                        alertas_enviadas += 1
                        self.stdout.write(
                            f'  Alerta enviada a {destinatario.email}: {doc.nombre}'
                        )
                    except Exception as e:
                        errores += 1
                        self.stdout.write(
                            self.style.ERROR(f'  Error enviando a {destinatario.email}: {str(e)}')
                        )

        # Resumen
        self.stdout.write('')
        if dry_run:
            self.stdout.write(self.style.SUCCESS(f'[DRY-RUN] Se habrían enviado alertas para {documentos.count()} documentos'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Alertas enviadas: {alertas_enviadas}'))
            if errores:
                self.stdout.write(self.style.ERROR(f'Errores: {errores}'))
