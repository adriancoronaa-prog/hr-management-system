// Empresa types

export interface Empresa {
  id: string;
  rfc: string;
  razon_social: string;
  nombre_comercial?: string;
  logo?: string;
  estado?: string;
  empleados_count?: number;
  direccion?: string;
  telefono?: string;
  email?: string;
}
