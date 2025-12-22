"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { useAuthStore } from "@/stores/auth-store";
import { vacacionesApi, reportesApi } from "@/lib/api";
import { ResumenVacaciones, SolicitudVacaciones, DashboardEmpresa } from "@/types";
import { formatCurrency, exportToExcel, CHART_COLORS } from "@/lib/export-utils";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";
import { toast } from "sonner";
import {
  Calendar,
  Clock,
  CheckCircle,
  XCircle,
  FileSpreadsheet,
  Search,
  AlertTriangle,
} from "lucide-react";
import {
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";

export function VacationReport() {
  const { empresaActual } = useAuthStore();
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedYear] = useState(new Date().getFullYear());

  // Dashboard empresa para datos de vacaciones
  const { data: dashboardData, isLoading: loadingDashboard } = useQuery({
    queryKey: ["dashboard-empresa-vacaciones", empresaActual?.id],
    queryFn: () => reportesApi.getDashboardEmpresa(empresaActual!.id),
    enabled: !!empresaActual?.id,
  });

  // Resumen de vacaciones
  const { data: resumenData, isLoading: loadingResumen } = useQuery({
    queryKey: ["vacaciones-resumen", empresaActual?.id],
    queryFn: () => vacacionesApi.getResumen(),
    enabled: !!empresaActual?.id,
  });

  // Estadisticas de solicitudes
  const { data: estadisticasData } = useQuery({
    queryKey: ["vacaciones-estadisticas", empresaActual?.id],
    queryFn: () => vacacionesApi.getEstadisticas(),
    enabled: !!empresaActual?.id,
  });

  // Solicitudes
  const { data: solicitudesData, isLoading: loadingSolicitudes } = useQuery({
    queryKey: ["vacaciones-solicitudes", empresaActual?.id],
    queryFn: async () => {
      const response = await vacacionesApi.getSolicitudes();
      return response.results || response;
    },
    enabled: !!empresaActual?.id,
  });

  const dashboard = dashboardData as DashboardEmpresa | undefined;
  const resumen = resumenData as ResumenVacaciones | undefined;
  const solicitudes = (solicitudesData as SolicitudVacaciones[]) || [];
  const estadisticas = estadisticasData as {
    pendientes?: number;
    aprobadas?: number;
    rechazadas?: number;
  } | undefined;

  // KPIs
  const diasOtorgados = dashboard?.vacaciones?.dias_pendientes_total || 0;
  const diasTomados = dashboard?.vacaciones?.dias_tomados_ano || 0;
  const diasPendientes = resumen?.dias_disponibles || diasOtorgados - diasTomados;
  const solicitudesPendientes = estadisticas?.pendientes || 0;

  // Datos para pie chart de solicitudes
  const datosSolicitudes = [
    {
      name: "Aprobadas",
      value: estadisticas?.aprobadas || 0,
      color: CHART_COLORS.secondary,
    },
    {
      name: "Pendientes",
      value: estadisticas?.pendientes || 0,
      color: CHART_COLORS.accent,
    },
    {
      name: "Rechazadas",
      value: estadisticas?.rechazadas || 0,
      color: CHART_COLORS.error,
    },
  ].filter((d) => d.value > 0);

  // Datos para grafico de barras - dias por mes (simulado desde solicitudes aprobadas)
  const diasPorMes = Array(12)
    .fill(0)
    .map((_, i) => {
      const mes = i;
      const diasMes = solicitudes
        .filter((s) => {
          if (s.estado !== "aprobada") return false;
          const fecha = new Date(s.fecha_inicio);
          return fecha.getMonth() === mes && fecha.getFullYear() === selectedYear;
        })
        .reduce((sum, s) => sum + (s.dias_solicitados || 0), 0);
      return {
        mes: ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"][i],
        dias: diasMes,
      };
    });

  // Saldos por empleado (del resumen)
  const saldosPorEmpleado = resumen
    ? [
        {
          empleado_id: resumen.empleado_id,
          empleado_nombre: resumen.empleado_nombre,
          antiguedad_anos: resumen.antiguedad_anios,
          dias_correspondientes: resumen.dias_correspondientes_anio_actual,
          dias_tomados: resumen.dias_tomados_anio_actual,
          dias_pendientes: resumen.dias_disponibles,
        },
      ]
    : [];

  // Filtrar saldos
  const saldosFiltrados = saldosPorEmpleado.filter(
    (s) =>
      !searchTerm ||
      s.empleado_nombre?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const handleExportExcel = () => {
    if (saldosFiltrados.length === 0 && solicitudes.length === 0) {
      toast.error("No hay datos para exportar");
      return;
    }

    const dataSolicitudes = solicitudes.map((s) => ({
      Empleado: s.empleado_nombre || "",
      "Fecha Inicio": s.fecha_inicio,
      "Fecha Fin": s.fecha_fin,
      "Dias Solicitados": s.dias_solicitados,
      Estado: s.estado_display || s.estado,
      "Fecha Solicitud": s.created_at?.split("T")[0] || "",
    }));

    exportToExcel(dataSolicitudes, `vacaciones_${selectedYear}`, "Solicitudes");
    toast.success("Archivo Excel generado");
  };

  const isLoading = loadingDashboard || loadingResumen || loadingSolicitudes;

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="grid gap-4 sm:grid-cols-4">
          {[1, 2, 3, 4].map((i) => (
            <Card key={i}>
              <CardContent className="p-4">
                <Skeleton className="h-4 w-24 mb-2" />
                <Skeleton className="h-8 w-32" />
              </CardContent>
            </Card>
          ))}
        </div>
        <div className="grid gap-6 lg:grid-cols-2">
          <Card>
            <CardHeader>
              <Skeleton className="h-5 w-40" />
            </CardHeader>
            <CardContent>
              <Skeleton className="h-64 w-full" />
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <Skeleton className="h-5 w-40" />
            </CardHeader>
            <CardContent>
              <Skeleton className="h-64 w-full" />
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header con ano y exportar */}
      <div className="flex justify-between items-center">
        <div className="flex items-center gap-4">
          <label className="text-sm font-medium text-warm-700">Ano:</label>
          <span className="text-lg font-semibold text-warm-900">{selectedYear}</span>
        </div>
        <Button variant="outline" onClick={handleExportExcel}>
          <FileSpreadsheet className="h-4 w-4 mr-2" />
          Exportar Excel
        </Button>
      </div>

      {/* KPIs */}
      <div className="grid gap-4 sm:grid-cols-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-sage-50">
                <Calendar className="h-5 w-5 text-sage-600" strokeWidth={1.5} />
              </div>
              <div>
                <p className="text-sm text-warm-500">Dias otorgados</p>
                <p className="text-2xl font-semibold text-warm-900">
                  {diasOtorgados + diasTomados}
                </p>
                <p className="text-xs text-warm-400">este ano</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-horizon-50">
                <CheckCircle className="h-5 w-5 text-horizon-600" strokeWidth={1.5} />
              </div>
              <div>
                <p className="text-sm text-warm-500">Dias tomados</p>
                <p className="text-2xl font-semibold text-warm-900">
                  {diasTomados}
                </p>
                <p className="text-xs text-warm-400">
                  {diasOtorgados + diasTomados > 0
                    ? `${((diasTomados / (diasOtorgados + diasTomados)) * 100).toFixed(1)}%`
                    : "0%"}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-amber-50">
                <Clock className="h-5 w-5 text-amber-600" strokeWidth={1.5} />
              </div>
              <div>
                <p className="text-sm text-warm-500">Dias pendientes</p>
                <p className="text-2xl font-semibold text-warm-900">
                  {diasPendientes}
                </p>
                <p className="text-xs text-warm-400">
                  {diasOtorgados + diasTomados > 0
                    ? `${((diasPendientes / (diasOtorgados + diasTomados)) * 100).toFixed(1)}%`
                    : "0%"}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-red-50">
                <AlertTriangle className="h-5 w-5 text-red-500" strokeWidth={1.5} />
              </div>
              <div>
                <p className="text-sm text-warm-500">Pendientes aprobar</p>
                <p className="text-2xl font-semibold text-warm-900">
                  {solicitudesPendientes}
                </p>
                <p className="text-xs text-warm-400">solicitudes</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Graficos */}
      <div className="grid gap-6 lg:grid-cols-2">
        {/* Pie chart de solicitudes */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Solicitudes por estado</CardTitle>
          </CardHeader>
          <CardContent>
            {datosSolicitudes.length === 0 ? (
              <div className="h-64 flex items-center justify-center text-warm-400">
                Sin solicitudes registradas
              </div>
            ) : (
              <ResponsiveContainer width="100%" height={280}>
                <PieChart>
                  <Pie
                    data={datosSolicitudes}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={100}
                    paddingAngle={2}
                    dataKey="value"
                    label={({ name, value }) => `${name}: ${value}`}
                  >
                    {datosSolicitudes.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            )}
          </CardContent>
        </Card>

        {/* Grafico de barras - dias por mes */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base">
              Dias de vacaciones por mes
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={diasPorMes}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e5e5" />
                <XAxis dataKey="mes" tick={{ fontSize: 11 }} />
                <YAxis tick={{ fontSize: 11 }} />
                <Tooltip />
                <Bar
                  dataKey="dias"
                  name="Dias tomados"
                  fill={CHART_COLORS.primary}
                  radius={[4, 4, 0, 0]}
                />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* Tabla de saldos por empleado */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle className="text-base">Saldo por empleado</CardTitle>
          <div className="relative w-64">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-warm-400" />
            <Input
              placeholder="Buscar empleado..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-9"
            />
          </div>
        </CardHeader>
        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-warm-50 border-b border-warm-200">
                <tr>
                  <th className="text-left p-3 font-medium text-warm-700">
                    Empleado
                  </th>
                  <th className="text-right p-3 font-medium text-warm-700">
                    Antiguedad
                  </th>
                  <th className="text-right p-3 font-medium text-warm-700">
                    Dias correspondientes
                  </th>
                  <th className="text-right p-3 font-medium text-warm-700">
                    Dias tomados
                  </th>
                  <th className="text-right p-3 font-medium text-warm-700">
                    Dias pendientes
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-warm-100">
                {saldosFiltrados.map((saldo) => (
                  <tr key={saldo.empleado_id}>
                    <td className="p-3 text-warm-900 font-medium">
                      {saldo.empleado_nombre}
                    </td>
                    <td className="p-3 text-right text-warm-600">
                      {saldo.antiguedad_anos} anos
                    </td>
                    <td className="p-3 text-right text-warm-600">
                      {saldo.dias_correspondientes}
                    </td>
                    <td className="p-3 text-right text-warm-600">
                      {saldo.dias_tomados}
                    </td>
                    <td className="p-3 text-right">
                      <span
                        className={`font-medium ${
                          saldo.dias_pendientes > 0
                            ? "text-amber-600"
                            : "text-sage-600"
                        }`}
                      >
                        {saldo.dias_pendientes}
                      </span>
                    </td>
                  </tr>
                ))}
                {saldosFiltrados.length === 0 && (
                  <tr>
                    <td colSpan={5} className="p-8 text-center text-warm-400">
                      {searchTerm
                        ? "No se encontraron empleados"
                        : "Sin datos de vacaciones disponibles"}
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      {/* Ultimas solicitudes */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Ultimas solicitudes</CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          <div className="divide-y divide-warm-100">
            {solicitudes.slice(0, 10).map((solicitud) => (
              <div
                key={solicitud.id}
                className="flex items-center justify-between p-4"
              >
                <div>
                  <p className="font-medium text-warm-900">
                    {solicitud.empleado_nombre}
                  </p>
                  <p className="text-sm text-warm-500">
                    {solicitud.fecha_inicio} - {solicitud.fecha_fin} (
                    {solicitud.dias_solicitados} dias)
                  </p>
                </div>
                <span
                  className={`px-2 py-1 rounded-full text-xs font-medium ${
                    solicitud.estado === "aprobada"
                      ? "bg-sage-100 text-sage-700"
                      : solicitud.estado === "pendiente"
                      ? "bg-amber-100 text-amber-700"
                      : solicitud.estado === "rechazada"
                      ? "bg-red-100 text-red-700"
                      : "bg-warm-100 text-warm-700"
                  }`}
                >
                  {solicitud.estado_display || solicitud.estado}
                </span>
              </div>
            ))}
            {solicitudes.length === 0 && (
              <div className="p-8 text-center text-warm-400">
                Sin solicitudes registradas
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
