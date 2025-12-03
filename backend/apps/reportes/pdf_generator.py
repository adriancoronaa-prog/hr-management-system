"""
Generador de PDFs profesionales para reportes de RRHH
"""
from decimal import Decimal
from datetime import date
from io import BytesIO
from typing import Dict

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable
)
from reportlab.lib.enums import TA_CENTER


class ColoresRRHH:
    """Paleta de colores corporativos"""
    PRIMARIO = colors.HexColor('#1a365d')
    SECUNDARIO = colors.HexColor('#2b6cb0')
    ACENTO = colors.HexColor('#38a169')
    ALERTA = colors.HexColor('#e53e3e')
    WARNING = colors.HexColor('#dd6b20')
    GRIS_CLARO = colors.HexColor('#f7fafc')
    GRIS = colors.HexColor('#718096')
    TEXTO = colors.HexColor('#2d3748')


class GeneradorPDFBase:
    """Clase base para generación de PDFs"""
    
    def __init__(self):
        self.buffer = BytesIO()
        self.styles = getSampleStyleSheet()
        self._configurar_estilos()
    
    def _configurar_estilos(self):
        self.styles.add(ParagraphStyle(
            name='TituloReporte',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=ColoresRRHH.PRIMARIO,
            spaceAfter=20,
            alignment=TA_CENTER,
        ))
        
        self.styles.add(ParagraphStyle(
            name='Subtitulo',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=ColoresRRHH.SECUNDARIO,
            spaceBefore=15,
            spaceAfter=10,
        ))
        
        self.styles.add(ParagraphStyle(
            name='SeccionTitulo',
            parent=self.styles['Heading3'],
            fontSize=12,
            textColor=ColoresRRHH.PRIMARIO,
            spaceBefore=12,
            spaceAfter=8,
        ))
        
        self.styles.add(ParagraphStyle(
            name='TextoNormal',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=ColoresRRHH.TEXTO,
            leading=14,
        ))
        
        self.styles.add(ParagraphStyle(
            name='TextoPequeno',
            parent=self.styles['Normal'],
            fontSize=8,
            textColor=ColoresRRHH.GRIS,
        ))
        
        self.styles.add(ParagraphStyle(
            name='MontoGrande',
            parent=self.styles['Normal'],
            fontSize=18,
            textColor=ColoresRRHH.ACENTO,
            fontName='Helvetica-Bold',
            alignment=TA_CENTER,
        ))
    
    def _crear_tabla_datos(self, datos: list, anchos: list = None) -> Table:
        tabla = Table(datos, colWidths=anchos)
        
        tabla.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), ColoresRRHH.PRIMARIO),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), ColoresRRHH.TEXTO),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, ColoresRRHH.GRIS),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, ColoresRRHH.GRIS_CLARO]),
        ]))
        return tabla
    
    def _crear_caja_metrica(self, titulo: str, valor: str, subtitulo: str = None) -> Table:
        contenido = [
            [Paragraph(titulo, self.styles['TextoPequeno'])],
            [Paragraph(valor, self.styles['MontoGrande'])],
        ]
        if subtitulo:
            contenido.append([Paragraph(subtitulo, self.styles['TextoPequeno'])])
        
        tabla = Table(contenido, colWidths=[2.5*inch])
        tabla.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), ColoresRRHH.GRIS_CLARO),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('BOX', (0, 0), (-1, -1), 1, ColoresRRHH.SECUNDARIO),
        ]))
        return tabla
    
    def _formato_moneda(self, valor) -> str:
        if valor is None:
            return "$0.00"
        return f"${valor:,.2f}"
    
    def _linea_separadora(self) -> HRFlowable:
        return HRFlowable(width="100%", thickness=1, color=ColoresRRHH.GRIS, spaceBefore=10, spaceAfter=10)


