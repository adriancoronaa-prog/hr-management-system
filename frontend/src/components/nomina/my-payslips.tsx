"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { nominaApi } from "@/lib/api";
import { ReciboNomina } from "@/types";
import { formatCurrency } from "@/lib/utils";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { toast } from "sonner";
import {
  Receipt,
  Download,
  Eye,
  Calendar,
  DollarSign,
  TrendingUp,
  FileText,
  Loader2,
} from "lucide-react";

export function MyPayslips() {
  const [selectedRecibo, setSelectedRecibo] = useState<ReciboNomina | null>(null);
  const [downloading, setDownloading] = useState<string | null>(null);

  const { data, isLoading } = useQuery({
    queryKey: ["mis-recibos"],
    queryFn: async () => {
      const response = await nominaApi.getMisRecibos();
      return response.results || response;
    },
  });

  const recibos: ReciboNomina[] = data || [];
  const ultimoRecibo = recibos[0];

  // Calcular totales del año actual
  const añoActual = new Date().getFullYear();
  const recibosAño = recibos.filter((r) => {
    const fecha = new Date(r.created_at || "");
    return fecha.getFullYear() === añoActual;
  });
  const totalPercepcionesAño = recibosAño.reduce(
    (sum, r) => sum + (r.total_percepciones || 0),
    0
  );
  const totalDeduccionesAño = recibosAño.reduce(
    (sum, r) => sum + (r.total_deducciones || 0),
    0
  );

  const formatFecha = (fecha: string) => {
    if (!fecha) return "";
    return new Date(fecha).toLocaleDateString("es-MX", {
      day: "2-digit",
      month: "short",
      year: "numeric",
    });
  };

  const formatFechaCorta = (fecha: string) => {
    if (!fecha) return "";
    return new Date(fecha).toLocaleDateString("es-MX", {
      day: "2-digit",
      month: "short",
    });
  };

  const getNombrePeriodo = (recibo: ReciboNomina) => {
    if (recibo.periodo_info) {
      return `${recibo.periodo_info.tipo_periodo_display} ${recibo.periodo_info.numero_periodo} - ${recibo.periodo_info.año}`;
    }
    return "Periodo";
  };

  const handleDownload = async (recibo: ReciboNomina) => {
    setDownloading(recibo.id);
    try {
      const blob = await nominaApi.getReciboPdf(recibo.id);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `recibo_${recibo.id}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      toast.success("Recibo descargado");
    } catch {
      toast.error("Error al descargar el recibo");
    } finally {
      setDownloading(null);
    }
  };

  if (isLoading) {
    return (
      <div className="space-y-6">
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
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* KPIs */}
      <div className="grid gap-4 sm:grid-cols-3">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-sage-50">
                <DollarSign className="h-5 w-5 text-sage-600" strokeWidth={1.5} />
              </div>
              <div>
                <p className="text-sm text-warm-500">Ultimo neto</p>
                <p className="text-2xl font-semibold text-sage-700">
                  {formatCurrency(ultimoRecibo?.neto_a_pagar || 0)}
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
                <p className="text-sm text-warm-500">Percepciones {añoActual}</p>
                <p className="text-2xl font-semibold text-warm-900">
                  {formatCurrency(totalPercepcionesAño)}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-amber-50">
                <FileText className="h-5 w-5 text-amber-600" strokeWidth={1.5} />
              </div>
              <div>
                <p className="text-sm text-warm-500">Deducciones {añoActual}</p>
                <p className="text-2xl font-semibold text-warm-900">
                  {formatCurrency(totalDeduccionesAño)}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Lista de recibos */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Mis recibos de nomina</CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          {recibos.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12">
              <div className="w-12 h-12 rounded-full bg-horizon-100 flex items-center justify-center mb-4">
                <Receipt className="h-6 w-6 text-horizon-600" strokeWidth={1.5} />
              </div>
              <h3 className="text-lg font-semibold text-warm-900 mb-2">
                Sin recibos
              </h3>
              <p className="text-warm-500 text-center max-w-sm">
                Aun no tienes recibos de nomina disponibles.
              </p>
            </div>
          ) : (
            <div className="divide-y divide-warm-100">
              {recibos.map((recibo) => (
                <div
                  key={recibo.id}
                  className="flex flex-col gap-3 p-4 sm:flex-row sm:items-center sm:justify-between"
                >
                  <div className="flex items-start gap-3">
                    <div className="rounded-md bg-horizon-50 p-2 text-horizon-600">
                      <Calendar className="h-5 w-5" strokeWidth={1.5} />
                    </div>
                    <div>
                      <p className="font-medium text-warm-900">
                        {getNombrePeriodo(recibo)}
                      </p>
                      <p className="text-sm text-warm-500">
                        {recibo.periodo_info
                          ? `${formatFechaCorta(recibo.periodo_info.fecha_inicio)} - ${formatFechaCorta(recibo.periodo_info.fecha_fin)}`
                          : formatFecha(recibo.created_at || "")}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-4">
                    <div className="text-right">
                      <p className="font-semibold text-sage-700">
                        {formatCurrency(recibo.neto_a_pagar)}
                      </p>
                      <p className="text-xs text-warm-500">Neto</p>
                    </div>
                    <Badge
                      variant={
                        recibo.estado === "timbrado" ? "success" : "default"
                      }
                    >
                      {recibo.estado_display ||
                        recibo.estado.charAt(0).toUpperCase() +
                          recibo.estado.slice(1)}
                    </Badge>
                    <div className="flex gap-1">
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => setSelectedRecibo(recibo)}
                      >
                        <Eye className="h-4 w-4" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => handleDownload(recibo)}
                        disabled={downloading === recibo.id}
                      >
                        {downloading === recibo.id ? (
                          <Loader2 className="h-4 w-4 animate-spin" />
                        ) : (
                          <Download className="h-4 w-4" />
                        )}
                      </Button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Dialog de detalle */}
      <Dialog open={!!selectedRecibo} onOpenChange={() => setSelectedRecibo(null)}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>Detalle del recibo</DialogTitle>
          </DialogHeader>
          {selectedRecibo && (
            <div className="space-y-4">
              <div className="p-4 rounded-lg bg-warm-50">
                <p className="text-sm text-warm-500 mb-1">Periodo</p>
                <p className="font-medium text-warm-900">
                  {getNombrePeriodo(selectedRecibo)}
                </p>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-warm-500">Salario diario</p>
                  <p className="font-medium text-warm-900">
                    {formatCurrency(selectedRecibo.salario_diario)}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-warm-500">Dias trabajados</p>
                  <p className="font-medium text-warm-900">
                    {selectedRecibo.dias_trabajados}
                  </p>
                </div>
              </div>

              <div className="border-t border-warm-200 pt-4 space-y-2">
                <div className="flex justify-between">
                  <span className="text-warm-600">Percepciones</span>
                  <span className="font-medium text-warm-900">
                    {formatCurrency(selectedRecibo.total_percepciones)}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-warm-600">ISR</span>
                  <span className="text-warm-900">
                    -{formatCurrency(selectedRecibo.isr_retenido || 0)}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-warm-600">IMSS</span>
                  <span className="text-warm-900">
                    -{formatCurrency(selectedRecibo.cuota_imss_obrera || 0)}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-warm-600">Total deducciones</span>
                  <span className="text-warm-900">
                    -{formatCurrency(selectedRecibo.total_deducciones)}
                  </span>
                </div>
              </div>

              <div className="border-t border-warm-200 pt-4">
                <div className="flex justify-between items-center">
                  <span className="font-medium text-warm-900">Neto a pagar</span>
                  <span className="text-xl font-semibold text-sage-700">
                    {formatCurrency(selectedRecibo.neto_a_pagar)}
                  </span>
                </div>
              </div>

              {selectedRecibo.uuid_fiscal && (
                <div className="p-3 rounded-lg bg-sage-50 text-sm">
                  <p className="text-sage-600">UUID Fiscal:</p>
                  <p className="font-mono text-sage-800 break-all">
                    {selectedRecibo.uuid_fiscal}
                  </p>
                </div>
              )}

              <Button
                className="w-full"
                onClick={() => handleDownload(selectedRecibo)}
                disabled={downloading === selectedRecibo.id}
              >
                {downloading === selectedRecibo.id ? (
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                ) : (
                  <Download className="h-4 w-4 mr-2" />
                )}
                Descargar PDF
              </Button>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}
