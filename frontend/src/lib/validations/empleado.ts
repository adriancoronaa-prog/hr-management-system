import { z } from "zod";

// Validaciones para documentos mexicanos
const rfcRegex = /^[A-ZÑ&]{3,4}\d{6}[A-Z0-9]{3}$/;
const curpRegex = /^[A-Z]{4}\d{6}[HM][A-Z]{5}[A-Z0-9]\d$/;
const nssRegex = /^\d{11}$/;
const clabeRegex = /^\d{18}$/;

export const empleadoSchema = z.object({
  // Datos personales - Requeridos
  nombre: z.string()
    .min(2, "El nombre debe tener al menos 2 caracteres")
    .max(100, "El nombre no puede exceder 100 caracteres"),

  apellido_paterno: z.string()
    .min(2, "El apellido debe tener al menos 2 caracteres")
    .max(100, "El apellido no puede exceder 100 caracteres"),

  apellido_materno: z.string().max(100).optional().default(""),
  fecha_nacimiento: z.string().optional().default(""),
  genero: z.string().optional().default(""),
  estado_civil: z.string().optional().default(""),

  // Documentos mexicanos
  rfc: z.string().max(13).optional().default("")
    .refine((val) => !val || rfcRegex.test(val.toUpperCase()), {
      message: "RFC invalido. Debe tener 12-13 caracteres (ej: GARC850101ABC)",
    }),

  curp: z.string().max(18).optional().default("")
    .refine((val) => !val || curpRegex.test(val.toUpperCase()), {
      message: "CURP invalido. Debe tener 18 caracteres",
    }),

  nss_imss: z.string().max(11).optional().default("")
    .refine((val) => !val || nssRegex.test(val), {
      message: "NSS invalido. Debe tener 11 digitos",
    }),

  // Contacto
  email_personal: z.string().optional().default("")
    .refine((val) => !val || z.string().email().safeParse(val).success, {
      message: "Email invalido",
    }),

  email_corporativo: z.string().optional().default("")
    .refine((val) => !val || z.string().email().safeParse(val).success, {
      message: "Email invalido",
    }),

  telefono_personal: z.string().max(20).optional().default(""),
  emergencia_nombre: z.string().max(255).optional().default(""),
  emergencia_parentesco: z.string().max(50).optional().default(""),
  emergencia_telefono: z.string().max(20).optional().default(""),

  // Direccion
  direccion_calle: z.string().max(255).optional().default(""),
  direccion_numero: z.string().max(20).optional().default(""),
  direccion_colonia: z.string().max(100).optional().default(""),
  direccion_cp: z.string().max(5).optional().default(""),
  direccion_municipio: z.string().max(100).optional().default(""),
  direccion_estado: z.string().max(50).optional().default(""),

  // Datos laborales - Requeridos
  empresa: z.string().min(1, "Debe seleccionar una empresa"),
  fecha_ingreso: z.string().min(1, "La fecha de ingreso es requerida"),

  puesto: z.string().max(100).optional().default(""),
  departamento: z.string().max(100).optional().default(""),
  tipo_contrato: z.string().optional().default(""),
  jornada: z.string().optional().default(""),
  modalidad: z.string().optional().default(""),

  // Salario
  salario_diario: z.union([z.number(), z.string()]).optional()
    .transform((val) => {
      if (val === "" || val === null || val === undefined) return undefined;
      const num = typeof val === "string" ? parseFloat(val) : val;
      return isNaN(num) ? undefined : num;
    }),

  // Datos bancarios
  banco: z.string().max(100).optional().default(""),

  clabe: z.string().max(18).optional().default("")
    .refine((val) => !val || clabeRegex.test(val), {
      message: "CLABE invalida. Debe tener 18 digitos",
    }),

  // Jerarquia
  jefe_directo: z.string().optional().default(""),
});

// Tipo para el formulario - input antes de transformaciones
export type EmpleadoFormData = {
  nombre: string;
  apellido_paterno: string;
  apellido_materno?: string;
  fecha_nacimiento?: string;
  genero?: string;
  estado_civil?: string;
  rfc?: string;
  curp?: string;
  nss_imss?: string;
  email_personal?: string;
  email_corporativo?: string;
  telefono_personal?: string;
  emergencia_nombre?: string;
  emergencia_parentesco?: string;
  emergencia_telefono?: string;
  direccion_calle?: string;
  direccion_numero?: string;
  direccion_colonia?: string;
  direccion_cp?: string;
  direccion_municipio?: string;
  direccion_estado?: string;
  empresa: string;
  fecha_ingreso: string;
  puesto?: string;
  departamento?: string;
  tipo_contrato?: string;
  jornada?: string;
  modalidad?: string;
  salario_diario?: number | string;
  banco?: string;
  clabe?: string;
  jefe_directo?: string;
};
