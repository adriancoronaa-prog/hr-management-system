"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { BarChart3, Construction, FileText, Users, Calendar } from "lucide-react";

export default function ReportesPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-display font-semibold text-warm-900">
          Reportes
        </h1>
        <p className="text-warm-500 mt-1">
          Analisis y reportes del sistema
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base">
            <Construction className="h-5 w-5 text-amber-500" />
            En Construccion
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-warm-500">
            El modulo de reportes esta en desarrollo. Proximamente podras generar:
          </p>
          <ul className="mt-4 space-y-3">
            <li className="flex items-center gap-3 text-sm text-warm-600">
              <div className="rounded-md bg-horizon-50 p-2">
                <FileText className="h-4 w-4 text-horizon-600" />
              </div>
              Reporte de nomina por periodo
            </li>
            <li className="flex items-center gap-3 text-sm text-warm-600">
              <div className="rounded-md bg-horizon-50 p-2">
                <Calendar className="h-4 w-4 text-horizon-600" />
              </div>
              Analisis de vacaciones y ausencias
            </li>
            <li className="flex items-center gap-3 text-sm text-warm-600">
              <div className="rounded-md bg-horizon-50 p-2">
                <BarChart3 className="h-4 w-4 text-horizon-600" />
              </div>
              Dashboard ejecutivo por empresa
            </li>
            <li className="flex items-center gap-3 text-sm text-warm-600">
              <div className="rounded-md bg-horizon-50 p-2">
                <Users className="h-4 w-4 text-horizon-600" />
              </div>
              Reporte de plantilla y rotacion
            </li>
          </ul>
        </CardContent>
      </Card>
    </div>
  );
}
