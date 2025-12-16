"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation, useQuery } from "@tanstack/react-query";
import Link from "next/link";
import api from "@/lib/api";
import { useAuthStore } from "@/stores/auth-store";
import {
  empleadoSchema,
  type EmpleadoFormData,
} from "@/lib/validations/empleado";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  GENERO_OPTIONS,
  ESTADO_CIVIL_OPTIONS,
  TIPO_CONTRATO_OPTIONS,
  JORNADA_OPTIONS,
  BANCOS_MEXICO,
  ESTADOS_MEXICO,
} from "@/types";
import {
  ArrowLeft,
  User,
  FileText,
  Phone,
  MapPin,
  Briefcase,
  DollarSign,
  Users,
  Loader2,
  AlertCircle,
  CheckCircle,
} from "lucide-react";

type SectionId = "personal" | "documentos" | "contacto" | "direccion" | "laboral" | "salario" | "jerarquia";

const sections: { id: SectionId; label: string; icon: React.ElementType }[] = [
  { id: "personal", label: "Datos personales", icon: User },
  { id: "documentos", label: "Documentos", icon: FileText },
  { id: "contacto", label: "Contacto", icon: Phone },
  { id: "direccion", label: "Direccion", icon: MapPin },
  { id: "laboral", label: "Datos laborales", icon: Briefcase },
  { id: "salario", label: "Salario y pago", icon: DollarSign },
  { id: "jerarquia", label: "Jerarquia", icon: Users },
];

