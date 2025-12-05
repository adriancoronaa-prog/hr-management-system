"use client";

import { useState, useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useForm } from "react-hook-form";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import Link from "next/link";
import api from "@/lib/api";
import { useAuthStore } from "@/stores/auth-store";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { TIPO_CONTRATO_LARGO_OPTIONS, JORNADA_OPTIONS } from "@/types";
import {
  ArrowLeft,
  FileText,
  User,
  Calendar,
  DollarSign,
  Briefcase,
  Loader2,
  AlertCircle,
  Save,
} from "lucide-react";

interface ContratoFormData {
  empleado: string;
  tipo_contrato: string;
  fecha_inicio: string;
  fecha_fin?: string;
  puesto?: string;
  departamento?: string;
  salario_mensual?: number | string;
  salario_diario?: number | string;
  jornada?: string;
  horario?: string;
  condiciones_especiales?: string;
}

export default function NuevoContratoPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const queryClient = useQueryClient();
  const { user, empresaActual } = useAuthStore();
  const [mounted, setMounted] = useState(false);
  const [backendErrors, setBackendErrors] = useState<Record<string, string[]> | null>(null);

  // Si viene de un empleado especifico
  const empleadoIdParam = searchParams.get("empleado");

  useEffect(() => {
    setMounted(true);
  }, []);

  const canCreate = user?.rol === "admin" || user?.rol === "rrhh" || user?.rol === "empleador";

  // Cargar lista de empleados
  const { data: empleados } = useQuery({
    queryKey: ["empleados", empresaActual?.id],
    queryFn: async () => {
      const response = await api.get("/empleados/");
      const data = response.data;
      return Array.isArray(data) ? data : data?.results || [];
    },
    enabled: mounted && !!empresaActual?.id,
  });

  // Si viene con empleado preseleccionado, cargar sus datos
  const { data: empleadoSeleccionado } = useQuery({
    queryKey: ["empleado", empleadoIdParam],
    queryFn: async () => {
      const response = await api.get(`/empleados/${empleadoIdParam}/`);
      return response.data;
    },
    enabled: mounted && !!empleadoIdParam,
  });

  const {
    register,
    handleSubmit,
    watch,
    setValue,
    formState: { errors, isSubmitting },
  } = useForm<ContratoFormData>({
    defaultValues: {
      empleado: empleadoIdParam || "",
      tipo_contrato: "indefinido",
      fecha_inicio: new Date().toISOString().split("T")[0],
      jornada: "diurna",
    },
  });

  // Cuando se carga el empleado, prellenar datos
  useEffect(() => {
    if (empleadoSeleccionado) {
      setValue("empleado", empleadoSeleccionado.id);
      setValue("puesto", empleadoSeleccionado.puesto || "");
      setValue("departamento", empleadoSeleccionado.departamento || "");
      setValue("salario_mensual", empleadoSeleccionado.salario_mensual || "");
      setValue("salario_diario", empleadoSeleccionado.salario_diario || "");
    }
  }, [empleadoSeleccionado, setValue]);

  const tipoContrato = watch("tipo_contrato");
  const empleadoId = watch("empleado");

  // Cuando cambia el empleado seleccionado, cargar sus datos
  const empleadoActual = Array.isArray(empleados)
    ? empleados.find((e: { id: string }) => e.id === empleadoId)
    : null;

  useEffect(() => {
    if (empleadoActual && !empleadoIdParam) {
      setValue("puesto", empleadoActual.puesto || "");
      setValue("departamento", empleadoActual.departamento || "");
      setValue("salario_mensual", empleadoActual.salario_mensual || "");
      setValue("salario_diario", empleadoActual.salario_diario || "");
    }
  }, [empleadoActual, setValue, empleadoIdParam]);

  const mutation = useMutation({
    mutationFn: async (data: ContratoFormData) => {
      setBackendErrors(null);

      // Limpiar campos vacios
      const cleanData: Record<string, unknown> = {};
      Object.entries(data).forEach(([key, value]) => {
        if (value !== "" && value !== null && value !== undefined) {
          cleanData[key] = value;
        }
      });

      // Si es indefinido, no enviar fecha_fin
      if (cleanData.tipo_contrato === "indefinido") {
        delete cleanData.fecha_fin;
      }

      // Convertir salarios a numeros
      if (cleanData.salario_diario) {
        cleanData.salario_diario = parseFloat(String(cleanData.salario_diario));
      }
      if (cleanData.salario_mensual) {
        cleanData.salario_mensual = parseFloat(String(cleanData.salario_mensual));
      }

      console.log("=== CREANDO CONTRATO ===");
      console.log(JSON.stringify(cleanData, null, 2));

      try {
        const response = await api.post("/contratos/", cleanData);
        return response.data;
      } catch (error: unknown) {
        const axiosError = error as { response?: { data?: Record<string, string[]> } };
        console.error("Error al crear contrato:", axiosError.response?.data);
        if (axiosError.response?.data) {
          setBackendErrors(axiosError.response.data);
        }
        throw error;
      }
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["contratos"] });
      queryClient.invalidateQueries({ queryKey: ["contratos-resumen"] });
      router.push(`/contratos/${data.id}`);
    },
  });

  const onSubmit = (data: ContratoFormData) => {
    mutation.mutate(data);
  };

  if (!mounted) return null;

  if (!canCreate) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] text-center">
        <AlertCircle className="w-16 h-16 text-amber-500 mb-4" />
        <h1 className="text-xl font-semibold text-warm-900">Acceso restringido</h1>
        <p className="text-warm-500 mt-2">No tienes permisos para crear contratos.</p>
        <Link href="/contratos">
          <Button variant="outline" className="mt-4">
            Volver a contratos
          </Button>
        </Link>
      </div>
    );
  }

  const empleadosList = Array.isArray(empleados)
    ? empleados.filter((e: { estado: string }) => e.estado === "activo")
    : [];

  return (
    <div className="max-w-3xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <Link
          href="/contratos"
          className="inline-flex items-center text-sm text-warm-500 hover:text-warm-700 mb-4"
        >
          <ArrowLeft className="w-4 h-4 mr-1" />
          Volver a contratos
        </Link>
        <h1 className="text-2xl font-display font-semibold text-warm-900">Nuevo contrato</h1>
        <p className="text-warm-500 mt-1">
          Registrar contrato laboral en {empresaActual?.nombre_comercial || empresaActual?.razon_social}
        </p>
      </div>

      {/* Errores del backend */}
      {backendErrors && Object.keys(backendErrors).length > 0 && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="font-medium text-red-800 mb-2">Por favor corrige los siguientes errores:</p>
          <ul className="text-sm text-red-600 space-y-1">
            {Object.entries(backendErrors).map(([field, errs]) => (
              <li key={field}>
                <strong className="capitalize">{field.replace(/_/g, " ")}:</strong>{" "}
                {Array.isArray(errs) ? errs.join(", ") : String(errs)}
              </li>
            ))}
          </ul>
        </div>
      )}

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        {/* Empleado */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <User className="w-5 h-5 text-horizon-600" />
              Empleado
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div>
              <label className="block text-sm font-medium text-warm-700 mb-1">
                Seleccionar empleado *
              </label>
              <select
                className="w-full px-3 py-2 border border-warm-300 rounded-lg text-warm-900 bg-white focus:ring-2 focus:ring-horizon-500 focus:border-horizon-500"
                {...register("empleado", { required: "Debe seleccionar un empleado" })}
              >
                <option value="">Seleccionar...</option>
                {empleadosList.map((emp: { id: string; nombre: string; apellido_paterno: string; apellido_materno?: string; puesto?: string }) => (
                  <option key={emp.id} value={emp.id}>
                    {emp.nombre} {emp.apellido_paterno} {emp.apellido_materno || ""} - {emp.puesto || "Sin puesto"}
                  </option>
                ))}
              </select>
              {errors.empleado && (
                <p className="text-red-500 text-xs mt-1">{errors.empleado.message}</p>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Tipo y Fechas */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Calendar className="w-5 h-5 text-horizon-600" />
              Tipo y vigencia
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-warm-700 mb-1">
                  Tipo de contrato *
                </label>
                <select
                  className="w-full px-3 py-2 border border-warm-300 rounded-lg text-warm-900 bg-white focus:ring-2 focus:ring-horizon-500 focus:border-horizon-500"
                  {...register("tipo_contrato", { required: "Debe seleccionar un tipo" })}
                >
                  {TIPO_CONTRATO_LARGO_OPTIONS.map((opt) => (
                    <option key={opt.value} value={opt.value}>
                      {opt.label}
                    </option>
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
                    <option key={opt.value} value={opt.value}>
                      {opt.label}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-warm-700 mb-1">
                  Fecha de inicio *
                </label>
                <input
                  type="date"
                  className="w-full px-3 py-2 border border-warm-300 rounded-lg text-warm-900 bg-white focus:ring-2 focus:ring-horizon-500 focus:border-horizon-500"
                  {...register("fecha_inicio", { required: "La fecha de inicio es requerida" })}
                />
                {errors.fecha_inicio && (
                  <p className="text-red-500 text-xs mt-1">{errors.fecha_inicio.message}</p>
                )}
              </div>
              {tipoContrato !== "indefinido" && (
                <div>
                  <label className="block text-sm font-medium text-warm-700 mb-1">
                    Fecha de fin
                  </label>
                  <input
                    type="date"
                    className="w-full px-3 py-2 border border-warm-300 rounded-lg text-warm-900 bg-white focus:ring-2 focus:ring-horizon-500 focus:border-horizon-500"
                    {...register("fecha_fin")}
                  />
                  <p className="text-xs text-warm-400 mt-1">
                    Dejar vacio si el contrato no tiene fecha de termino definida
                  </p>
                </div>
              )}
              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-warm-700 mb-1">Horario</label>
                <input
                  type="text"
                  placeholder="Ej: Lunes a Viernes 9:00 - 18:00"
                  className="w-full px-3 py-2 border border-warm-300 rounded-lg text-warm-900 bg-white placeholder:text-warm-400 focus:ring-2 focus:ring-horizon-500 focus:border-horizon-500"
                  {...register("horario")}
                />
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Puesto y Departamento */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Briefcase className="w-5 h-5 text-horizon-600" />
              Puesto
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-warm-700 mb-1">Puesto</label>
                <input
                  type="text"
                  placeholder="Ej: Desarrollador Senior"
                  className="w-full px-3 py-2 border border-warm-300 rounded-lg text-warm-900 bg-white placeholder:text-warm-400 focus:ring-2 focus:ring-horizon-500 focus:border-horizon-500"
                  {...register("puesto")}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-warm-700 mb-1">Departamento</label>
                <input
                  type="text"
                  placeholder="Ej: Tecnologia"
                  className="w-full px-3 py-2 border border-warm-300 rounded-lg text-warm-900 bg-white placeholder:text-warm-400 focus:ring-2 focus:ring-horizon-500 focus:border-horizon-500"
                  {...register("departamento")}
                />
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Salario */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <DollarSign className="w-5 h-5 text-horizon-600" />
              Condiciones economicas
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-warm-700 mb-1">
                  Salario diario
                </label>
                <input
                  type="number"
                  step="0.01"
                  placeholder="850.00"
                  className="w-full px-3 py-2 border border-warm-300 rounded-lg text-warm-900 bg-white placeholder:text-warm-400 focus:ring-2 focus:ring-horizon-500 focus:border-horizon-500"
                  {...register("salario_diario")}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-warm-700 mb-1">
                  Salario mensual
                </label>
                <input
                  type="number"
                  step="0.01"
                  placeholder="25500.00"
                  className="w-full px-3 py-2 border border-warm-300 rounded-lg text-warm-900 bg-white placeholder:text-warm-400 focus:ring-2 focus:ring-horizon-500 focus:border-horizon-500"
                  {...register("salario_mensual")}
                />
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Observaciones */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileText className="w-5 h-5 text-horizon-600" />
              Condiciones especiales
            </CardTitle>
          </CardHeader>
          <CardContent>
            <textarea
              placeholder="Notas adicionales sobre el contrato..."
              rows={3}
              className="w-full px-3 py-2 border border-warm-300 rounded-lg text-warm-900 bg-white placeholder:text-warm-400 focus:ring-2 focus:ring-horizon-500 focus:border-horizon-500 resize-none"
              {...register("condiciones_especiales")}
            />
          </CardContent>
        </Card>

        {/* Botones */}
        <div className="flex items-center justify-between pt-4">
          <Link href="/contratos">
            <Button variant="outline">Cancelar</Button>
          </Link>
          <Button type="submit" disabled={isSubmitting || mutation.isPending}>
            {isSubmitting || mutation.isPending ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                Guardando...
              </>
            ) : (
              <>
                <Save className="w-4 h-4 mr-2" />
                Crear contrato
              </>
            )}
          </Button>
        </div>
      </form>
    </div>
  );
}
