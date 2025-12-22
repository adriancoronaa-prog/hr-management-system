"use client";

import { useQuery } from "@tanstack/react-query";
import { useAuthStore } from "@/stores/auth-store";
import { reportesApi, nominaApi, contratosApi } from "@/lib/api";
import { DashboardEmpresa, PeriodoNomina, Contrato } from "@/types";
import {
  formatCurrency,
  downloadBlob,
  CHART_COLORS,
} from "@/lib/export-utils";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { toast } from "sonner";
import {
  Users,
  FileText,
  Calendar,
  DollarSign,
  Download,
  TrendingUp,
  TrendingDown,
  AlertTriangle,
  Loader2,
} from "lucide-react";
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";
import { useState } from "react";

export function ExecutiveDashboard() {
  const { empresaActual } = useAuthStore();
  const [downloading, setDownloading] = useState(false);

  // Dashboard principal
  const { data: dashboard, isLoading } = useQuery({
    queryKey: ["dashboard-empresa", empresaActual?.id],
    queryFn: () => reportesApi.getDashboardEmpresa(empresaActual!.id),
    enabled: !!empresaActual?.id,
    staleTime: 5 * 60 * 1000, // 5 minutos
  });

  // Periodos de nomina para grafico
  const { data: periodosData } = useQuery({
    queryKey: ["nomina-periodos-reporte", empresaActual?.id],
    queryFn: async () => {
      const response = await nominaApi.getPeriodos();
      return response.results || response;
    },
    enabled: !!empresaActual?.id,
  });

  // Contratos por vencer
  const { data: contratosPorVencer } = useQuery({
    queryKey: ["contratos-por-vencer", empresaActual?.id],
    queryFn: async () => {
      const response = await contratosApi.getPorVencer();
      return response.results || response;
    },
    enabled: !!empresaActual?.id,
  });

  const data = dashboard as DashboardEmpresa | undefined;
  const periodos = (periodosData as PeriodoNomina[]) || [];
  const contratos = (contratosPorVencer as Contrato[]) || [];

  // Preparar datos para grafico de nomina
  const datosNomina = periodos
    .filter((p) => p.estado === "pagado" || p.estado === "timbrado")
    .slice(0, 12)
    .reverse()
    .map((p) => ({
      periodo: `P${p.numero_periodo}`,
      neto: p.total_neto || 0,
      percepciones: p.total_percepciones || 0,
      deducciones: p.total_deducciones || 0,
    }));

  // Datos para pie chart de departamentos
  const datosDepartamentos = (data?.empleados?.por_departamento || []).map(
    (d, i) => ({
      name: d.departamento || "Sin departamento",
      value: d.total,
      color: CHART_COLORS.palette[i % CHART_COLORS.palette.length],
    })
  );

  // Calcular variacion
  const variacionNomina =
    periodos.length >= 2
      ? (((periodos[0]?.total_neto || 0) - (periodos[1]?.total_neto || 0)) /
          (periodos[1]?.total_neto || 1)) *
        100
      : 0;

  const handleDownloadPdf = async () => {
    if (!empresaActual?.id) return;
    setDownloading(true);
    try {
      const blob = await reportesApi.getDashboardEmpresaPdf(empresaActual.id);
      downloadBlob(blob, `dashboard_${empresaActual.rfc || empresaActual.id}.pdf`);
      toast.success("Dashboard descargado");
    } catch {
      toast.error("Error al descargar el dashboard");
    } finally {
      setDownloading(false);
    }
  };

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
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

  if (!data) {
    return (
      <Card>
        <CardContent className="flex flex-col items-center justify-center py-12">
          <AlertTriangle className="h-12 w-12 text-amber-500 mb-4" />
          <h3 className="text-lg font-semibold text-warm-900 mb-2">
            Sin datos disponibles
          </h3>
          <p className="text-warm-500 text-center max-w-sm">
            No se encontraron datos para generar el dashboard. Verifica que la
            empresa tenga empleados registrados.
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header con boton de descarga */}
      <div className="flex justify-end">
        <Button
          variant="outline"
          onClick={handleDownloadPdf}
          disabled={downloading}
        >
          {downloading ? (
            <Loader2 className="h-4 w-4 mr-2 animate-spin" />
          ) : (
            <Download className="h-4 w-4 mr-2" />
          )}
          Exportar PDF
        </Button>
      </div>

      {/* KPIs */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-horizon-50">
                <Users className="h-5 w-5 text-horizon-600" strokeWidth={1.5} />
              </div>
              <div>
                <p className="text-sm text-warm-500">Empleados activos</p>
                <p className="text-2xl font-semibold text-warm-900">
                  {data.empleados?.activos || 0}
                </p>
                <p className="text-xs text-warm-400">
                  de {data.empleados?.total || 0} totales
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-amber-50">
                <FileText
                  className="h-5 w-5 text-amber-600"
                  strokeWidth={1.5}
                />
              </div>
              <div>
                <p className="text-sm text-warm-500">Contratos por vencer</p>
                <p className="text-2xl font-semibold text-warm-900">
                  {contratos.length}
                </p>
                <p className="text-xs text-warm-400">proximos 30 dias</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-sage-50">
                <Calendar
                  className="h-5 w-5 text-sage-600"
                  strokeWidth={1.5}
                />
              </div>
              <div>
                <p className="text-sm text-warm-500">Dias vac. pendientes</p>
                <p className="text-2xl font-semibold text-warm-900">
                  {data.vacaciones?.dias_pendientes_total || 0}
                </p>
                <p className="text-xs text-warm-400">
                  {data.vacaciones?.dias_tomados_ano || 0} tomados este ano
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-horizon-50">
                <DollarSign
                  className="h-5 w-5 text-horizon-600"
                  strokeWidth={1.5}
                />
              </div>
              <div>
                <p className="text-sm text-warm-500">Nomina mensual</p>
                <p className="text-2xl font-semibold text-sage-700">
                  {formatCurrency(data.empleados?.nomina_mensual_estimada)}
                </p>
                <div className="flex items-center gap-1 text-xs">
                  {variacionNomina >= 0 ? (
                    <>
                      <TrendingUp className="h-3 w-3 text-sage-600" />
                      <span className="text-sage-600">
                        +{variacionNomina.toFixed(1)}%
                      </span>
                    </>
                  ) : (
                    <>
                      <TrendingDown className="h-3 w-3 text-red-500" />
                      <span className="text-red-500">
                        {variacionNomina.toFixed(1)}%
                      </span>
                    </>
                  )}
                  <span className="text-warm-400">vs periodo anterior</span>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Graficos */}
      <div className="grid gap-6 lg:grid-cols-2">
        {/* Grafico de lineas - Tendencia de nomina */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Tendencia de nomina</CardTitle>
          </CardHeader>
          <CardContent>
            {datosNomina.length === 0 ? (
              <div className="h-64 flex items-center justify-center text-warm-400">
                Sin datos de nomina disponibles
              </div>
            ) : (
              <ResponsiveContainer width="100%" height={280}>
                <LineChart data={datosNomina}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e5e5e5" />
                  <XAxis dataKey="periodo" tick={{ fontSize: 12 }} />
                  <YAxis
                    tickFormatter={(v) =>
                      `$${(v / 1000).toFixed(0)}k`
                    }
                    tick={{ fontSize: 12 }}
                  />
                  <Tooltip
                    formatter={(value) => formatCurrency(value as number)}
                    labelStyle={{ color: "#44403c" }}
                  />
                  <Legend />
                  <Line
                    type="monotone"
                    dataKey="neto"
                    name="Neto"
                    stroke={CHART_COLORS.primary}
                    strokeWidth={2}
                    dot={{ fill: CHART_COLORS.primary }}
                  />
                  <Line
                    type="monotone"
                    dataKey="percepciones"
                    name="Percepciones"
                    stroke={CHART_COLORS.secondary}
                    strokeWidth={2}
                    dot={{ fill: CHART_COLORS.secondary }}
                  />
                </LineChart>
              </ResponsiveContainer>
            )}
          </CardContent>
        </Card>

        {/* Pie chart - Empleados por departamento */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base">
              Empleados por departamento
            </CardTitle>
          </CardHeader>
          <CardContent>
            {datosDepartamentos.length === 0 ? (
              <div className="h-64 flex items-center justify-center text-warm-400">
                Sin datos de departamentos
              </div>
            ) : (
              <ResponsiveContainer width="100%" height={280}>
                <PieChart>
                  <Pie
                    data={datosDepartamentos}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={100}
                    paddingAngle={2}
                    dataKey="value"
                    label={({ name, percent }) =>
                      `${name}: ${((percent || 0) * 100).toFixed(0)}%`
                    }
                    labelLine={false}
                  >
                    {datosDepartamentos.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Costos proyectados y alertas */}
      <div className="grid gap-6 lg:grid-cols-2">
        {/* Costos proyectados */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Costos proyectados anuales</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex justify-between items-center pb-2 border-b border-warm-100">
                <span className="text-warm-600">Nomina anual (12 meses)</span>
                <span className="font-medium text-warm-900">
                  {formatCurrency(
                    (data.empleados?.nomina_mensual_estimada || 0) * 12
                  )}
                </span>
              </div>
              <div className="flex justify-between items-center pb-2 border-b border-warm-100">
                <span className="text-warm-600">Aguinaldo proyectado</span>
                <span className="font-medium text-warm-900">
                  {formatCurrency(data.costos_proyectados?.aguinaldo_proyectado)}
                </span>
              </div>
              <div className="flex justify-between items-center pb-2 border-b border-warm-100">
                <span className="text-warm-600">Prima vacacional</span>
                <span className="font-medium text-warm-900">
                  {formatCurrency(
                    data.costos_proyectados?.prima_vacacional_proyectada
                  )}
                </span>
              </div>
              <div className="flex justify-between items-center pb-2 border-b border-warm-100">
                <span className="text-warm-600">Pasivo por vacaciones</span>
                <span className="font-medium text-warm-900">
                  {formatCurrency(data.vacaciones?.pasivo_vacaciones)}
                </span>
              </div>
              <div className="flex justify-between items-center pt-2">
                <span className="font-semibold text-warm-900">
                  Costo total estimado
                </span>
                <span className="font-semibold text-sage-700 text-lg">
                  {formatCurrency(data.costos_proyectados?.costo_anual_estimado)}
                </span>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Alertas */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Alertas</CardTitle>
          </CardHeader>
          <CardContent>
            {(data.alertas?.length || 0) === 0 ? (
              <div className="text-center py-8 text-warm-400">
                <Calendar className="h-8 w-8 mx-auto mb-2 opacity-50" />
                <p>Sin alertas pendientes</p>
              </div>
            ) : (
              <div className="space-y-3 max-h-64 overflow-y-auto">
                {data.alertas?.slice(0, 5).map((alerta, idx) => (
                  <div
                    key={idx}
                    className={`p-3 rounded-lg border ${
                      alerta.nivel === "warning"
                        ? "bg-amber-50 border-amber-200"
                        : alerta.nivel === "error"
                        ? "bg-red-50 border-red-200"
                        : "bg-horizon-50 border-horizon-200"
                    }`}
                  >
                    <div className="flex items-start gap-2">
                      <AlertTriangle
                        className={`h-4 w-4 mt-0.5 ${
                          alerta.nivel === "warning"
                            ? "text-amber-500"
                            : alerta.nivel === "error"
                            ? "text-red-500"
                            : "text-horizon-500"
                        }`}
                      />
                      <div>
                        <p className="text-sm font-medium text-warm-900">
                          {alerta.empleado}
                        </p>
                        <p className="text-xs text-warm-600">{alerta.mensaje}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