export default function NuevoEmpleadoPage() {
  const router = useRouter();
  const { user, empresaActual } = useAuthStore();
  const [mounted, setMounted] = useState(false);
  const [activeSection, setActiveSection] = useState<SectionId>("personal");

  useEffect(() => {
    setMounted(true);
  }, []);

  // Verificar permisos
  const canCreate =
    user?.rol === "admin" ||
    user?.rol === "rrhh" ||
    user?.rol === "empleador";

  // Cargar lista de empleados para selector de jefe
  const { data: empleadosLista } = useQuery({
    queryKey: ["empleados-jefes", empresaActual?.id],
    queryFn: async () => {
      const response = await api.get("/empleados/");
      const rawData = response.data;
      return rawData.results || rawData;
    },
    enabled: mounted && !!empresaActual?.id,
  });

  const {
    register,
    handleSubmit,
    watch,
    setValue,
    formState: { errors, isSubmitting },
  } = useForm<EmpleadoFormData>({
    resolver: zodResolver(empleadoSchema),
    defaultValues: {
      empresa: empresaActual?.id || "",
      fecha_ingreso: new Date().toISOString().split("T")[0],
      tipo_contrato: "indefinido",
      jornada: "diurna",
      modalidad: "presencial",
    },
  });

  // Actualizar empresa cuando cambie
  useEffect(() => {
    if (empresaActual?.id) {
      setValue("empresa", empresaActual.id);
    }
  }, [empresaActual, setValue]);

  const banco = watch("banco");

  const [backendErrors, setBackendErrors] = useState<Record<string, string[]> | null>(null);

  const mutation = useMutation({
    mutationFn: async (data: EmpleadoFormData) => {
      // Limpiar errores previos
      setBackendErrors(null);

      // Limpiar campos vacios
      const cleanData: Record<string, unknown> = {};

      Object.entries(data).forEach(([key, value]) => {
        // Solo incluir valores no vacíos
        if (
          value !== "" &&
          value !== null &&
          value !== undefined &&
          !(typeof value === "string" && value.trim() === "")
        ) {
          cleanData[key] = value;
        }
      });

      try {
        const response = await api.post("/empleados/", cleanData);
        return response.data;
      } catch (error: unknown) {
        const axiosError = error as { response?: { status?: number; data?: Record<string, string[]> } };
        // Guardar errores del backend para mostrarlos
        if (axiosError.response?.data && typeof axiosError.response.data === "object") {
          setBackendErrors(axiosError.response.data);
        }
        throw error;
      }
    },
    onSuccess: (data) => {
      setBackendErrors(null);
      router.push(`/empleados/${data.id}`);
    },
  });

  const onSubmit = (data: EmpleadoFormData) => {
    mutation.mutate(data);
  };

  const onError = (formErrors: typeof errors) => {
    // Encontrar la primera seccion con errores y navegar a ella
    const sectionFields: Record<SectionId, string[]> = {
      personal: ["nombre", "apellido_paterno", "apellido_materno", "fecha_nacimiento", "genero", "estado_civil"],
      documentos: ["rfc", "curp", "nss_imss"],
      contacto: ["email_personal", "email_corporativo", "telefono_personal", "emergencia_nombre", "emergencia_parentesco", "emergencia_telefono"],
      direccion: ["direccion_calle", "direccion_numero", "direccion_colonia", "direccion_cp", "direccion_municipio", "direccion_estado"],
      laboral: ["empresa", "fecha_ingreso", "puesto", "departamento", "tipo_contrato", "jornada", "modalidad"],
      salario: ["salario_diario", "banco", "clabe"],
      jerarquia: ["jefe_directo"],
    };

    for (const [sectionId, fields] of Object.entries(sectionFields)) {
      if (fields.some((field) => formErrors[field as keyof typeof formErrors])) {
        setActiveSection(sectionId as SectionId);
        break;
      }
    }
  };

  const goToNextSection = () => {
    const currentIndex = sections.findIndex((s) => s.id === activeSection);
    if (currentIndex < sections.length - 1) {
      setActiveSection(sections[currentIndex + 1].id);
    }
  };

  const goToPreviousSection = () => {
    const currentIndex = sections.findIndex((s) => s.id === activeSection);
    if (currentIndex > 0) {
      setActiveSection(sections[currentIndex - 1].id);
    }
  };

  if (!mounted) return null;

  if (!canCreate) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] text-center">
        <AlertCircle className="w-16 h-16 text-amber-500 mb-4" />
        <h1 className="text-xl font-semibold text-warm-900">
          Acceso restringido
        </h1>
        <p className="text-warm-500 mt-2">
          No tienes permisos para crear empleados.
        </p>
        <Link href="/empleados">
          <Button variant="outline" className="mt-4">
            Volver a empleados
          </Button>
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <Link
          href="/empleados"
          className="inline-flex items-center text-sm text-warm-500 hover:text-warm-700 mb-4"
        >
          <ArrowLeft className="w-4 h-4 mr-1" />
          Volver a empleados
        </Link>
        <h1 className="text-2xl font-display font-semibold text-warm-900">
          Nuevo empleado
        </h1>
        <p className="text-warm-500 mt-1">
          Registrar en{" "}
          {empresaActual?.nombre_comercial || empresaActual?.razon_social}
        </p>
      </div>

      {/* Error general */}
      {(mutation.error || backendErrors) && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
          <div className="flex-1">
            <p className="font-medium text-red-800">Error al crear empleado</p>
            {backendErrors ? (
              <ul className="text-sm text-red-600 mt-2 space-y-1">
                {Object.entries(backendErrors).map(([field, messages]) => (
                  <li key={field}>
                    <strong>{field}:</strong>{" "}
                    {Array.isArray(messages) ? messages.join(", ") : String(messages)}
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-sm text-red-600 mt-1">
                {(mutation.error as Error)?.message ||
                  "Ocurrio un error inesperado"}
              </p>
            )}
          </div>
        </div>
      )}

      {/* Navegacion de secciones */}
      <div className="flex gap-2 overflow-x-auto pb-2 mb-6">
        {sections.map((section) => {
          const Icon = section.icon;
          const sectionFields: Record<SectionId, string[]> = {
            personal: ["nombre", "apellido_paterno", "apellido_materno", "fecha_nacimiento", "genero", "estado_civil"],
            documentos: ["rfc", "curp", "nss_imss"],
            contacto: ["email_personal", "email_corporativo", "telefono_personal", "emergencia_nombre", "emergencia_parentesco", "emergencia_telefono"],
            direccion: ["direccion_calle", "direccion_numero", "direccion_colonia", "direccion_cp", "direccion_municipio", "direccion_estado"],
            laboral: ["empresa", "fecha_ingreso", "puesto", "departamento", "tipo_contrato", "jornada", "modalidad"],
            salario: ["salario_diario", "banco", "clabe"],
            jerarquia: ["jefe_directo"],
          };
          const hasErrors = sectionFields[section.id].some(
            (field) => errors[field as keyof typeof errors]
          );
          return (
            <button
              key={section.id}
              type="button"
              onClick={() => setActiveSection(section.id)}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium whitespace-nowrap transition-colors ${
                activeSection === section.id
                  ? "bg-horizon-600 text-white"
                  : hasErrors
                  ? "bg-red-100 text-red-600 hover:bg-red-200 border border-red-300"
                  : "bg-warm-100 text-warm-600 hover:bg-warm-200"
              }`}
            >
              <Icon className="w-4 h-4" />
              {section.label}
              {hasErrors && <AlertCircle className="w-4 h-4 text-red-500" />}
            </button>
          );
        })}
      </div>

      <form onSubmit={handleSubmit(onSubmit, onError)} className="space-y-6">
        {/* Datos Personales */}
        {activeSection === "personal" && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <User className="w-5 h-5 text-horizon-600" />
                Datos personales
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Input
                  label="Nombre(s) *"
                  placeholder="Juan Carlos"
                  error={errors.nombre?.message}
                  {...register("nombre")}
                />
                <Input
                  label="Apellido paterno *"
                  placeholder="Garcia"
                  error={errors.apellido_paterno?.message}
                  {...register("apellido_paterno")}
                />
                <Input
                  label="Apellido materno"
                  placeholder="Lopez"
                  error={errors.apellido_materno?.message}
                  {...register("apellido_materno")}
                />
                <Input
                  label="Fecha de nacimiento"
                  type="date"
                  error={errors.fecha_nacimiento?.message}
                  {...register("fecha_nacimiento")}
                />
                <div>
                  <label className="block text-sm font-medium text-warm-700 mb-1.5">
                    Genero
                  </label>
                  <select
                    className="flex h-10 w-full rounded-md border border-warm-300 bg-white px-3 py-2 text-sm text-warm-900 focus:border-horizon-500 focus:outline-none focus:ring-1 focus:ring-horizon-500"
                    {...register("genero")}
                  >
                    <option value="">Seleccionar...</option>
                    {GENERO_OPTIONS.map((opt) => (
                      <option key={opt.value} value={opt.value}>
                        {opt.label}
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-warm-700 mb-1.5">
                    Estado civil
                  </label>
                  <select
                    className="flex h-10 w-full rounded-md border border-warm-300 bg-white px-3 py-2 text-sm text-warm-900 focus:border-horizon-500 focus:outline-none focus:ring-1 focus:ring-horizon-500"
                    {...register("estado_civil")}
                  >
                    <option value="">Seleccionar...</option>
                    {ESTADO_CIVIL_OPTIONS.map((opt) => (
                      <option key={opt.value} value={opt.value}>
                        {opt.label}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Documentos */}
        {activeSection === "documentos" && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <FileText className="w-5 h-5 text-horizon-600" />
                Documentos oficiales
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Input
                  label="RFC"
                  placeholder="GARC850101ABC"
                  error={errors.rfc?.message}
                  className="uppercase"
                  maxLength={13}
                  {...register("rfc")}
                />
                <Input
                  label="CURP"
                  placeholder="GARC850101HDFRRL09"
                  error={errors.curp?.message}
                  className="uppercase"
                  maxLength={18}
                  {...register("curp")}
                />
                <Input
                  label="NSS (Numero de Seguro Social)"
                  placeholder="12345678901"
                  error={errors.nss_imss?.message}
                  maxLength={11}
                  {...register("nss_imss")}
                />
              </div>
              <p className="text-xs text-warm-400 mt-4">
                Estos documentos son importantes para el registro ante el IMSS y
                SAT.
              </p>
            </CardContent>
          </Card>
        )}

        {/* Contacto */}
        {activeSection === "contacto" && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Phone className="w-5 h-5 text-horizon-600" />
                Informacion de contacto
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Input
                  label="Email personal"
                  type="email"
                  placeholder="juan.garcia@email.com"
                  error={errors.email_personal?.message}
                  {...register("email_personal")}
                />
                <Input
                  label="Email corporativo"
                  type="email"
                  placeholder="jgarcia@empresa.com"
                  error={errors.email_corporativo?.message}
                  {...register("email_corporativo")}
                />
                <Input
                  label="Telefono personal"
                  placeholder="55 1234 5678"
                  error={errors.telefono_personal?.message}
                  {...register("telefono_personal")}
                />
                <div className="md:col-span-2 border-t pt-4 mt-2">
                  <h4 className="text-sm font-medium text-warm-700 mb-3">
                    Contacto de emergencia
                  </h4>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <Input
                      label="Nombre completo"
                      placeholder="Maria Garcia"
                      error={errors.emergencia_nombre?.message}
                      {...register("emergencia_nombre")}
                    />
                    <Input
                      label="Parentesco"
                      placeholder="Madre"
                      error={errors.emergencia_parentesco?.message}
                      {...register("emergencia_parentesco")}
                    />
                    <Input
                      label="Telefono"
                      placeholder="55 8765 4321"
                      error={errors.emergencia_telefono?.message}
                      {...register("emergencia_telefono")}
                    />
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Direccion */}
        {activeSection === "direccion" && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <MapPin className="w-5 h-5 text-horizon-600" />
                Direccion
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Input
                  label="Calle"
                  placeholder="Av. Insurgentes Sur"
                  error={errors.direccion_calle?.message}
                  {...register("direccion_calle")}
                />
                <Input
                  label="Numero"
                  placeholder="1234, Int. 5"
                  error={errors.direccion_numero?.message}
                  {...register("direccion_numero")}
                />
                <Input
                  label="Colonia"
                  placeholder="Del Valle"
                  error={errors.direccion_colonia?.message}
                  {...register("direccion_colonia")}
                />
                <Input
                  label="Codigo Postal"
                  placeholder="03100"
                  maxLength={5}
                  error={errors.direccion_cp?.message}
                  {...register("direccion_cp")}
                />
                <Input
                  label="Municipio/Alcaldia"
                  placeholder="Benito Juarez"
                  error={errors.direccion_municipio?.message}
                  {...register("direccion_municipio")}
                />
                <div>
                  <label className="block text-sm font-medium text-warm-700 mb-1.5">
                    Estado
                  </label>
                  <select
                    className="flex h-10 w-full rounded-md border border-warm-300 bg-white px-3 py-2 text-sm text-warm-900 focus:border-horizon-500 focus:outline-none focus:ring-1 focus:ring-horizon-500"
                    {...register("direccion_estado")}
                  >
                    <option value="">Seleccionar...</option>
                    {ESTADOS_MEXICO.map((estado) => (
                      <option key={estado} value={estado}>
                        {estado}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Datos Laborales */}
        {activeSection === "laboral" && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Briefcase className="w-5 h-5 text-horizon-600" />
                Datos laborales
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Input
                  label="Fecha de ingreso *"
                  type="date"
                  error={errors.fecha_ingreso?.message}
                  {...register("fecha_ingreso")}
                />
                <Input
                  label="Puesto"
                  placeholder="Desarrollador Senior"
                  error={errors.puesto?.message}
                  {...register("puesto")}
                />
                <Input
                  label="Departamento"
                  placeholder="Tecnologia"
                  error={errors.departamento?.message}
                  {...register("departamento")}
                />
                <div>
                  <label className="block text-sm font-medium text-warm-700 mb-1.5">
                    Tipo de contrato
                  </label>
                  <select
                    className="flex h-10 w-full rounded-md border border-warm-300 bg-white px-3 py-2 text-sm text-warm-900 focus:border-horizon-500 focus:outline-none focus:ring-1 focus:ring-horizon-500"
                    {...register("tipo_contrato")}
                  >
                    {TIPO_CONTRATO_OPTIONS.map((opt) => (
                      <option key={opt.value} value={opt.value}>
                        {opt.label}
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-warm-700 mb-1.5">
                    Jornada laboral
                  </label>
                  <select
                    className="flex h-10 w-full rounded-md border border-warm-300 bg-white px-3 py-2 text-sm text-warm-900 focus:border-horizon-500 focus:outline-none focus:ring-1 focus:ring-horizon-500"
                    {...register("jornada")}
                  >
                    {JORNADA_OPTIONS.map((opt) => (
                      <option key={opt.value} value={opt.value}>
                        {opt.label}
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-warm-700 mb-1.5">
                    Modalidad
                  </label>
                  <select
                    className="flex h-10 w-full rounded-md border border-warm-300 bg-white px-3 py-2 text-sm text-warm-900 focus:border-horizon-500 focus:outline-none focus:ring-1 focus:ring-horizon-500"
                    {...register("modalidad")}
                  >
                    <option value="presencial">Presencial</option>
                    <option value="remoto">Remoto</option>
                    <option value="hibrido">Hibrido</option>
                  </select>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Salario y Pago */}
        {activeSection === "salario" && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <DollarSign className="w-5 h-5 text-horizon-600" />
                Salario y forma de pago
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Input
                  label="Salario diario"
                  type="number"
                  step="0.01"
                  placeholder="850.00"
                  error={errors.salario_diario?.message}
                  {...register("salario_diario")}
                />
                <div>
                  <label className="block text-sm font-medium text-warm-700 mb-1.5">
                    Banco
                  </label>
                  <select
                    className="flex h-10 w-full rounded-md border border-warm-300 bg-white px-3 py-2 text-sm text-warm-900 focus:border-horizon-500 focus:outline-none focus:ring-1 focus:ring-horizon-500"
                    {...register("banco")}
                  >
                    <option value="">Seleccionar banco...</option>
                    {BANCOS_MEXICO.map((b) => (
                      <option key={b.value} value={b.value}>
                        {b.label}
                      </option>
                    ))}
                  </select>
                </div>

                {banco && (
                  <div className="md:col-span-2">
                    <Input
                      label="CLABE interbancaria"
                      placeholder="012345678901234567"
                      maxLength={18}
                      error={errors.clabe?.message}
                      {...register("clabe")}
                    />
                  </div>
                )}
              </div>
              <p className="text-xs text-warm-400 mt-4">
                El salario mensual se calcula automaticamente (salario diario x
                30).
              </p>
            </CardContent>
          </Card>
        )}

        {/* Jerarquia */}
        {activeSection === "jerarquia" && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Users className="w-5 h-5 text-horizon-600" />
                Jerarquia organizacional
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div>
                <label className="block text-sm font-medium text-warm-700 mb-1.5">
                  Jefe directo
                </label>
                <select
                  className="flex h-10 w-full rounded-md border border-warm-300 bg-white px-3 py-2 text-sm text-warm-900 focus:border-horizon-500 focus:outline-none focus:ring-1 focus:ring-horizon-500"
                  {...register("jefe_directo")}
                >
                  <option value="">Sin jefe asignado</option>
                  {Array.isArray(empleadosLista) &&
                    empleadosLista
                      .filter((e: { estado: string }) => e.estado === "activo")
                      .map(
                        (emp: {
                          id: string;
                          nombre: string;
                          apellido_paterno: string;
                          nombre_completo?: string;
                          puesto?: string;
                        }) => (
                          <option key={emp.id} value={emp.id}>
                            {emp.nombre_completo ||
                              `${emp.nombre} ${emp.apellido_paterno}`}{" "}
                            - {emp.puesto || "Sin puesto"}
                          </option>
                        )
                      )}
                </select>
                <p className="text-xs text-warm-400 mt-1">
                  El jefe directo recibira notificaciones y podra aprobar
                  solicitudes.
                </p>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Input oculto para empresa */}
        <input type="hidden" {...register("empresa")} />

        {/* Botones */}
        <div className="flex items-center justify-between pt-4 border-t border-warm-200">
          <Link href="/empleados">
            <Button variant="outline" type="button">
              Cancelar
            </Button>
          </Link>
          <div className="flex gap-2">
            {activeSection !== "personal" && (
              <Button
                type="button"
                variant="outline"
                onClick={goToPreviousSection}
              >
                Anterior
              </Button>
            )}
            {activeSection !== "jerarquia" ? (
              <Button type="button" onClick={goToNextSection}>
                Siguiente
              </Button>
            ) : (
              <Button
                type="submit"
                disabled={isSubmitting || mutation.isPending}
              >
                {isSubmitting || mutation.isPending ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Guardando...
                  </>
                ) : (
                  <>
                    <CheckCircle className="w-4 h-4 mr-2" />
                    Crear empleado
                  </>
                )}
              </Button>
            )}
          </div>
        </div>
      </form>
    </div>
  );
}
