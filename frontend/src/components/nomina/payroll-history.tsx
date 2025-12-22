"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { nominaApi } from "@/lib/api";
import { PeriodoNomina } from "@/types";
import { formatCurrency } from "@/lib/utils";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Calendar,
  Users,
  DollarSign,
  TrendingUp,
  ChevronRight,
  Plus,
} from "lucide-react";

interface PayrollHistoryProps {
  onSelectPeriodo: (periodo: PeriodoNomina) => void;
  onNewPeriodo: () => void;
}

const estadoBadgeVariant: Record<
  string,
  "default" | "primary" | "success" | "warning"
> = {
  borrador: "default",
  calculado: "warning",
  autorizado: "primary",
  pagado: "success",
  timbrado: "success",
  cancelado: "default",
};

export function PayrollHistory({ onSelectPeriodo, onNewPeriodo }: PayrollHistoryProps) {
  const { data, isLoading } = useQuery({
    queryKey: ["nomina-periodos"],
    queryFn: async () => {
      const response = await nominaApi.getPeriodos();
      return response.results || response;
    },
  });

  const periodos: PeriodoNomina[] = data || [];
  const ultimoPeriodo = periodos[0];

  // KPIs
  const totalEmpleados = ultimoPeriodo?.total_empleados || 0;
  const totalNeto = ultimoPeriodo?.total_neto || 0;
  const periodosActivos = periodos.filter(
    (p) => p.estado !== "cancelado" && p.estado !== "pagado"
  ).length;

  const formatFecha = (fecha: string) => {
    if (!fecha) return "";
    return new Date(fecha).toLocaleDateString("es-MX", {
      day: "2-digit",
      month: "short",
    });
  };

  const getNombrePeriodo = (periodo: PeriodoNomina) => {
    if (periodo.tipo_periodo_display && periodo.numero_periodo) {
      return `${periodo.tipo_periodo_display} ${periodo.numero_periodo} - ${periodo.año}`;
    }
    return `Periodo #${periodo.numero_periodo || "?"}`;
  };

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
        <Card>
          <CardHeader>
            <Skeleton className="h-5 w-40" />
          </CardHeader>
          <CardContent className="space-y-4">
            {[1, 2, 3].map((i) => (
              <Skeleton key={i} className="h-16 w-full" />
            ))}
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* KPIs */}
      <div className="grid gap-4 sm:grid-cols-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-horizon-50">
                <Calendar className="h-5 w-5 text-horizon-600" strokeWidth={1.5} />
              </div>
              <div>
                <p className="text-sm text-warm-500">Periodos activos</p>
                <p className="text-2xl font-semibold text-warm-900">
                  {periodosActivos}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-sage-50">
                <Users className="h-5 w-5 text-sage-600" strokeWidth={1.5} />
              </div>
              <div>
                <p className="text-sm text-warm-500">Empleados</p>
                <p className="text-2xl font-semibold text-warm-900">
                  {totalEmpleados}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-amber-50">
                <DollarSign className="h-5 w-5 text-amber-600" strokeWidth={1.5} />
              </div>
              <div>
                <p className="text-sm text-warm-500">Ultimo neto</p>
                <p className="text-2xl font-semibold text-warm-900">
                  {formatCurrency(totalNeto)}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-horizon-50">
                <TrendingUp className="h-5 w-5 text-horizon-600" strokeWidth={1.5} />
              </div>
              <div>
                <p className="text-sm text-warm-500">Ultimo periodo</p>
                <p className="text-lg font-semibold text-warm-900 truncate">
                  {ultimoPeriodo ? getNombrePeriodo(ultimoPeriodo) : "Sin periodos"}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Historial de periodos */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle className="text-base">Historial de periodos</CardTitle>
          <Button size="sm" onClick={onNewPeriodo}>
            <Plus className="h-4 w-4 mr-1" strokeWidth={1.5} />
            Nuevo periodo
          </Button>
        </CardHeader>
        <CardContent className="p-0">
          {periodos.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12">
              <div className="w-12 h-12 rounded-full bg-horizon-100 flex items-center justify-center mb-4">
                <Calendar className="h-6 w-6 text-horizon-600" strokeWidth={1.5} />
              </div>
              <h3 className="text-lg font-semibold text-warm-900 mb-2">
                Sin periodos
              </h3>
              <p className="text-warm-500 mb-6 text-center max-w-sm">
                Crea tu primer periodo de nomina para comenzar.
              </p>
              <Button onClick={onNewPeriodo}>
                <Plus className="mr-2 h-4 w-4" strokeWidth={1.5} />
                Crear periodo
              </Button>
            </div>
          ) : (
            <div className="divide-y divide-warm-100">
              {periodos.map((periodo) => (
                <button
                  key={periodo.id}
                  onClick={() => onSelectPeriodo(periodo)}
                  className="w-full flex flex-col gap-3 p-4 transition-colors hover:bg-warm-50 sm:flex-row sm:items-center sm:justify-between text-left"
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
                        {formatFecha(periodo.fecha_inicio)} -{" "}
                        {formatFecha(periodo.fecha_fin)}
                        {periodo.total_empleados
                          ? ` • ${periodo.total_empleados} empleados`
                          : ""}
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
                    <Badge
                      variant={estadoBadgeVariant[periodo.estado] || "default"}
                    >
                      {periodo.estado_display ||
                        periodo.estado.charAt(0).toUpperCase() +
                          periodo.estado.slice(1)}
                    </Badge>
                    <ChevronRight className="h-5 w-5 text-warm-400" />
                  </div>
                </button>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
