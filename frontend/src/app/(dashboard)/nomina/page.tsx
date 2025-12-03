"use client";

import * as React from "react";
import { Calendar, Download, FileText } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { formatCurrency } from "@/lib/utils";

// Mock data
const periodos = [
  {
    id: "1",
    periodo: "1ra Quincena Diciembre 2024",
    fecha_inicio: "2024-12-01",
    fecha_fin: "2024-12-15",
    estado: "procesado",
    total_empleados: 22,
    total_percepciones: 285000,
    total_deducciones: 45000,
    total_neto: 240000,
  },
  {
    id: "2",
    periodo: "2da Quincena Noviembre 2024",
    fecha_inicio: "2024-11-16",
    fecha_fin: "2024-11-30",
    estado: "timbrado",
    total_empleados: 22,
    total_percepciones: 282500,
    total_deducciones: 44200,
    total_neto: 238300,
  },
  {
    id: "3",
    periodo: "1ra Quincena Noviembre 2024",
    fecha_inicio: "2024-11-01",
    fecha_fin: "2024-11-15",
    estado: "timbrado",
    total_empleados: 21,
    total_percepciones: 275000,
    total_deducciones: 43500,
    total_neto: 231500,
  },
];

const estadoBadgeVariant: Record<string, "default" | "primary" | "success" | "warning"> = {
  borrador: "default",
  procesado: "primary",
  timbrado: "success",
  pagado: "success",
};

export default function NominaPage() {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="text-xl font-semibold text-warm-900">Nomina</h2>
          <p className="text-sm text-warm-500">Periodos de nomina</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline">
            <Download className="mr-2 h-4 w-4" strokeWidth={1.5} />
            Exportar
          </Button>
          <Button>
            <FileText className="mr-2 h-4 w-4" strokeWidth={1.5} />
            Nuevo periodo
          </Button>
        </div>
      </div>

      {/* Summary cards */}
      <div className="grid gap-4 sm:grid-cols-3">
        <Card>
          <CardContent className="p-4">
            <p className="text-sm text-warm-500">Total percepciones</p>
            <p className="text-2xl font-semibold text-warm-900">
              {formatCurrency(periodos[0].total_percepciones)}
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <p className="text-sm text-warm-500">Total deducciones</p>
            <p className="text-2xl font-semibold text-warm-900">
              {formatCurrency(periodos[0].total_deducciones)}
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <p className="text-sm text-warm-500">Neto a pagar</p>
            <p className="text-2xl font-semibold text-sage-700">
              {formatCurrency(periodos[0].total_neto)}
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
              <div
                key={periodo.id}
                className="flex flex-col gap-3 p-4 transition-colors hover:bg-warm-50 sm:flex-row sm:items-center sm:justify-between"
              >
                <div className="flex items-start gap-3">
                  <div className="rounded-md bg-horizon-50 p-2 text-horizon-600">
                    <Calendar className="h-5 w-5" strokeWidth={1.5} />
                  </div>
                  <div>
                    <p className="font-medium text-warm-900">
                      {periodo.periodo}
                    </p>
                    <p className="text-sm text-warm-500">
                      {periodo.total_empleados} empleados
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-4">
                  <div className="text-right">
                    <p className="font-medium text-warm-900">
                      {formatCurrency(periodo.total_neto)}
                    </p>
                    <p className="text-xs text-warm-500">Neto</p>
                  </div>
                  <Badge variant={estadoBadgeVariant[periodo.estado]}>
                    {periodo.estado.charAt(0).toUpperCase() +
                      periodo.estado.slice(1)}
                  </Badge>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
