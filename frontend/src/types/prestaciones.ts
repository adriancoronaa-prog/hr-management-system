/**
 * Types para el módulo de prestaciones
 */

export interface PlanPrestaciones {
  id: string;
  empresa: string;
  empresa_nombre?: string;
  nombre: string;
  descripcion?: string;
  es_default: boolean;
  activo: boolean;
  // Prestaciones de ley (superiores al mínimo)
  vacaciones_dias_extra: number;
  prima_vacacional_porcentaje: number;
  aguinaldo_dias: number;
  // Relaciones
  prestaciones_adicionales?: PrestacionAdicional[];
  // Comparativa con ley
  comparativa_ley?: {
    vacaciones: { ley: string; plan: string; diferencia: number };
    prima_vacacional: { ley: number; plan: number; diferencia: number };
    aguinaldo: { ley: number; plan: number; diferencia: number };
  };
  created_at?: string;
  updated_at?: string;
}

export interface PrestacionAdicional {
  id: string;
  plan: string;
  plan_nombre?: string;
  empresa_nombre?: string;
  categoria: 'economica' | 'salud' | 'tiempo' | 'desarrollo' | 'familia' | 'otro';
  categoria_display?: string;
  tipo_prestacion?: string;
  tipo_prestacion_display?: string;
  nombre: string;
  descripcion?: string;
  tipo_valor: 'monto' | 'porcentaje' | 'texto';
  valor: string;
  periodicidad: 'mensual' | 'anual' | 'unica';
  tope_mensual?: number | null;
  tope_anual?: number | null;
  porcentaje_empresa?: number | null;
  porcentaje_empleado?: number | null;
  aplica_a_dependientes?: boolean;
  numero_dependientes?: number | null;
  proveedor?: string;
  activo: boolean;
  orden?: number;
  created_at?: string;
  updated_at?: string;
}

export interface CatalogoPrestacion {
  key: string;
  nombre: string;
  categoria?: string;
}

export interface CatalogoResponse {
  categorias: CatalogoPrestacion[];
  tipos: Array<{ key: string; nombre: string; categoria: string }>;
  categorias_con_tipos: Array<{
    key: string;
    nombre: string;
    tipos: CatalogoPrestacion[];
  }>;
}

export interface ReferenciaLey {
  vacaciones_por_antiguedad: Record<string, number>;
  prima_vacacional_minima: number;
  aguinaldo_minimo_dias: number;
  prima_dominical: number;
}

export interface AjusteIndividual {
  id: string;
  empleado: string;
  empleado_nombre?: string;
  concepto: string;
  tipo_ajuste: 'reemplaza' | 'suma';
  valor: string;
  motivo: string;
  fecha_inicio: string;
  fecha_fin?: string | null;
  activo: boolean;
  created_at?: string;
}

export const CATEGORIAS_PRESTACION = [
  { value: 'economica', label: 'Económica', icon: 'Wallet', color: 'text-green-600 bg-green-100' },
  { value: 'salud', label: 'Salud y Bienestar', icon: 'Heart', color: 'text-red-600 bg-red-100' },
  { value: 'tiempo', label: 'Tiempo y Flexibilidad', icon: 'Clock', color: 'text-blue-600 bg-blue-100' },
  { value: 'desarrollo', label: 'Desarrollo y Educación', icon: 'GraduationCap', color: 'text-purple-600 bg-purple-100' },
  { value: 'familia', label: 'Familia', icon: 'Users', color: 'text-orange-600 bg-orange-100' },
  { value: 'otro', label: 'Otro', icon: 'Package', color: 'text-gray-600 bg-gray-100' },
] as const;
