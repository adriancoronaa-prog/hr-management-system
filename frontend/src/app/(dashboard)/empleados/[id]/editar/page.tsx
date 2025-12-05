"use client";

import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import Link from "next/link";
import api from "@/lib/api";
import { useAuthStore } from "@/stores/auth-store";
import { empleadoSchema, type EmpleadoFormData } from "@/lib/validations/empleado";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
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
  Save,
  ChevronLeft,
  ChevronRight,
} from "lucide-react";
import {
  GENERO_OPTIONS,
  ESTADO_CIVIL_OPTIONS,
  TIPO_CONTRATO_OPTIONS,
  JORNADA_OPTIONS,
  BANCOS_MEXICO,
  ESTADOS_MEXICO,
} from "@/types";

type SectionId = "personal" | "documentos" | "contacto" | "direccion" | "laboral" | "salario" | "jerarquia";

const sections: { id: SectionId; label: string; icon: typeof User }[] = [
  { id: "personal", label: "Datos personales", icon: User },
  { id: "documentos", label: "Documentos", icon: FileText },
  { id: "contacto", label: "Contacto", icon: Phone },
  { id: "direccion", label: "Direccion", icon: MapPin },
  { id: "laboral", label: "Datos laborales", icon: Briefcase },
  { id: "salario", label: "Salario y pago", icon: DollarSign },
  { id: "jerarquia", label: "Jerarquia", icon: Users },
];

