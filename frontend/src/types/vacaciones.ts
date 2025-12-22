// Vacaciones types

export interface SolicitudVacaciones {
  id: string;
  empleado: string;
  empleado_nombre?: string;
  empleado_puesto?: string;
  empresa_nombre?: string;

  fecha_inicio: string;
  fecha_fin: string;
  dias_solicitados: number;

  estado: "pendiente" | "aprobada" | "rechazada" | "cancelada";
  estado_display?: string;

  aprobado_por?: string;
  aprobador_nombre?: string;
  fecha_aprobacion?: string;

  comentarios?: string;
  notas?: string;

  puede_aprobar?: boolean;

  created_at?: string;
  updated_at?: string;
}

export interface ResumenVacaciones {
  empleado_id: string;
  empleado_nombre: string;
  fecha_ingreso: string;
  antiguedad_anios: number;
  dias_correspondientes_anio_actual: number;
  dias_tomados_anio_actual: number;
  dias_disponibles: number;
  dias_pendientes_anteriores: number;
  total_disponible: number;
  solicitudes_pendientes: number;
}

export interface EstadisticasVacaciones {
  pendientes: number;
  aprobadas: number;
  rechazadas: number;
  proximas_7_dias: number;
}

export const ESTADO_VACACIONES_OPTIONS = [
  { value: "pendiente", label: "Pendiente", color: "amber" },
  { value: "aprobada", label: "Aprobada", color: "green" },
  { value: "rechazada", label: "Rechazada", color: "red" },
  { value: "cancelada", label: "Cancelada", color: "warm" },
];