class PDFDashboardEmpresa(GeneradorPDFBase):
    """Genera PDF de dashboard de empresa"""
    
    def generar(self, metricas: Dict) -> BytesIO:
        doc = SimpleDocTemplate(
            self.buffer, pagesize=letter,
            rightMargin=0.75*inch, leftMargin=0.75*inch,
            topMargin=0.75*inch, bottomMargin=0.75*inch,
        )
        
        elementos = []
        
        # Encabezado
        empresa = metricas['empresa']
        elementos.append(Paragraph("DASHBOARD EMPRESARIAL", self.styles['TituloReporte']))
        elementos.append(Paragraph(empresa['razon_social'], self.styles['Subtitulo']))
        elementos.append(Paragraph(f"RFC: {empresa['rfc']}", self.styles['TextoNormal']))
        elementos.append(Spacer(1, 20))
        elementos.append(self._linea_separadora())
        
        # Métricas principales
        emp = metricas['empleados']
        caja1 = self._crear_caja_metrica("EMPLEADOS ACTIVOS", str(emp['activos']), f"de {emp['total']} totales")
        caja2 = self._crear_caja_metrica("ANTIGÜEDAD PROMEDIO", f"{emp['antiguedad_promedio_anos']} años")
        caja3 = self._crear_caja_metrica("NÓMINA MENSUAL", self._formato_moneda(emp['nomina_mensual_estimada']))
        
        tabla_metricas = Table([[caja1, caja2, caja3]], colWidths=[2.7*inch]*3)
        tabla_metricas.setStyle(TableStyle([('ALIGN', (0, 0), (-1, -1), 'CENTER')]))
        
        elementos.append(Paragraph("Resumen Ejecutivo", self.styles['SeccionTitulo']))
        elementos.append(tabla_metricas)
        elementos.append(Spacer(1, 20))
        
        # Empleados
        datos = [
            ['Métrica', 'Valor'],
            ['Empleados Activos', str(emp['activos'])],
            ['Salario Diario Promedio', self._formato_moneda(emp['salario_diario_promedio'])],
            ['Salario Mensual Promedio', self._formato_moneda(emp['salario_mensual_promedio'])],
        ]
        elementos.append(Paragraph("Plantilla de Personal", self.styles['SeccionTitulo']))
        elementos.append(self._crear_tabla_datos(datos, [3*inch, 2*inch]))
        elementos.append(Spacer(1, 15))
        
        # Nómina
        nom = metricas['nomina']
        datos = [
            ['Concepto', 'Monto Anual'],
            ['Percepciones Pagadas', self._formato_moneda(nom['total_percepciones_ano'])],
            ['Deducciones Aplicadas', self._formato_moneda(nom['total_deducciones_ano'])],
            ['Neto Pagado', self._formato_moneda(nom['total_neto_pagado_ano'])],
        ]
        elementos.append(Paragraph("Nómina del Año", self.styles['SeccionTitulo']))
        elementos.append(self._crear_tabla_datos(datos, [3*inch, 2*inch]))
        elementos.append(Spacer(1, 15))
        
        # Costos proyectados
        costos = metricas['costos_proyectados']
        datos = [
            ['Concepto', 'Proyección'],
            ['Aguinaldo (Diciembre)', self._formato_moneda(costos['aguinaldo_proyectado'])],
            ['Prima Vacacional', self._formato_moneda(costos['prima_vacacional_proyectada'])],
            ['Costo Anual Estimado', self._formato_moneda(costos['costo_anual_estimado'])],
        ]
        elementos.append(Paragraph("Costos Proyectados", self.styles['SeccionTitulo']))
        elementos.append(self._crear_tabla_datos(datos, [3*inch, 2*inch]))
        
        # Pie
        elementos.append(self._linea_separadora())
        elementos.append(Paragraph(f"Generado el {metricas['fecha_generacion']} | Sistema RRHH", self.styles['TextoPequeno']))
        
        doc.build(elementos)
        self.buffer.seek(0)
        return self.buffer


