"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import api from "@/lib/api";
import { useAuthStore } from "@/stores/auth-store";
import { formatDate } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import type { SolicitudVacaciones, ResumenVacaciones } from "@/types";
import {
  Palmtree,
  Calendar,
  User,
  Clock,
  Plus,
  CheckCircle,
  XCircle,
  Loader2,
  AlertCircle,
} from "lucide-react";

// Tabla LFT 2023 para mostrar días según antigüedad
function getDiasLFT(anios: number): number {
  if (anios < 1) return 0;
  if (anios === 1) return 12;
  if (anios === 2) return 14;
  if (anios === 3) return 16;
  if (anios === 4) return 18;
  if (anios === 5) return 20;
  if (anios <= 10) return 22;
  if (anios <= 15) return 24;
  if (anios <= 20) return 26;
  if (anios <= 25) return 28;
  if (anios <= 30) return 30;
  return 32;
}

export function EmployeeView() {
  const { user, empresaActual } = useAuthStore();
  const queryClient = useQueryClient();
  const [showSolicitarDialog, setShowSolicitarDialog] = useState(false);
  const [fechaInicio, setFechaInicio] = useState("");
  const [fechaFin, setFechaFin] = useState("");
  const [comentarios, setComentarios] = useState("");

  // Query para resumen del usuario actual
  const { data: miResumen, isLoading: loadingResumen } = useQuery<ResumenVacaciones>({
    queryKey: ["vacaciones-resumen", user?.id],
    queryFn: async () => {
      const response = await api.get("/vacaciones/solicitudes/resumen/");
      return response.data;
    },
    enabled: !!user,
  });

  // Query para mis solicitudes
  const { data: misSolicitudes, isLoading: loadingSolicitudes } = useQuery<SolicitudVacaciones[]>({
    queryKey: ["mis-vacaciones", user?.id],
    queryFn: async () => {
      const response = await api.get("/vacaciones/solicitudes/");
      const data = response.data;
      return Array.isArray(data) ? data : data?.results || [];
    },
    enabled: !!user && !!empresaActual?.id,
  });

  // Mutation para crear solicitud
  const crearSolicitudMutation = useMutation({
    mutationFn: async (data: { fecha_inicio: string; fecha_fin: string; comentarios?: string }) => {
      const response = await api.post("/vacaciones/solicitudes/", data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["mis-vacaciones"] });
      queryClient.invalidateQueries({ queryKey: ["vacaciones-resumen"] });
      setShowSolicitarDialog(false);
      setFechaInicio("");
      setFechaFin("");
      setComentarios("");
      toast.success("Solicitud enviada", {
        description: "Tu solicitud de vacaciones ha sido registrada correctamente.",
      });
    },
    onError: (error: any) => {
      toast.error("Error al enviar solicitud", {
        description: error.response?.data?.detail || "Intenta de nuevo más tarde.",
      });
    },
  });

  // Mutation para cancelar solicitud
  const cancelarMutation = useMutation({
    mutationFn: async (id: string) => {
      const response = await api.post(`/vacaciones/solicitudes/${id}/cancelar/`);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["mis-vacaciones"] });
      queryClient.invalidateQueries({ queryKey: ["vacaciones-resumen"] });
      toast.success("Solicitud cancelada");
    },
    onError: () => {
      toast.error("Error al cancelar solicitud");
    },
  });

  // Calcular días solicitados
  const calcularDias = () => {
    if (!fechaInicio || !fechaFin) return 0;
    const inicio = new Date(fechaInicio);
    const fin = new Date(fechaFin);
    if (fin < inicio) return 0;
    const diffTime = Math.abs(fin.getTime() - inicio.getTime());
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24)) + 1;
    return diffDays;
  };

  // Validaciones
  const hoy = new Date().toISOString().split("T")[0];
  const diasCalculados = calcularDias();
  const puedeEnviar = fechaInicio && fechaFin && fechaInicio >= hoy && fechaFin >= fechaInicio && diasCalculados > 0;

  const getEstadoBadge = (estado: string) => {
    const badges: Record<string, { bg: string; text: string; icon: typeof Clock }> = {
      pendiente: { bg: "bg-amber-100", text: "text-amber-700", icon: Clock },
      aprobada: { bg: "bg-green-100", text: "text-green-700", icon: CheckCircle },
      rechazada: { bg: "bg-red-100", text: "text-red-700", icon: XCircle },
      cancelada: { bg: "bg-warm-100", text: "text-warm-600", icon: XCircle },
    };
    return badges[estado] || badges.pendiente;
  };

  const solicitudesList = misSolicitudes || [];
  const diasLFT = miResumen ? getDiasLFT(miResumen.antiguedad_anios) : 0;

  return (
    <div className="space-y-6">
      {/* Métricas */}
      {loadingResumen ? (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {[1, 2, 3, 4].map((i) => (
            <Card key={i}>
              <CardContent className="p-5">
                <div className="animate-pulse space-y-3">
                  <div className="h-4 w-24 bg-warm-200 rounded" />
                  <div className="h-8 w-16 bg-warm-200 rounded" />
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : miResumen ? (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {/* Días disponibles */}
          <Card className="border-green-200 bg-gradient-to-br from-green-50 to-white">
            <CardContent className="p-5">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-green-700">Días disponibles</p>
                  <p className="text-3xl font-bold text-green-600 mt-1">
                    {miResumen.total_disponible}
                  </p>
                  <p className="text-xs text-green-600/70 mt-1">
                    {miResumen.dias_correspondientes_anio_actual} este periodo
                  </p>
                </div>
                <div className="w-12 h-12 bg-green-100 rounded-xl flex items-center justify-center">
                  <Palmtree className="w-6 h-6 text-green-600" />
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Días tomados */}
          <Card>
            <CardContent className="p-5">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-warm-500">Días tomados</p>
                  <p className="text-3xl font-bold text-warm-900 mt-1">
                    {miResumen.dias_tomados_anio_actual}
                  </p>
                  <p className="text-xs text-warm-400 mt-1">este año</p>
                </div>
                <div className="w-12 h-12 bg-horizon-100 rounded-xl flex items-center justify-center">
                  <Calendar className="w-6 h-6 text-horizon-600" />
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Antigüedad */}
          <Card>
            <CardContent className="p-5">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-warm-500">Antigüedad</p>
                  <p className="text-3xl font-bold text-warm-900 mt-1">
                    {miResumen.antiguedad_anios}
                  </p>
                  <p className="text-xs text-warm-400 mt-1">
                    año{miResumen.antiguedad_anios !== 1 ? "s" : ""} ({diasLFT} días/año)
                  </p>
                </div>
                <div className="w-12 h-12 bg-warm-100 rounded-xl flex items-center justify-center">
                  <User className="w-6 h-6 text-warm-600" />
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Pendientes años anteriores */}
          <Card className={miResumen.dias_pendientes_anteriores > 0 ? "border-amber-200" : ""}>
            <CardContent className="p-5">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-warm-500">Pendientes anteriores</p>
                  <p className={`text-3xl font-bold mt-1 ${miResumen.dias_pendientes_anteriores > 0 ? "text-amber-600" : "text-warm-900"}`}>
                    {miResumen.dias_pendientes_anteriores}
                  </p>
                  <p className="text-xs text-warm-400 mt-1">días acumulados</p>
                </div>
                <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${miResumen.dias_pendientes_anteriores > 0 ? "bg-amber-100" : "bg-warm-100"}`}>
                  <Clock className={`w-6 h-6 ${miResumen.dias_pendientes_anteriores > 0 ? "text-amber-600" : "text-warm-600"}`} />
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      ) : null}

      {/* Botón solicitar */}
      <div className="flex justify-center">
        <Button
          size="lg"
          onClick={() => setShowSolicitarDialog(true)}
          className="bg-horizon-600 hover:bg-horizon-700 gap-2"
        >
          <Palmtree className="w-5 h-5" />
          Solicitar Vacaciones
        </Button>
      </div>

      {/* Mis solicitudes */}
      <div>
        <h2 className="text-lg font-semibold text-warm-900 mb-4">Mis Solicitudes</h2>

        {loadingSolicitudes ? (
          <div className="flex justify-center py-8">
            <Loader2 className="w-6 h-6 animate-spin text-horizon-500" />
          </div>
        ) : solicitudesList.length === 0 ? (
          <Card>
            <CardContent className="py-12 text-center">
              <Palmtree className="w-12 h-12 text-warm-300 mx-auto mb-3" />
              <p className="text-warm-500">No tienes solicitudes de vacaciones</p>
              <p className="text-sm text-warm-400 mt-1">
                Solicita tus primeras vacaciones usando el botón de arriba
              </p>
            </CardContent>
          </Card>
        ) : (
          <div className="space-y-3">
            {solicitudesList.map((solicitud) => {
              const badge = getEstadoBadge(solicitud.estado);
              const BadgeIcon = badge.icon;
              const puedeCancel = solicitud.estado === "pendiente";

              return (
                <Card key={solicitud.id} className="hover:shadow-md transition-shadow">
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-4">
                        <div className="text-center min-w-[60px]">
                          <p className="text-2xl font-bold text-warm-900">{solicitud.dias_solicitados}</p>
                          <p className="text-xs text-warm-500">días</p>
                        </div>
                        <div className="border-l border-warm-200 pl-4">
                          <p className="font-medium text-warm-900">
                            {formatDate(solicitud.fecha_inicio)} - {formatDate(solicitud.fecha_fin)}
                          </p>
                          {solicitud.comentarios && (
                            <p className="text-sm text-warm-500 mt-1">{solicitud.comentarios}</p>
                          )}
                          <p className="text-xs text-warm-400 mt-1">
                            Solicitado el {formatDate(solicitud.created_at || "")}
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center gap-3">
                        <span className={`inline-flex items-center gap-1 px-3 py-1.5 rounded-full text-xs font-medium ${badge.bg} ${badge.text}`}>
                          <BadgeIcon className="w-3 h-3" />
                          {solicitud.estado_display || solicitud.estado.charAt(0).toUpperCase() + solicitud.estado.slice(1)}
                        </span>
                        {puedeCancel && (
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => cancelarMutation.mutate(solicitud.id)}
                            disabled={cancelarMutation.isPending}
                            className="text-warm-500 hover:text-red-600"
                          >
                            Cancelar
                          </Button>
                        )}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        )}
      </div>

      {/* Dialog para solicitar */}
      <Dialog open={showSolicitarDialog} onOpenChange={setShowSolicitarDialog}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Palmtree className="w-5 h-5 text-horizon-600" />
              Solicitar Vacaciones
            </DialogTitle>
            <DialogDescription>
              Selecciona las fechas para tu solicitud de vacaciones
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4 py-4">
            {/* Fechas */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-warm-700 mb-1">
                  Fecha inicio *
                </label>
                <Input
                  type="date"
                  value={fechaInicio}
                  onChange={(e) => setFechaInicio(e.target.value)}
                  min={hoy}
                  className="w-full"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-warm-700 mb-1">
                  Fecha fin *
                </label>
                <Input
                  type="date"
                  value={fechaFin}
                  onChange={(e) => setFechaFin(e.target.value)}
                  min={fechaInicio || hoy}
                  className="w-full"
                />
              </div>
            </div>

            {/* Días calculados */}
            {diasCalculados > 0 && (
              <div className="bg-horizon-50 border border-horizon-200 rounded-lg p-3 text-center">
                <p className="text-2xl font-bold text-horizon-700">{diasCalculados}</p>
                <p className="text-sm text-horizon-600">días solicitados</p>
              </div>
            )}

            {/* Validaciones */}
            {fechaInicio && fechaInicio < hoy && (
              <div className="flex items-center gap-2 text-red-600 text-sm">
                <AlertCircle className="w-4 h-4" />
                La fecha de inicio no puede ser en el pasado
              </div>
            )}
            {fechaInicio && fechaFin && fechaFin < fechaInicio && (
              <div className="flex items-center gap-2 text-red-600 text-sm">
                <AlertCircle className="w-4 h-4" />
                La fecha fin debe ser igual o posterior a la fecha inicio
              </div>
            )}

            {/* Comentarios */}
            <div>
              <label className="block text-sm font-medium text-warm-700 mb-1">
                Comentarios (opcional)
              </label>
              <textarea
                value={comentarios}
                onChange={(e) => setComentarios(e.target.value)}
                placeholder="Agrega algún comentario para tu solicitud..."
                rows={2}
                className="w-full px-3 py-2 border border-warm-300 rounded-lg text-warm-900 bg-white placeholder:text-warm-400 resize-none focus:ring-2 focus:ring-horizon-500 focus:border-horizon-500"
              />
            </div>

            {/* Días disponibles info */}
            {miResumen && (
              <div className="text-sm text-warm-500 bg-warm-50 rounded-lg p-3">
                <p>
                  Tienes <strong className="text-warm-900">{miResumen.total_disponible} días</strong> disponibles
                </p>
              </div>
            )}
          </div>

          <DialogFooter className="gap-2">
            <Button
              variant="outline"
              onClick={() => setShowSolicitarDialog(false)}
            >
              Cancelar
            </Button>
            <Button
              onClick={() => crearSolicitudMutation.mutate({
                fecha_inicio: fechaInicio,
                fecha_fin: fechaFin,
                comentarios: comentarios || undefined,
              })}
              disabled={!puedeEnviar || crearSolicitudMutation.isPending}
              className="bg-horizon-600 hover:bg-horizon-700"
            >
              {crearSolicitudMutation.isPending ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Enviando...
                </>
              ) : (
                "Enviar solicitud"
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
