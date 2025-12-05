"use client";

import { useState, useEffect } from "react";
import { Calendar, Download, FileText, Plus, Receipt } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { formatCurrency } from "@/lib/utils";
import { useQuery } from "@tanstack/react-query";
import { useAuthStore } from "@/stores/auth-store";
import api from "@/lib/api";
import Link from "next/link";

interface PeriodoNomina {
  id: string;
  nombre?: string;
  periodo?: string;
  tipo_periodo?: string;
  tipo_periodo_display?: string;
  numero_periodo?: number;
  año?: number;
  fecha_inicio: string;
  fecha_fin: string;
  estado: string;
  estado_display?: string;
  total_empleados?: number;
  total_percepciones?: number;
  total_deducciones?: number;
  total_neto?: number;
}

const estadoBadgeVariant: Record<
  string,
  "default" | "primary" | "success" | "warning"
> = {
  borrador: "default",
  calculado: "warning",
  procesado: "primary",
  timbrado: "success",
  pagado: "success",
};

export default function NominaPage() {
  const { empresaActual } = useAuthStore();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  const { data, isLoading } = useQuery({
    queryKey: ["nomina-periodos", empresaActual?.id],
    queryFn: async () => {
      const response = await api.get("/nomina/periodos/");
      const rawData = response.data;
      return rawData.results || rawData;
    },
    enabled: mounted && !!empresaActual?.id,
  });

  const periodos: PeriodoNomina[] = data || [];
  const ultimoPeriodo = periodos[0];

  // Función para formatear fecha corta
  const formatFechaCorta = (fecha: string) => {
    if (!fecha) return "";
    try {
      return new Date(fecha).toLocaleDateString("es-MX", {
        day: "2-digit",
        month: "short",
      });
    } catch {
      return fecha;
    }
  };

  // Función para generar nombre del periodo
  const getNombrePeriodo = (periodo: PeriodoNomina) => {
    // Si tiene nombre y no es un UUID, usarlo
    if (periodo.nombre && !periodo.nombre.includes("-")) {
      return periodo.nombre;
    }
    // Si tiene tipo_periodo_display y numero_periodo, construir nombre
    if (periodo.tipo_periodo_display && periodo.numero_periodo) {
      return `${periodo.tipo_periodo_display} ${periodo.numero_periodo}${periodo.año ? ` - ${periodo.año}` : ""}`;
    }
    // Fallback a fechas formateadas
    const inicio = formatFechaCorta(periodo.fecha_inicio);
    const fin = formatFechaCorta(periodo.fecha_fin);
    if (inicio && fin) {
      return `${inicio} - ${fin}`;
    }
    return `Periodo #${periodo.numero_periodo || "?"}`;
  };

  if (!mounted) return null;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-display font-semibold text-warm-900">
            Nomina
          </h1>
          <p className="text-sm text-warm-500 mt-1">
            {periodos.length} periodo{periodos.length !== 1 ? "s" : ""} registrado
            {periodos.length !== 1 ? "s" : ""}
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline">
            <Download className="mr-2 h-4 w-4" strokeWidth={1.5} />
            Exportar
          </Button>
          <Link href="/nomina/nuevo">
            <Button>
              <Plus className="mr-2 h-4 w-4" strokeWidth={1.5} />
              Nuevo periodo
            </Button>
          </Link>
        </div>
      </div>

      {/* Loading state */}
      {isLoading && (
        <>
          <div className="grid gap-4 sm:grid-cols-3">
            {[1, 2, 3].map((i) => (
              <Card key={i}>
                <CardContent className="p-4">
                  <Skeleton className="h-4 w-24 mb-2" />
                  <Skeleton className="h-8 w-32" />
                </CardContent>
              </Card>
            ))}
          </div>
          <Card>
            <CardHeader>
              <Skeleton className="h-5 w-32" />
            </CardHeader>
            <CardContent className="space-y-4">
              {[1, 2, 3].map((i) => (
                <Skeleton key={i} className="h-16 w-full" />
              ))}
            </CardContent>
          </Card>
        </>
      )}

      {/* Empty state */}
      {!isLoading && periodos.length === 0 && (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <div className="w-12 h-12 rounded-full bg-horizon-100 flex items-center justify-center mb-4">
              <Receipt className="h-6 w-6 text-horizon-600" strokeWidth={1.5} />
            </div>
            <h3 className="text-lg font-semibold text-warm-900 mb-2">
              Sin periodos de nomina
            </h3>
            <p className="text-warm-500 mb-6 text-center max-w-sm">
              Crea tu primer periodo de nomina para comenzar a calcular pagos.
            </p>
            <Link href="/nomina/nuevo">
              <Button>
                <Plus className="mr-2 h-4 w-4" strokeWidth={1.5} />
                Crear periodo
              </Button>
            </Link>
          </CardContent>
        </Card>
      )}

      {/* Content when data exists */}
      {!isLoading && periodos.length > 0 && (
        <>
          {/* Summary cards */}
          <div className="grid gap-4 sm:grid-cols-3">
            <Card>
              <CardContent className="p-4">
                <p className="text-sm text-warm-500">Total percepciones</p>
                <p className="text-2xl font-semibold text-warm-900">
                  {formatCurrency(ultimoPeriodo?.total_percepciones || 0)}
                </p>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-4">
                <p className="text-sm text-warm-500">Total deducciones</p>
                <p className="text-2xl font-semibold text-warm-900">
                  {formatCurrency(ultimoPeriodo?.total_deducciones || 0)}
                </p>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-4">
                <p className="text-sm text-warm-500">Neto a pagar</p>
                <p className="text-2xl font-semibold text-sage-700">
                  {formatCurrency(ultimoPeriodo?.total_neto || 0)}
                </p>
              </CardContent>
            </Card>
          </div>

          {/* Periodos list */}
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Periodos recientes</CardTitle>
            </CardHeader>
            <CardContent className="p-0">
              <div className="divide-y divide-warm-100">
                {periodos.map((periodo) => (
                  <Link
                    key={periodo.id}
                    href={`/nomina/${periodo.id}`}
                    className="flex flex-col gap-3 p-4 transition-colors hover:bg-warm-50 sm:flex-row sm:items-center sm:justify-between"
                  >
                    <div className="flex items-start gap-3">
                      <div className="rounded-md bg-horizon-50 p-2 text-horizon-600">
                        <Calendar className="h-5 w-5" strokeWidth={1.5} />
                      </div>
                      <div>
                        <p className="font-medium text-warm-900">
                          {getNombrePeriodo(periodo)}
                        </p>
                        <p className="text-sm text-warm-500">
                          {formatFechaCorta(periodo.fecha_inicio)} - {formatFechaCorta(periodo.fecha_fin)}
                          {periodo.total_empleados ? ` • ${periodo.total_empleados} empleados` : ""}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-4">
                      <div className="text-right">
                        <p className="font-medium text-warm-900">
                          {formatCurrency(periodo.total_neto || 0)}
                        </p>
                        <p className="text-xs text-warm-500">Neto</p>
                      </div>
                      <Badge variant={estadoBadgeVariant[periodo.estado] || "default"}>
                        {periodo.estado_display ||
                          (periodo.estado
                            ? periodo.estado.charAt(0).toUpperCase() +
                              periodo.estado.slice(1)
                            : "Borrador")}
                      </Badge>
                    </div>
                  </Link>
                ))}
              </div>
            </CardContent>
          </Card>
        </>
      )}
    </div>
  );
}
