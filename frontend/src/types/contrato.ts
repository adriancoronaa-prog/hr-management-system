// Contrato types

export interface Contrato {
  id: string;
  empleado: string;
  empleado_nombre?: string;
  empresa_nombre?: string;

  // Tipo de contrato
  tipo_contrato: "indefinido" | "temporal" | "obra" | "tiempo" | "capacitacion" | "prueba";
  tipo_contrato_display?: string;

  // Fechas
  fecha_inicio: string;
  fecha_fin?: string | null;
  fecha_firma?: string;
  fecha_terminacion?: string;

  // Condiciones
  puesto?: string;
  departamento?: string;
  salario_mensual?: number;
  salario_diario?: number;
  jornada?: string;
  horario?: string;
  condiciones_especiales?: string;
  clausulas_adicionales?: string;

  // Estado
  estado: "vigente" | "vencido" | "renovado" | "cancelado" | "terminado";
  estado_display?: string;
  motivo_terminacion?: string;

  // Documento
  documento?: string;
  documento_url?: string;
  documento_firmado?: string;
  documento_firmado_url?: string;

  // Renovacion
  contrato_anterior?: string;
  numero_renovaciones?: number;

  // Calculados
  dias_para_vencer?: number | null;
  es_vigente?: boolean;
  esta_por_vencer?: boolean;

  // Metadata
  created_at?: string;
  updated_at?: string;
}

export const TIPO_CONTRATO_LARGO_OPTIONS = [
  { value: "indefinido", label: "Tiempo indefinido" },
  { value: "temporal", label: "Temporal" },
  { value: "obra", label: "Por obra determinada" },
  { value: "tiempo", label: "Por tiempo determinado" },
  { value: "capacitacion", label: "Capacitacion inicial" },
  { value: "prueba", label: "Periodo de prueba" },
];

export const ESTADO_CONTRATO_OPTIONS = [
  { value: "vigente", label: "Vigente" },
  { value: "vencido", label: "Vencido" },
  { value: "renovado", label: "Renovado" },
  { value: "cancelado", label: "Cancelado" },
  { value: "terminado", label: "Terminado" },
];
