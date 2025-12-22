// Empleado types

export interface Empleado {
  id: string;
  nombre: string;
  apellido_paterno: string;
  apellido_materno?: string;
  nombre_completo?: string;

  // Documentos mexicanos
  curp?: string;
  rfc?: string;
  nss_imss?: string;

  // Datos personales
  fecha_nacimiento?: string;
  genero?: string;
  estado_civil?: string;

  // Contacto
  telefono_personal?: string;
  email_personal?: string;
  email_corporativo?: string;

  // Dirección
  direccion_calle?: string;
  direccion_numero?: string;
  direccion_colonia?: string;
  direccion_cp?: string;
  direccion_municipio?: string;
  direccion_estado?: string;

  // Contacto emergencia
  emergencia_nombre?: string;
  emergencia_parentesco?: string;
  emergencia_telefono?: string;

  // Datos bancarios
  banco?: string;
  clabe?: string;

  // Datos laborales
  empresa: string;
  empresa_nombre?: string;
  puesto?: string;
  departamento?: string;
  fecha_ingreso: string;
  tipo_contrato?: "indefinido" | "temporal" | "obra" | "tiempo" | "capacitacion" | "prueba";
  jornada?: "diurna" | "nocturna" | "mixta";
  modalidad?: string;

  // Salario
  salario_diario?: number;
  salario_mensual?: number;

  // Jerarquía
  jefe_directo?: string;
  jefe_directo_nombre?: string;
  plan_prestaciones?: string;

  // Estado
  estado: "activo" | "baja" | "incapacidad";
  fecha_baja?: string;
  tipo_baja?: string;
  motivo_baja?: string;

  // Foto
  foto?: string;

  // Metadata
  antiguedad_anos?: number;
  created_at?: string;
  updated_at?: string;
}

// Opciones para formularios de empleado
export const GENERO_OPTIONS = [
  { value: "M", label: "Masculino" },
  { value: "F", label: "Femenino" },
  { value: "O", label: "Otro" },
];

export const ESTADO_CIVIL_OPTIONS = [
  { value: "soltero", label: "Soltero(a)" },
  { value: "casado", label: "Casado(a)" },
  { value: "divorciado", label: "Divorciado(a)" },
  { value: "viudo", label: "Viudo(a)" },
  { value: "union_libre", label: "Unión libre" },
];

export const TIPO_CONTRATO_OPTIONS = [
  { value: "indefinido", label: "Tiempo indefinido" },
  { value: "temporal", label: "Temporal" },
  { value: "obra", label: "Por obra determinada" },
  { value: "tiempo", label: "Por tiempo determinado" },
  { value: "capacitacion", label: "Capacitación inicial" },
  { value: "prueba", label: "Periodo de prueba" },
];

export const JORNADA_OPTIONS = [
  { value: "diurna", label: "Diurna" },
  { value: "nocturna", label: "Nocturna" },
  { value: "mixta", label: "Mixta" },
];

export const BANCOS_MEXICO = [
  { value: "BBVA", label: "BBVA México" },
  { value: "Santander", label: "Santander" },
  { value: "Banorte", label: "Banorte" },
  { value: "HSBC", label: "HSBC" },
  { value: "Scotiabank", label: "Scotiabank" },
  { value: "Citibanamex", label: "Citibanamex" },
  { value: "Inbursa", label: "Inbursa" },
  { value: "Azteca", label: "Banco Azteca" },
  { value: "BanCoppel", label: "BanCoppel" },
  { value: "Otro", label: "Otro" },
];

export const ESTADOS_MEXICO = [
  "Aguascalientes", "Baja California", "Baja California Sur", "Campeche",
  "Chiapas", "Chihuahua", "Ciudad de México", "Coahuila", "Colima",
  "Durango", "Estado de México", "Guanajuato", "Guerrero", "Hidalgo",
  "Jalisco", "Michoacán", "Morelos", "Nayarit", "Nuevo León", "Oaxaca",
  "Puebla", "Querétaro", "Quintana Roo", "San Luis Potosí", "Sinaloa",
  "Sonora", "Tabasco", "Tamaulipas", "Tlaxcala", "Veracruz", "Yucatán", "Zacatecas",
];