export default function EditarEmpleadoPage() {
  const params = useParams();
  const router = useRouter();
  const queryClient = useQueryClient();
  const { user, empresaActual } = useAuthStore();
  const [mounted, setMounted] = useState(false);
  const [activeSection, setActiveSection] = useState<SectionId>("personal");
  const [backendErrors, setBackendErrors] = useState<Record<string, string[]> | null>(null);

  const empleadoId = params.id as string;

  useEffect(() => {
    setMounted(true);
  }, []);

  // Verificar permisos
  const canEdit = user?.rol === "admin" || user?.rol === "rrhh" || user?.rol === "empleador";

  // Cargar datos del empleado
  const { data: empleado, isLoading: loadingEmpleado } = useQuery({
    queryKey: ["empleado", empleadoId],
    queryFn: async () => {
      const response = await api.get(`/empleados/${empleadoId}/`);
      return response.data;
    },
    enabled: mounted && !!empleadoId,
  });

  // Cargar lista de empleados para selector de jefe
  const { data: empleadosLista } = useQuery({
    queryKey: ["empleados-jefes", empresaActual?.id],
    queryFn: async () => {
      const response = await api.get("/empleados/");
      const rawData = response.data;
      return Array.isArray(rawData) ? rawData : rawData?.results || [];
    },
    enabled: mounted && !!empresaActual?.id,
  });

  const {
    register,
    handleSubmit,
    watch,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<EmpleadoFormData>({
    resolver: zodResolver(empleadoSchema),
  });

  // Cargar datos del empleado en el formulario cuando lleguen
  useEffect(() => {
    if (empleado) {
      const formData: Partial<EmpleadoFormData> = {
        nombre: empleado.nombre || "",
        apellido_paterno: empleado.apellido_paterno || "",
        apellido_materno: empleado.apellido_materno || "",
        fecha_nacimiento: empleado.fecha_nacimiento || "",
        genero: empleado.genero || "",
        estado_civil: empleado.estado_civil || "",
        rfc: empleado.rfc || "",
        curp: empleado.curp || "",
        nss_imss: empleado.nss_imss || empleado.nss || "",
        email_personal: empleado.email_personal || empleado.email || "",
        email_corporativo: empleado.email_corporativo || "",
        telefono_personal: empleado.telefono_personal || empleado.telefono || "",
        emergencia_nombre: empleado.emergencia_nombre || empleado.contacto_emergencia || "",
        emergencia_telefono: empleado.emergencia_telefono || empleado.telefono_emergencia || "",
        emergencia_parentesco: empleado.emergencia_parentesco || "",
        direccion_calle: empleado.direccion_calle || empleado.direccion || "",
        direccion_numero: empleado.direccion_numero || "",
        direccion_colonia: empleado.direccion_colonia || empleado.colonia || "",
        direccion_cp: empleado.direccion_cp || empleado.codigo_postal || "",
        direccion_municipio: empleado.direccion_municipio || empleado.ciudad || "",
        direccion_estado: empleado.direccion_estado || empleado.estado_republica || "",
        empresa: empleado.empresa || empresaActual?.id || "",
        fecha_ingreso: empleado.fecha_ingreso || "",
        puesto: empleado.puesto || "",
        departamento: empleado.departamento || "",
        tipo_contrato: empleado.tipo_contrato || "",
        jornada: empleado.jornada || "",
        modalidad: empleado.modalidad || "",
        salario_diario: empleado.salario_diario || "",
        banco: empleado.banco || "",
        clabe: empleado.clabe || "",
        jefe_directo: empleado.jefe_directo || "",
      };
      reset(formData);
    }
  }, [empleado, reset, empresaActual]);

  const banco = watch("banco");

  // Mutation para actualizar
  const mutation = useMutation({
    mutationFn: async (data: EmpleadoFormData) => {
      setBackendErrors(null);

      // Limpiar campos vacios
      const cleanData: Record<string, unknown> = {};
      Object.entries(data).forEach(([key, value]) => {
        if (value !== "" && value !== null && value !== undefined && !(typeof value === "string" && value.trim() === "")) {
          cleanData[key] = value;
        }
      });

      console.log("=== ACTUALIZANDO EMPLEADO ===");
      console.log(JSON.stringify(cleanData, null, 2));

      try {
        const response = await api.patch(`/empleados/${empleadoId}/`, cleanData);
        return response.data;
      } catch (error: unknown) {
        const axiosError = error as { response?: { status?: number; data?: Record<string, string[]> } };
        console.error("=== ERROR DEL BACKEND ===");
        console.error("Status:", axiosError.response?.status);
        console.error("Data:", axiosError.response?.data);

        if (axiosError.response?.data && typeof axiosError.response.data === "object") {
          setBackendErrors(axiosError.response.data);
        }
        throw error;
      }
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["empleado", empleadoId] });
      queryClient.invalidateQueries({ queryKey: ["empleados"] });
      router.push(`/empleados/${empleadoId}`);
    },
  });

  const onSubmit = (data: EmpleadoFormData) => {
    console.log("Form submitted with data:", data);
    mutation.mutate(data);
  };

  const goToNextSection = () => {
    const currentIndex = sections.findIndex((s) => s.id === activeSection);
    if (currentIndex < sections.length - 1) {
      setActiveSection(sections[currentIndex + 1].id);
    }
  };

  const goToPrevSection = () => {
    const currentIndex = sections.findIndex((s) => s.id === activeSection);
    if (currentIndex > 0) {
      setActiveSection(sections[currentIndex - 1].id);
    }
  };

  if (!mounted) return null;

  if (!canEdit) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] text-center">
        <AlertCircle className="w-16 h-16 text-amber-500 mb-4" />
        <h1 className="text-xl font-semibold text-warm-900">Acceso restringido</h1>
        <p className="text-warm-500 mt-2">No tienes permisos para editar empleados.</p>
        <Link href={`/empleados/${empleadoId}`}>
          <Button variant="outline" className="mt-4">
            Volver al empleado
          </Button>
        </Link>
      </div>
    );
  }

  if (loadingEmpleado) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <Loader2 className="w-8 h-8 animate-spin text-horizon-500" />
      </div>
    );
  }

  if (!empleado) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] text-center">
        <AlertCircle className="w-16 h-16 text-red-500 mb-4" />
        <h1 className="text-xl font-semibold text-warm-900">Empleado no encontrado</h1>
        <Link href="/empleados">
          <Button variant="outline" className="mt-4">
            Volver a empleados
          </Button>
        </Link>
      </div>
    );
  }

  const nombreCompleto = [empleado.nombre, empleado.apellido_paterno].filter(Boolean).join(" ");

  return (
    <div className="max-w-4xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <Link
          href={`/empleados/${empleadoId}`}
          className="inline-flex items-center text-sm text-warm-500 hover:text-warm-700 mb-4"
        >
          <ArrowLeft className="w-4 h-4 mr-1" />
          Volver al empleado
        </Link>
        <h1 className="text-2xl font-display font-semibold text-warm-900">
          Editar empleado
        </h1>
        <p className="text-warm-500 mt-1">{nombreCompleto}</p>
      </div>

      {/* Errores del backend */}
      {backendErrors && Object.keys(backendErrors).length > 0 && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="font-medium text-red-800 mb-2">Por favor corrige los siguientes errores:</p>
          <ul className="text-sm text-red-600 space-y-1">
            {Object.entries(backendErrors).map(([field, fieldErrors]) => (
              <li key={field}>
                <strong className="capitalize">{field.replace(/_/g, " ")}:</strong>{" "}
                {Array.isArray(fieldErrors) ? fieldErrors.join(", ") : String(fieldErrors)}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Error de mutation */}
      {mutation.error && !backendErrors && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
          <div>
            <p className="font-medium text-red-800">Error al actualizar</p>
            <p className="text-sm text-red-600 mt-1">
              Ocurrio un error inesperado. Por favor intenta de nuevo.
            </p>
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

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
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
                <div>
                  <label className="block text-sm font-medium text-warm-700 mb-1">Nombre(s) *</label>
                  <input
                    type="text"
                    placeholder="Juan Carlos"
                    className="w-full px-3 py-2 border border-warm-300 rounded-lg text-warm-900 bg-white placeholder:text-warm-400 focus:ring-2 focus:ring-horizon-500 focus:border-horizon-500"
                    {...register("nombre")}
                  />
                  {errors.nombre && <p className="text-red-500 text-xs mt-1">{errors.nombre.message}</p>}
                </div>
                <div>
                  <label className="block text-sm font-medium text-warm-700 mb-1">Apellido paterno *</label>
                  <input
                    type="text"
                    placeholder="Garcia"
                    className="w-full px-3 py-2 border border-warm-300 rounded-lg text-warm-900 bg-white placeholder:text-warm-400 focus:ring-2 focus:ring-horizon-500 focus:border-horizon-500"
                    {...register("apellido_paterno")}
                  />
                  {errors.apellido_paterno && <p className="text-red-500 text-xs mt-1">{errors.apellido_paterno.message}</p>}
                </div>
                <div>
                  <label className="block text-sm font-medium text-warm-700 mb-1">Apellido materno</label>
                  <input
                    type="text"
                    placeholder="Lopez"
                    className="w-full px-3 py-2 border border-warm-300 rounded-lg text-warm-900 bg-white placeholder:text-warm-400 focus:ring-2 focus:ring-horizon-500 focus:border-horizon-500"
                    {...register("apellido_materno")}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-warm-700 mb-1">Fecha de nacimiento</label>
                  <input
                    type="date"
                    className="w-full px-3 py-2 border border-warm-300 rounded-lg text-warm-900 bg-white focus:ring-2 focus:ring-horizon-500 focus:border-horizon-500"
                    {...register("fecha_nacimiento")}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-warm-700 mb-1">Genero</label>
                  <select
                    className="w-full px-3 py-2 border border-warm-300 rounded-lg text-warm-900 bg-white focus:ring-2 focus:ring-horizon-500 focus:border-horizon-500"
                    {...register("genero")}
                  >
                    <option value="">Seleccionar...</option>
                    {GENERO_OPTIONS.map((opt) => (
                      <option key={opt.value} value={opt.value}>{opt.label}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-warm-700 mb-1">Estado civil</label>
                  <select
                    className="w-full px-3 py-2 border border-warm-300 rounded-lg text-warm-900 bg-white focus:ring-2 focus:ring-horizon-500 focus:border-horizon-500"
                    {...register("estado_civil")}
                  >
                    <option value="">Seleccionar...</option>
                    {ESTADO_CIVIL_OPTIONS.map((opt) => (
                      <option key={opt.value} value={opt.value}>{opt.label}</option>
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
                <div>
                  <label className="block text-sm font-medium text-warm-700 mb-1">RFC</label>
                  <input
                    type="text"
                    placeholder="GARC850101ABC"
                    maxLength={13}
                    className="w-full px-3 py-2 border border-warm-300 rounded-lg text-warm-900 bg-white placeholder:text-warm-400 focus:ring-2 focus:ring-horizon-500 focus:border-horizon-500 uppercase"
                    {...register("rfc")}
                  />
                  {errors.rfc && <p className="text-red-500 text-xs mt-1">{errors.rfc.message}</p>}
                </div>
                <div>
                  <label className="block text-sm font-medium text-warm-700 mb-1">CURP</label>
                  <input
                    type="text"
                    placeholder="GARC850101HDFRRL09"
                    maxLength={18}
                    className="w-full px-3 py-2 border border-warm-300 rounded-lg text-warm-900 bg-white placeholder:text-warm-400 focus:ring-2 focus:ring-horizon-500 focus:border-horizon-500 uppercase"
                    {...register("curp")}
                  />
                  {errors.curp && <p className="text-red-500 text-xs mt-1">{errors.curp.message}</p>}
                </div>
                <div>
                  <label className="block text-sm font-medium text-warm-700 mb-1">NSS (IMSS)</label>
                  <input
                    type="text"
                    placeholder="12345678901"
                    maxLength={11}
                    className="w-full px-3 py-2 border border-warm-300 rounded-lg text-warm-900 bg-white placeholder:text-warm-400 focus:ring-2 focus:ring-horizon-500 focus:border-horizon-500"
                    {...register("nss_imss")}
                  />
                  {errors.nss_imss && <p className="text-red-500 text-xs mt-1">{errors.nss_imss.message}</p>}
                </div>
              </div>
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
                <div>
                  <label className="block text-sm font-medium text-warm-700 mb-1">Email personal</label>
                  <input
                    type="email"
                    placeholder="juan@email.com"
                    className="w-full px-3 py-2 border border-warm-300 rounded-lg text-warm-900 bg-white placeholder:text-warm-400 focus:ring-2 focus:ring-horizon-500 focus:border-horizon-500"
                    {...register("email_personal")}
                  />
                  {errors.email_personal && <p className="text-red-500 text-xs mt-1">{errors.email_personal.message}</p>}
                </div>
                <div>
                  <label className="block text-sm font-medium text-warm-700 mb-1">Email corporativo</label>
                  <input
                    type="email"
                    placeholder="juan@empresa.com"
                    className="w-full px-3 py-2 border border-warm-300 rounded-lg text-warm-900 bg-white placeholder:text-warm-400 focus:ring-2 focus:ring-horizon-500 focus:border-horizon-500"
                    {...register("email_corporativo")}
                  />
                  {errors.email_corporativo && <p className="text-red-500 text-xs mt-1">{errors.email_corporativo.message}</p>}
                </div>
                <div>
                  <label className="block text-sm font-medium text-warm-700 mb-1">Telefono personal</label>
                  <input
                    type="tel"
                    placeholder="55 1234 5678"
                    className="w-full px-3 py-2 border border-warm-300 rounded-lg text-warm-900 bg-white placeholder:text-warm-400 focus:ring-2 focus:ring-horizon-500 focus:border-horizon-500"
                    {...register("telefono_personal")}
                  />
                </div>
                <div className="md:col-span-2 border-t border-warm-100 pt-4 mt-2">
                  <p className="text-sm font-medium text-warm-700 mb-3">Contacto de emergencia</p>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div>
                      <label className="block text-sm text-warm-600 mb-1">Nombre</label>
                      <input
                        type="text"
                        placeholder="Maria Garcia"
                        className="w-full px-3 py-2 border border-warm-300 rounded-lg text-warm-900 bg-white placeholder:text-warm-400 focus:ring-2 focus:ring-horizon-500 focus:border-horizon-500"
                        {...register("emergencia_nombre")}
                      />
                    </div>
                    <div>
                      <label className="block text-sm text-warm-600 mb-1">Parentesco</label>
                      <input
                        type="text"
                        placeholder="Madre"
                        className="w-full px-3 py-2 border border-warm-300 rounded-lg text-warm-900 bg-white placeholder:text-warm-400 focus:ring-2 focus:ring-horizon-500 focus:border-horizon-500"
                        {...register("emergencia_parentesco")}
                      />
                    </div>
                    <div>
                      <label className="block text-sm text-warm-600 mb-1">Telefono</label>
                      <input
                        type="tel"
                        placeholder="55 8765 4321"
                        className="w-full px-3 py-2 border border-warm-300 rounded-lg text-warm-900 bg-white placeholder:text-warm-400 focus:ring-2 focus:ring-horizon-500 focus:border-horizon-500"
                        {...register("emergencia_telefono")}
                      />
                    </div>
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
                <div>
                  <label className="block text-sm font-medium text-warm-700 mb-1">Calle</label>
                  <input
                    type="text"
                    placeholder="Av. Insurgentes Sur"
                    className="w-full px-3 py-2 border border-warm-300 rounded-lg text-warm-900 bg-white placeholder:text-warm-400 focus:ring-2 focus:ring-horizon-500 focus:border-horizon-500"
                    {...register("direccion_calle")}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-warm-700 mb-1">Numero</label>
                  <input
                    type="text"
                    placeholder="1234"
                    className="w-full px-3 py-2 border border-warm-300 rounded-lg text-warm-900 bg-white placeholder:text-warm-400 focus:ring-2 focus:ring-horizon-500 focus:border-horizon-500"
                    {...register("direccion_numero")}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-warm-700 mb-1">Colonia</label>
                  <input
                    type="text"
                    placeholder="Del Valle"
                    className="w-full px-3 py-2 border border-warm-300 rounded-lg text-warm-900 bg-white placeholder:text-warm-400 focus:ring-2 focus:ring-horizon-500 focus:border-horizon-500"
                    {...register("direccion_colonia")}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-warm-700 mb-1">Codigo Postal</label>
                  <input
                    type="text"
                    placeholder="03100"
                    maxLength={5}
                    className="w-full px-3 py-2 border border-warm-300 rounded-lg text-warm-900 bg-white placeholder:text-warm-400 focus:ring-2 focus:ring-horizon-500 focus:border-horizon-500"
                    {...register("direccion_cp")}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-warm-700 mb-1">Municipio/Alcaldia</label>
                  <input
                    type="text"
                    placeholder="Benito Juarez"
                    className="w-full px-3 py-2 border border-warm-300 rounded-lg text-warm-900 bg-white placeholder:text-warm-400 focus:ring-2 focus:ring-horizon-500 focus:border-horizon-500"
                    {...register("direccion_municipio")}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-warm-700 mb-1">Estado</label>
                  <select
                    className="w-full px-3 py-2 border border-warm-300 rounded-lg text-warm-900 bg-white focus:ring-2 focus:ring-horizon-500 focus:border-horizon-500"
                    {...register("direccion_estado")}
                  >
                    <option value="">Seleccionar...</option>
                    {ESTADOS_MEXICO.map((estado) => (
                      <option key={estado} value={estado}>{estado}</option>
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
                <div>
                  <label className="block text-sm font-medium text-warm-700 mb-1">Fecha de ingreso *</label>
                  <input
                    type="date"
                    className="w-full px-3 py-2 border border-warm-300 rounded-lg text-warm-900 bg-white focus:ring-2 focus:ring-horizon-500 focus:border-horizon-500"
                    {...register("fecha_ingreso")}
                  />
                  {errors.fecha_ingreso && <p className="text-red-500 text-xs mt-1">{errors.fecha_ingreso.message}</p>}
                </div>
                <div>
                  <label className="block text-sm font-medium text-warm-700 mb-1">Puesto</label>
                  <input
                    type="text"
                    placeholder="Desarrollador Senior"
                    className="w-full px-3 py-2 border border-warm-300 rounded-lg text-warm-900 bg-white placeholder:text-warm-400 focus:ring-2 focus:ring-horizon-500 focus:border-horizon-500"
                    {...register("puesto")}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-warm-700 mb-1">Departamento</label>
                  <input
                    type="text"
                    placeholder="Tecnologia"
                    className="w-full px-3 py-2 border border-warm-300 rounded-lg text-warm-900 bg-white placeholder:text-warm-400 focus:ring-2 focus:ring-horizon-500 focus:border-horizon-500"
                    {...register("departamento")}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-warm-700 mb-1">Tipo de contrato</label>
                  <select
                    className="w-full px-3 py-2 border border-warm-300 rounded-lg text-warm-900 bg-white focus:ring-2 focus:ring-horizon-500 focus:border-horizon-500"
                    {...register("tipo_contrato")}
                  >
                    <option value="">Seleccionar...</option>
                    {TIPO_CONTRATO_OPTIONS.map((opt) => (
                      <option key={opt.value} value={opt.value}>{opt.label}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-warm-700 mb-1">Jornada</label>
                  <select
                    className="w-full px-3 py-2 border border-warm-300 rounded-lg text-warm-900 bg-white focus:ring-2 focus:ring-horizon-500 focus:border-horizon-500"
                    {...register("jornada")}
                  >
                    <option value="">Seleccionar...</option>
                    {JORNADA_OPTIONS.map((opt) => (
                      <option key={opt.value} value={opt.value}>{opt.label}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-warm-700 mb-1">Modalidad</label>
                  <select
                    className="w-full px-3 py-2 border border-warm-300 rounded-lg text-warm-900 bg-white focus:ring-2 focus:ring-horizon-500 focus:border-horizon-500"
                    {...register("modalidad")}
                  >
                    <option value="">Seleccionar...</option>
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
                <div>
                  <label className="block text-sm font-medium text-warm-700 mb-1">Salario diario</label>
                  <input
                    type="number"
                    step="0.01"
                    placeholder="850.00"
                    className="w-full px-3 py-2 border border-warm-300 rounded-lg text-warm-900 bg-white placeholder:text-warm-400 focus:ring-2 focus:ring-horizon-500 focus:border-horizon-500"
                    {...register("salario_diario")}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-warm-700 mb-1">Banco</label>
                  <select
                    className="w-full px-3 py-2 border border-warm-300 rounded-lg text-warm-900 bg-white focus:ring-2 focus:ring-horizon-500 focus:border-horizon-500"
                    {...register("banco")}
                  >
                    <option value="">Seleccionar...</option>
                    {BANCOS_MEXICO.map((b) => (
                      <option key={b.value} value={b.value}>{b.label}</option>
                    ))}
                  </select>
                </div>
                {banco && (
                  <div className="md:col-span-2">
                    <label className="block text-sm font-medium text-warm-700 mb-1">CLABE interbancaria</label>
                    <input
                      type="text"
                      placeholder="012345678901234567"
                      maxLength={18}
                      className="w-full px-3 py-2 border border-warm-300 rounded-lg text-warm-900 bg-white placeholder:text-warm-400 focus:ring-2 focus:ring-horizon-500 focus:border-horizon-500"
                      {...register("clabe")}
                    />
                    {errors.clabe && <p className="text-red-500 text-xs mt-1">{errors.clabe.message}</p>}
                  </div>
                )}
              </div>
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
                <label className="block text-sm font-medium text-warm-700 mb-1">Jefe directo</label>
                <select
                  className="w-full px-3 py-2 border border-warm-300 rounded-lg text-warm-900 bg-white focus:ring-2 focus:ring-horizon-500 focus:border-horizon-500"
                  {...register("jefe_directo")}
                >
                  <option value="">Sin jefe asignado</option>
                  {Array.isArray(empleadosLista) &&
                    empleadosLista
                      .filter((e: { estado: string; id: string }) => e.estado === "activo" && e.id !== empleadoId)
                      .map((emp: { id: string; nombre: string; apellido_paterno: string; puesto?: string }) => (
                        <option key={emp.id} value={emp.id}>
                          {emp.nombre} {emp.apellido_paterno} - {emp.puesto || "Sin puesto"}
                        </option>
                      ))}
                </select>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Input oculto para empresa */}
        <input type="hidden" {...register("empresa")} />

        {/* Botones de navegacion */}
        <div className="flex items-center justify-between pt-4 border-t border-warm-200">
          <Link href={`/empleados/${empleadoId}`}>
            <Button variant="outline">Cancelar</Button>
          </Link>
          <div className="flex gap-2">
            {activeSection !== "personal" && (
              <Button type="button" variant="outline" onClick={goToPrevSection}>
                <ChevronLeft className="w-4 h-4 mr-1" />
                Anterior
              </Button>
            )}
            {activeSection !== "jerarquia" ? (
              <Button type="button" onClick={goToNextSection}>
                Siguiente
                <ChevronRight className="w-4 h-4 ml-1" />
              </Button>
            ) : (
              <Button type="submit" disabled={isSubmitting || mutation.isPending}>
                {isSubmitting || mutation.isPending ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Guardando...
                  </>
                ) : (
                  <>
                    <Save className="w-4 h-4 mr-2" />
                    Guardar cambios
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
