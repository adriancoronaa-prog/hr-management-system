// Nomina types

export interface PeriodoNomina {
  id: string;
  empresa: string;
  tipo_periodo: "semanal" | "quincenal" | "mensual";
  tipo_periodo_display?: string;
  numero_periodo: number;
  año: number;
  fecha_inicio: string;
  fecha_fin: string;
  fecha_pago?: string;
  estado: "borrador" | "calculado" | "autorizado" | "pagado" | "timbrado" | "cancelado";
  estado_display?: string;

  // Totales
  total_percepciones?: number;
  total_deducciones?: number;
  total_neto?: number;
  total_empleados?: number;

  // Auditoria
  fecha_calculo?: string;
  calculado_por?: string;
  fecha_autorizacion?: string;
  autorizado_por?: string;

  created_at?: string;
  updated_at?: string;
}

export interface ReciboNomina {
  id: string;
  periodo: string;
  periodo_info?: {
    tipo_periodo_display: string;
    numero_periodo: number;
    año: number;
    fecha_inicio: string;
    fecha_fin: string;
  };
  empleado: string;
  empleado_nombre?: string;
  empleado_puesto?: string;

  // Salario
  salario_diario: number;
  salario_base_cotizacion: number;
  dias_trabajados: number;
  dias_pagados?: number;

  // Totales
  total_percepciones: number;
  total_percepciones_gravadas?: number;
  total_percepciones_exentas?: number;
  total_deducciones: number;
  neto_a_pagar: number;

  // ISR
  base_gravable_isr?: number;
  isr_antes_subsidio?: number;
  subsidio_aplicado?: number;
  isr_retenido?: number;

  // IMSS
  cuota_imss_obrera?: number;
  cuota_imss_patronal?: number;

  // CFDI
  uuid_fiscal?: string;
  fecha_timbrado?: string;
  xml_cfdi?: string;
  pdf_cfdi?: string;

  estado: "borrador" | "calculado" | "timbrado" | "cancelado";
  estado_display?: string;

  created_at?: string;
}

export interface DetalleReciboNomina {
  id: string;
  recibo: string;
  concepto: string;
  concepto_nombre?: string;
  concepto_codigo?: string;
  tipo: "percepcion" | "deduccion" | "otro_pago";
  cantidad?: number;
  valor_unitario?: number;
  importe_gravado?: number;
  importe_exento?: number;
  importe_total: number;
}

export interface IncidenciaNomina {
  id: string;
  empleado: string;
  empleado_nombre?: string;
  periodo?: string;
  periodo_info?: string;
  tipo: "falta" | "incapacidad" | "vacaciones" | "permiso_cg" | "permiso_sg" | "horas_extra" | "bono" | "comision" | "descuento" | "prestamo" | "otro";
  tipo_display?: string;
  fecha_inicio: string;
  fecha_fin?: string;
  cantidad?: number;
  monto?: number;
  descripcion?: string;
  estado: "pendiente" | "aplicada" | "cancelada";
  created_at?: string;
}

export interface ResumenNomina {
  periodo: PeriodoNomina;
  total_empleados: number;
  total_percepciones: number;
  total_deducciones: number;
  total_neto: number;
  desglose_isr: number;
  desglose_imss: number;
  recibos: ReciboNomina[];
}

export const TIPO_PERIODO_OPTIONS = [
  { value: "semanal", label: "Semanal" },
  { value: "quincenal", label: "Quincenal" },
  { value: "mensual", label: "Mensual" },
];

export const ESTADO_PERIODO_OPTIONS = [
  { value: "borrador", label: "Borrador", color: "warm" },
  { value: "calculado", label: "Calculado", color: "amber" },
  { value: "autorizado", label: "Autorizado", color: "blue" },
  { value: "pagado", label: "Pagado", color: "green" },
  { value: "timbrado", label: "Timbrado", color: "green" },
  { value: "cancelado", label: "Cancelado", color: "red" },
];

export const TIPO_INCIDENCIA_OPTIONS = [
  { value: "falta", label: "Falta", tipo: "deduccion" },
  { value: "incapacidad", label: "Incapacidad", tipo: "deduccion" },
  { value: "vacaciones", label: "Vacaciones", tipo: "neutral" },
  { value: "permiso_cg", label: "Permiso con goce", tipo: "neutral" },
  { value: "permiso_sg", label: "Permiso sin goce", tipo: "deduccion" },
  { value: "horas_extra", label: "Horas extra", tipo: "percepcion" },
  { value: "bono", label: "Bono", tipo: "percepcion" },
  { value: "comision", label: "Comision", tipo: "percepcion" },
  { value: "descuento", label: "Descuento", tipo: "deduccion" },
  { value: "prestamo", label: "Prestamo", tipo: "deduccion" },
  { value: "otro", label: "Otro", tipo: "neutral" },
];