class PDFDashboardEmpleado(GeneradorPDFBase):
    """Genera PDF de dashboard de empleado"""
    
    def generar(self, metricas: Dict, incluir_liquidacion: bool = False) -> BytesIO:
        doc = SimpleDocTemplate(
            self.buffer, pagesize=letter,
            rightMargin=0.75*inch, leftMargin=0.75*inch,
            topMargin=0.75*inch, bottomMargin=0.75*inch,
        )
        
        elementos = []
        
        # Encabezado
        emp = metricas['empleado']
        elementos.append(Paragraph("REPORTE DE EMPLEADO", self.styles['TituloReporte']))
        elementos.append(Paragraph(emp['nombre_completo'], self.styles['Subtitulo']))
        elementos.append(Paragraph(f"{emp['puesto'] or 'Sin puesto'} | {emp['departamento'] or 'Sin departamento'}", self.styles['TextoNormal']))
        elementos.append(self._linea_separadora())
        
        # Info personal
        ant = metricas['antiguedad']
        datos = [
            ['Dato', 'Valor', 'Dato', 'Valor'],
            ['CURP', emp.get('curp') or 'N/A', 'RFC', emp.get('rfc') or 'N/A'],
            ['NSS (IMSS)', emp.get('nss') or 'N/A', 'Fecha Ingreso', emp['fecha_ingreso']],
            ['Estado', emp['estado'].upper(), 'Antigüedad', ant['descripcion']],
        ]
        elementos.append(Paragraph("Información Personal", self.styles['SeccionTitulo']))
        elementos.append(self._crear_tabla_datos(datos, [1.3*inch, 1.8*inch, 1.3*inch, 1.8*inch]))
        elementos.append(Spacer(1, 15))
        
        # Métricas principales
        sal = metricas['salario']
        caja1 = self._crear_caja_metrica("ANTIGÜEDAD", f"{ant['anos']} años", f"{ant['meses']} meses")
        caja2 = self._crear_caja_metrica("SALARIO DIARIO", self._formato_moneda(sal['salario_diario']))
        caja3 = self._crear_caja_metrica("SALARIO MENSUAL", self._formato_moneda(sal['salario_mensual']))
        
        tabla_metricas = Table([[caja1, caja2, caja3]], colWidths=[2.7*inch]*3)
        tabla_metricas.setStyle(TableStyle([('ALIGN', (0, 0), (-1, -1), 'CENTER')]))
        elementos.append(tabla_metricas)
        elementos.append(Spacer(1, 20))
        
        # Vacaciones
        vac = metricas['vacaciones']
        datos = [
            ['Concepto', 'Valor'],
            ['Días por Ley (Anual)', str(vac['dias_por_ley'])],
            ['Días Tomados (Este Año)', str(vac['dias_tomados_ano'])],
            ['Días Pendientes', str(vac['dias_pendientes'])],
            ['Prima Vacacional', self._formato_moneda(vac['prima_vacacional_monto'])],
        ]
        elementos.append(Paragraph("Vacaciones", self.styles['SeccionTitulo']))
        elementos.append(self._crear_tabla_datos(datos, [3*inch, 2*inch]))
        elementos.append(Spacer(1, 15))
        
        # Prestaciones
        prest = metricas['prestaciones']
        ag = prest['aguinaldo']
        pv = prest['prima_vacacional']
        datos = [
            ['Prestación', 'Cálculo', 'Monto'],
            ['Aguinaldo', f"{ag['dias']} días", self._formato_moneda(ag['monto'])],
            ['Prima Vacacional', f"{pv['dias_vacaciones']} días × {pv['porcentaje']}%", self._formato_moneda(pv['monto'])],
        ]
        elementos.append(Paragraph("Prestaciones de Ley", self.styles['SeccionTitulo']))
        elementos.append(self._crear_tabla_datos(datos, [2*inch, 2.5*inch, 1.5*inch]))
        
        # Liquidación
        if incluir_liquidacion and metricas.get('liquidacion'):
            elementos.append(PageBreak())
            elementos.extend(self._crear_seccion_liquidacion(metricas))
        
        # Pie
        elementos.append(self._linea_separadora())
        elementos.append(Paragraph(f"Generado el {metricas['fecha_generacion']} | Sistema RRHH", self.styles['TextoPequeno']))
        
        doc.build(elementos)
        self.buffer.seek(0)
        return self.buffer
    
    def _crear_seccion_liquidacion(self, metricas: Dict) -> list:
        liq = metricas['liquidacion']
        fin = liq['finiquito']
        liq_det = liq['liquidacion']
        ant = liq['antiguedad']
        
        elementos = [
            Paragraph("CÁLCULO DE LIQUIDACIÓN / FINIQUITO", self.styles['TituloReporte']),
            Paragraph(liq['tipo'], self.styles['Subtitulo']),
            Spacer(1, 10),
        ]
        
        # Info base
        info_base = [
            ['Dato', 'Valor'],
            ['Fecha de Baja', liq['fecha_baja']],
            ['Salario Diario', self._formato_moneda(liq['salario_diario'])],
            ['Salario Diario Integrado', self._formato_moneda(liq['salario_diario_integrado'])],
            ['Antigüedad', f"{ant['anos']} años, {ant['meses']} meses"],
        ]
        elementos.append(self._crear_tabla_datos(info_base, [3*inch, 2*inch]))
        elementos.append(Spacer(1, 15))
        
        # Finiquito
        elementos.append(Paragraph("FINIQUITO (Siempre Aplica)", self.styles['SeccionTitulo']))
        
        datos_finiquito = [
            ['Concepto', 'Monto'],
            ['Aguinaldo Proporcional', self._formato_moneda(fin['aguinaldo_proporcional'])],
            ['Vacaciones Proporcionales', self._formato_moneda(fin['vacaciones_proporcionales_monto'])],
            ['Prima Vacacional (25%)', self._formato_moneda(fin['prima_vacacional'])],
            ['SUBTOTAL FINIQUITO', self._formato_moneda(fin['subtotal_finiquito'])],
        ]
        
        tabla_fin = self._crear_tabla_datos(datos_finiquito, [3.5*inch, 2*inch])
        tabla_fin.setStyle(TableStyle([
            ('BACKGROUND', (0, -1), (-1, -1), ColoresRRHH.SECUNDARIO),
            ('TEXTCOLOR', (0, -1), (-1, -1), colors.white),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ]))
        elementos.append(tabla_fin)
        elementos.append(Spacer(1, 15))
        
        # Liquidación
        if liq_det['aplica']:
            elementos.append(Paragraph("LIQUIDACIÓN (Despido Injustificado)", self.styles['SeccionTitulo']))
            
            datos_liq = [
                ['Concepto', 'Monto'],
                ['Indemnización 3 Meses', self._formato_moneda(liq_det['indemnizacion_3_meses'])],
                ['Indemnización 20 días/año', self._formato_moneda(liq_det['indemnizacion_20_dias_ano'])],
                ['Prima de Antigüedad', self._formato_moneda(liq_det['prima_antiguedad'])],
                ['SUBTOTAL LIQUIDACIÓN', self._formato_moneda(liq_det['subtotal_liquidacion'])],
            ]
            
            tabla_liq = self._crear_tabla_datos(datos_liq, [3.5*inch, 2*inch])
            tabla_liq.setStyle(TableStyle([
                ('BACKGROUND', (0, -1), (-1, -1), ColoresRRHH.WARNING),
                ('TEXTCOLOR', (0, -1), (-1, -1), colors.white),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ]))
            elementos.append(tabla_liq)
            elementos.append(Spacer(1, 15))
        
        # Total
        caja_total = self._crear_caja_metrica("TOTAL A PAGAR", self._formato_moneda(liq['total_a_pagar']), "Finiquito + Liquidación")
        tabla_total = Table([[caja_total]], colWidths=[4*inch])
        tabla_total.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('BACKGROUND', (0, 0), (-1, -1), ColoresRRHH.ACENTO),
        ]))
        elementos.append(tabla_total)
        elementos.append(Spacer(1, 20))
        
        # Nota legal
        nota = """<b>Fundamento Legal:</b><br/>
        • Art. 48 LFT - Indemnización constitucional (3 meses)<br/>
        • Art. 50 LFT - 20 días por año trabajado<br/>
        • Art. 162 LFT - Prima de antigüedad (12 días por año, tope 2 SM)<br/>
        • Art. 79 LFT - Prima vacacional (25% mínimo)<br/>
        • Art. 87 LFT - Aguinaldo (15 días mínimo)"""
        elementos.append(Paragraph(nota, self.styles['TextoPequeno']))
        
        return elementos
