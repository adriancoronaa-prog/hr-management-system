"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { useAuthStore } from "@/stores/auth-store";
import { nominaApi } from "@/lib/api";
import { PeriodoNomina, ReciboNomina, ResumenNomina } from "@/types";
import {
  formatCurrency,
  exportToExcel,
  exportTableToPdf,
} from "@/lib/export-utils";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";
import { toast } from "sonner";
import {
  DollarSign,
  Download,
  FileSpreadsheet,
  FileText,
  Search,
  Users,
  Receipt,
} from "lucide-react";

export function PayrollReport() {
  const { empresaActual } = useAuthStore();
  const [selectedPeriodoId, setSelectedPeriodoId] = useState<string>("");
  const [searchTerm, setSearchTerm] = useState("");

  // Lista de periodos
  const { data: periodosData, isLoading: loadingPeriodos } = useQuery({
    queryKey: ["nomina-periodos-reporte", empresaActual?.id],
    queryFn: async () => {
      const response = await nominaApi.getPeriodos();
      return response.results || response;
    },
    enabled: !!empresaActual?.id,
  });

  const periodos = (periodosData as PeriodoNomina[]) || [];

  // Resumen del periodo seleccionado
  const { data: resumenData, isLoading: loadingResumen } = useQuery({
    queryKey: ["resumen-periodo", selectedPeriodoId],
    queryFn: () => nominaApi.getResumenPeriodo(selectedPeriodoId),
    enabled: !!selectedPeriodoId,
  });

  // Recibos del periodo
  const { data: recibosData, isLoading: loadingRecibos } = useQuery({
    queryKey: ["recibos-periodo", selectedPeriodoId],
    queryFn: async () => {
      const response = await nominaApi.getRecibos({ periodo: selectedPeriodoId });
      return response.results || response;
    },
    enabled: !!selectedPeriodoId,
  });

  const resumen = resumenData as ResumenNomina | undefined;
  const recibos = (recibosData as ReciboNomina[]) || [];

  // Filtrar recibos por busqueda
  const recibosFiltrados = recibos.filter(
    (r) =>
      !searchTerm ||
      r.empleado_nombre?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  // Agrupar por departamento (simulado desde recibos)
  const porDepartamento = recibosFiltrados.reduce((acc, recibo) => {
    const depto = recibo.empleado_puesto || "Sin departamento";
    if (!acc[depto]) {
      acc[depto] = { empleados: 0, percepciones: 0, deducciones: 0, neto: 0 };
    }
    acc[depto].empleados += 1;
    acc[depto].percepciones += recibo.total_percepciones || 0;
    acc[depto].deducciones += recibo.total_deducciones || 0;
    acc[depto].neto += recibo.neto_a_pagar || 0;
    return acc;
  }, {} as Record<string, { empleados: number; percepciones: number; deducciones: number; neto: number }>);

  const periodoSeleccionado = periodos.find((p) => p.id === selectedPeriodoId);

  const getNombrePeriodo = (periodo: PeriodoNomina) => {
    if (periodo.tipo_periodo_display && periodo.numero_periodo) {
      return `${periodo.tipo_periodo_display} ${periodo.numero_periodo} - ${periodo.año}`;
    }
    return `Periodo #${periodo.numero_periodo}`;
  };

  // Totales
  const totalPercepciones = recibosFiltrados.reduce(
    (sum, r) => sum + (r.total_percepciones || 0),
    0
  );
  const totalDeducciones = recibosFiltrados.reduce(
    (sum, r) => sum + (r.total_deducciones || 0),
    0
  );
  const totalISR = recibosFiltrados.reduce(
    (sum, r) => sum + (r.isr_retenido || 0),
    0
  );
  const totalNeto = recibosFiltrados.reduce(
    (sum, r) => sum + (r.neto_a_pagar || 0),
    0
  );

  const handleExportExcel = () => {
    if (recibosFiltrados.length === 0) {
      toast.error("No hay datos para exportar");
      return;
    }

    const data = recibosFiltrados.map((r) => ({
      Empleado: r.empleado_nombre || "",
      Puesto: r.empleado_puesto || "",
      "Salario Base": r.salario_diario || 0,
      "Dias Trabajados": r.dias_trabajados || 0,
      Percepciones: r.total_percepciones || 0,
      ISR: r.isr_retenido || 0,
      IMSS: r.cuota_imss_obrera || 0,
      Deducciones: r.total_deducciones || 0,
      Neto: r.neto_a_pagar || 0,
    }));

    const filename = periodoSeleccionado
      ? `nomina_${getNombrePeriodo(periodoSeleccionado).replace(/\s/g, "_")}`
      : "nomina_reporte";

    exportToExcel(data, filename, "Nomina");
    toast.success("Archivo Excel generado");
  };

  const handleExportPdf = () => {
    if (recibosFiltrados.length === 0) {
      toast.error("No hay datos para exportar");
      return;
    }

    const columns = [
      "Empleado",
      "Percepciones",
      "ISR",
      "IMSS",
      "Deducciones",
      "Neto",
    ];
    const rows = recibosFiltrados.map((r) => [
      r.empleado_nombre || "",
      formatCurrency(r.total_percepciones),
      formatCurrency(r.isr_retenido),
      formatCurrency(r.cuota_imss_obrera),
      formatCurrency(r.total_deducciones),
      formatCurrency(r.neto_a_pagar),
    ]);

    const title = periodoSeleccionado
      ? `Reporte de Nomina - ${getNombrePeriodo(periodoSeleccionado)}`
      : "Reporte de Nomina";

    const filename = periodoSeleccionado
      ? `nomina_${getNombrePeriodo(periodoSeleccionado).replace(/\s/g, "_")}`
      : "nomina_reporte";

    exportTableToPdf(columns, rows, title, filename);
    toast.success("Archivo PDF generado");
  };

  if (loadingPeriodos) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-10 w-64" />
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
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Selector de periodo y botones de exportacion */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-center gap-4">
          <label className="text-sm font-medium text-warm-700">Periodo:</label>
          <select
            className="rounded-md border border-warm-300 p-2 text-sm min-w-[200px]"
            value={selectedPeriodoId}
            onChange={(e) => setSelectedPeriodoId(e.target.value)}
          >
            <option value="">Seleccionar periodo</option>
            {periodos.map((p) => (
              <option key={p.id} value={p.id}>
                {getNombrePeriodo(p)}
              </option>
            ))}
          </select>
        </div>

        {selectedPeriodoId && (
          <div className="flex gap-2">
            <Button variant="outline" onClick={handleExportExcel}>
              <FileSpreadsheet className="h-4 w-4 mr-2" />
              Excel
            </Button>
            <Button variant="outline" onClick={handleExportPdf}>
              <FileText className="h-4 w-4 mr-2" />
              PDF
            </Button>
          </div>
        )}
      </div>

      {!selectedPeriodoId ? (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <Receipt className="h-12 w-12 text-warm-300 mb-4" />
            <h3 className="text-lg font-semibold text-warm-900 mb-2">
              Selecciona un periodo
            </h3>
            <p className="text-warm-500 text-center max-w-sm">
              Elige un periodo de nomina para ver el reporte detallado.
            </p>
          </CardContent>
        </Card>
      ) : loadingResumen || loadingRecibos ? (
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
          <Card>
            <CardContent className="p-4">
              <Skeleton className="h-64 w-full" />
            </CardContent>
          </Card>
        </div>
      ) : (
        <>
          {/* KPIs del periodo */}
          <div className="grid gap-4 sm:grid-cols-4">
            <Card>
              <CardContent className="p-4">
                <div className="flex items-center gap-3">
                  <div className="p-2 rounded-lg bg-sage-50">
                    <DollarSign className="h-5 w-5 text-sage-600" />
                  </div>
                  <div>
                    <p className="text-sm text-warm-500">Percepciones</p>
                    <p className="text-xl font-semibold text-warm-900">
                      {formatCurrency(totalPercepciones)}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-4">
                <div className="flex items-center gap-3">
                  <div className="p-2 rounded-lg bg-amber-50">
                    <DollarSign className="h-5 w-5 text-amber-600" />
                  </div>
                  <div>
                    <p className="text-sm text-warm-500">Deducciones</p>
                    <p className="text-xl font-semibold text-warm-900">
                      {formatCurrency(totalDeducciones)}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-4">
                <div className="flex items-center gap-3">
                  <div className="p-2 rounded-lg bg-red-50">
                    <FileText className="h-5 w-5 text-red-600" />
                  </div>
                  <div>
                    <p className="text-sm text-warm-500">ISR</p>
                    <p className="text-xl font-semibold text-warm-900">
                      {formatCurrency(totalISR)}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-4">
                <div className="flex items-center gap-3">
                  <div className="p-2 rounded-lg bg-horizon-50">
                    <Users className="h-5 w-5 text-horizon-600" />
                  </div>
                  <div>
                    <p className="text-sm text-warm-500">Neto total</p>
                    <p className="text-xl font-semibold text-sage-700">
                      {formatCurrency(totalNeto)}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Tabla por departamento */}
          {Object.keys(porDepartamento).length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="text-base">Por departamento/puesto</CardTitle>
              </CardHeader>
              <CardContent className="p-0">
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead className="bg-warm-50 border-b border-warm-200">
                      <tr>
                        <th className="text-left p-3 font-medium text-warm-700">
                          Departamento
                        </th>
                        <th className="text-right p-3 font-medium text-warm-700">
                          Empleados
                        </th>
                        <th className="text-right p-3 font-medium text-warm-700">
                          Percepciones
                        </th>
                        <th className="text-right p-3 font-medium text-warm-700">
                          Deducciones
                        </th>
                        <th className="text-right p-3 font-medium text-warm-700">
                          Neto
                        </th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-warm-100">
                      {Object.entries(porDepartamento).map(([depto, datos]) => (
                        <tr key={depto}>
                          <td className="p-3 text-warm-900">{depto}</td>
                          <td className="p-3 text-right text-warm-600">
                            {datos.empleados}
                          </td>
                          <td className="p-3 text-right text-warm-600">
                            {formatCurrency(datos.percepciones)}
                          </td>
                          <td className="p-3 text-right text-warm-600">
                            {formatCurrency(datos.deducciones)}
                          </td>
                          <td className="p-3 text-right font-medium text-warm-900">
                            {formatCurrency(datos.neto)}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Tabla detallada por empleado */}
          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle className="text-base">Detalle por empleado</CardTitle>
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
                        Salario base
                      </th>
                      <th className="text-right p-3 font-medium text-warm-700">
                        Percepciones
                      </th>
                      <th className="text-right p-3 font-medium text-warm-700">
                        ISR
                      </th>
                      <th className="text-right p-3 font-medium text-warm-700">
                        IMSS
                      </th>
                      <th className="text-right p-3 font-medium text-warm-700">
                        Neto
                      </th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-warm-100">
                    {recibosFiltrados.map((recibo) => (
                      <tr key={recibo.id}>
                        <td className="p-3">
                          <p className="text-warm-900 font-medium">
                            {recibo.empleado_nombre}
                          </p>
                          <p className="text-xs text-warm-500">
                            {recibo.empleado_puesto}
                          </p>
                        </td>
                        <td className="p-3 text-right text-warm-600">
                          {formatCurrency(recibo.salario_diario)}
                        </td>
                        <td className="p-3 text-right text-warm-600">
                          {formatCurrency(recibo.total_percepciones)}
                        </td>
                        <td className="p-3 text-right text-warm-600">
                          {formatCurrency(recibo.isr_retenido)}
                        </td>
                        <td className="p-3 text-right text-warm-600">
                          {formatCurrency(recibo.cuota_imss_obrera)}
                        </td>
                        <td className="p-3 text-right font-medium text-sage-700">
                          {formatCurrency(recibo.neto_a_pagar)}
                        </td>
                      </tr>
                    ))}
                    {recibosFiltrados.length === 0 && (
                      <tr>
                        <td
                          colSpan={6}
                          className="p-8 text-center text-warm-400"
                        >
                          {searchTerm
                            ? "No se encontraron empleados"
                            : "Sin recibos en este periodo"}
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        </>
      )}
    </div>
  );
}
