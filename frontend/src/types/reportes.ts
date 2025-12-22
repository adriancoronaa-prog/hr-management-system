// Reportes types

export interface DashboardEmpresa {
  empresa: {
    id: string;
    razon_social: string;
    nombre_comercial: string;
    rfc: string;
    regimen_fiscal?: string;
  };
  empleados: {
    total: number;
    activos: number;
    inactivos: number;
    bajas: number;
    antiguedad_promedio_anos: number;
    salario_diario_promedio: number;
    salario_mensual_promedio: number;
    nomina_mensual_estimada: number;
    por_departamento: Array<{ departamento: string; total: number }>;
  };
  nomina: {
    periodos_procesados_ano: number;
    total_percepciones_ano: number;
    total_deducciones_ano: number;
    total_neto_pagado_ano: number;
    ultimo_periodo: {
      fecha_pago: string | null;
      total_neto: number;
      empleados: number;
    } | null;
  };
  vacaciones: {
    dias_pendientes_total: number;
    dias_tomados_ano: number;
    pasivo_vacaciones: number;
  };
  costos_proyectados: {
    aguinaldo_proyectado: number;
    prima_vacacional_proyectada: number;
    nomina_mensual: number;
    costo_anual_estimado: number;
  };
  alertas: Array<{
    tipo: string;
    nivel: "warning" | "error" | "info";
    empleado: string;
    mensaje: string;
  }>;
  fecha_generacion: string;
}

// Datos para graficos
export interface DatosMensuales {
  mes: string;
  valor: number;
}

export interface EmpleadosPorDepartamento {
  departamento: string;
  cantidad: number;
  porcentaje: number;
}

export interface ContratosPorTipo {
  tipo: string;
  tipo_display: string;
  cantidad: number;
  porcentaje: number;
}

// Resumen de vacaciones para reportes
export interface ResumenVacacionesReporte {
  total_empleados: number;
  dias_otorgados_ano: number;
  dias_tomados_ano: number;
  dias_pendientes: number;
  solicitudes_pendientes: number;
  solicitudes_aprobadas: number;
  solicitudes_rechazadas: number;
  por_empleado: Array<{
    empleado_id: string;
    empleado_nombre: string;
    antiguedad_anos: number;
    dias_correspondientes: number;
    dias_tomados: number;
    dias_pendientes: number;
  }>;
}
