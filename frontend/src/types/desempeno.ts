/**
 * Types para el módulo de desempeño
 */

export interface CatalogoKPI {
  id: string;
  nombre: string;
  descripcion?: string;
  categoria: string;
  categoria_display?: string;
  tipo_medicion: 'numero' | 'porcentaje' | 'moneda' | 'boolean' | 'escala';
  tipo_medicion_display?: string;
  unidad?: string;
  frecuencia: string;
  frecuencia_display?: string;
  valor_minimo?: number;
  valor_objetivo?: number;
  valor_excelente?: number;
  es_mayor_mejor: boolean;
  activo: boolean;
}

export interface AsignacionKPI {
  id: string;
  empleado: string;
  empleado_nombre?: string;
  nombre_kpi: string;
  descripcion_personalizada?: string;
  periodo: string;
  fecha_inicio: string;
  fecha_fin: string;
  meta: number;
  peso: number;
  es_mayor_mejor: boolean;
  estado: 'borrador' | 'activo' | 'pendiente' | 'evaluado' | 'cancelado';
  estado_display?: string;
  valor_logrado?: number;
  porcentaje_cumplimiento?: number;
  tiene_cambios_pendientes: boolean;
  created_at?: string;
}

export interface ResumenKPIs {
  total: number;
  activos: number;
  promedio_cumplimiento?: number;
  pendientes_cambio: number;
}

export interface Evaluacion {
  id: string;
  empleado: string;
  empleado_nombre?: string;
  evaluador_nombre?: string;
  tipo: 'mensual' | 'trimestral' | 'semestral' | 'anual' | 'prueba';
  tipo_display?: string;
  periodo: string;
  fecha_inicio?: string;
  fecha_fin?: string;
  modalidad: '90' | '180' | '360';
  estado: 'borrador' | 'en_progreso' | 'pendiente_revision' | 'completada' | 'cerrada';
  estado_display?: string;
  puntuacion_kpis?: number;
  puntuacion_competencias?: number;
  puntuacion_final?: number;
  clasificacion_desempeno?: 'bajo' | 'medio' | 'alto';
  clasificacion_potencial?: 'bajo' | 'medio' | 'alto';
  clasificacion_9box?: string;
  logros?: string;
  areas_mejora?: string;
  competencias_evaluadas_count?: number;
  created_at?: string;
}

export interface Retroalimentacion {
  id: string;
  empleado: string;
  empleado_nombre?: string;
  autor_nombre?: string;
  tipo: 'reconocimiento' | 'mejora' | 'coaching' | 'objetivo' | 'general';
  tipo_display?: string;
  contenido: string;
  es_privado: boolean;
  requiere_seguimiento: boolean;
  seguimiento_completado: boolean;
  created_at?: string;
}

export interface Matriz9Box {
  [clasificacion: string]: Array<{
    id: string;
    nombre: string;
    puesto?: string;
    puntuacion?: number;
  }>;
}

export const CLASIFICACIONES_9BOX = [
  { key: 'Estrella', label: 'Estrella', color: 'bg-green-500', position: { row: 0, col: 2 } },
  { key: 'Alto Desempeno', label: 'Alto Desempeno', color: 'bg-green-400', position: { row: 0, col: 1 } },
  { key: 'Experto Tecnico', label: 'Experto Tecnico', color: 'bg-blue-400', position: { row: 0, col: 0 } },
  { key: 'Futuro Lider', label: 'Futuro Lider', color: 'bg-yellow-400', position: { row: 1, col: 2 } },
  { key: 'Colaborador Clave', label: 'Colaborador Clave', color: 'bg-yellow-300', position: { row: 1, col: 1 } },
  { key: 'Efectivo', label: 'Efectivo', color: 'bg-gray-300', position: { row: 1, col: 0 } },
  { key: 'Enigma', label: 'Enigma', color: 'bg-orange-400', position: { row: 2, col: 2 } },
  { key: 'En Desarrollo', label: 'En Desarrollo', color: 'bg-orange-300', position: { row: 2, col: 1 } },
  { key: 'Accion Requerida', label: 'Accion Requerida', color: 'bg-red-400', position: { row: 2, col: 0 } },
] as const;
