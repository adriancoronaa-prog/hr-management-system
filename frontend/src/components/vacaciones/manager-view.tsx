"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import api from "@/lib/api";
import { useAuthStore } from "@/stores/auth-store";
import { formatDate } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "@/components/ui/dialog";
import { EmployeeView } from "./employee-view";
import type { SolicitudVacaciones, EstadisticasVacaciones } from "@/types";
import {
  Clock,
  CheckCircle,
  XCircle,
  User,
  Loader2,
  AlertCircle,
  CalendarCheck,
  ChevronRight,
  Users,
} from "lucide-react";

type TabEstado = "" | "pendiente" | "aprobada" | "rechazada";

export function ManagerView() {
  const { empresaActual } = useAuthStore();
  const queryClient = useQueryClient();

  const [filtroTab, setFiltroTab] = useState<TabEstado>("");
  const [showAprobarModal, setShowAprobarModal] = useState(false);
  const [showRechazarModal, setShowRechazarModal] = useState(false);
  const [solicitudSeleccionada, setSolicitudSeleccionada] = useState<SolicitudVacaciones | null>(null);
  const [motivoRechazo, setMotivoRechazo] = useState("");

  // Query para estadísticas
  const { data: estadisticas } = useQuery<EstadisticasVacaciones>({
    queryKey: ["vacaciones-estadisticas", empresaActual?.id],
    queryFn: async () => {
      const response = await api.get("/vacaciones/solicitudes/estadisticas/");
      return response.data;
    },
    enabled: !!empresaActual?.id,
  });

  // Query para todas las solicitudes (filtradas por tab)
  const { data: solicitudes, isLoading } = useQuery<SolicitudVacaciones[]>({
    queryKey: ["vacaciones-team", empresaActual?.id, filtroTab],
    queryFn: async () => {
      let url = "/vacaciones/solicitudes/";
      if (filtroTab) url += `?estado=${filtroTab}`;
      const response = await api.get(url);
      const data = response.data;
      return Array.isArray(data) ? data : data?.results || [];
    },
    enabled: !!empresaActual?.id,
  });

  // Mutation para aprobar
  const aprobarMutation = useMutation({
    mutationFn: async (id: string) => {
      const response = await api.post(`/vacaciones/solicitudes/${id}/aprobar/`);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["vacaciones-team"] });
      queryClient.invalidateQueries({ queryKey: ["vacaciones-estadisticas"] });
      setShowAprobarModal(false);
      setSolicitudSeleccionada(null);
      toast.success("Solicitud aprobada", {
        description: "Las vacaciones han sido aprobadas correctamente.",
      });
    },
    onError: (error: any) => {
      toast.error("Error al aprobar", {
        description: error.response?.data?.error || "Intenta de nuevo.",
      });
    },
  });

  // Mutation para rechazar
  const rechazarMutation = useMutation({
    mutationFn: async ({ id, motivo }: { id: string; motivo: string }) => {
      const response = await api.post(`/vacaciones/solicitudes/${id}/rechazar/`, {
        motivo,
      });
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["vacaciones-team"] });
      queryClient.invalidateQueries({ queryKey: ["vacaciones-estadisticas"] });
      setShowRechazarModal(false);
      setSolicitudSeleccionada(null);
      setMotivoRechazo("");
      toast.success("Solicitud rechazada", {
        description: "La solicitud ha sido rechazada.",
      });
    },
    onError: (error: any) => {
      toast.error("Error al rechazar", {
        description: error.response?.data?.error || "Intenta de nuevo.",
      });
    },
  });

  const solicitudesList = solicitudes || [];
  const pendientes = solicitudesList.filter((s) => s.estado === "pendiente");

  const getEstadoBadge = (estado: string) => {
    const badges: Record<string, { bg: string; text: string; icon: typeof Clock }> = {
      pendiente: { bg: "bg-amber-100", text: "text-amber-700", icon: Clock },
      aprobada: { bg: "bg-green-100", text: "text-green-700", icon: CheckCircle },
      rechazada: { bg: "bg-red-100", text: "text-red-700", icon: XCircle },
      cancelada: { bg: "bg-warm-100", text: "text-warm-600", icon: XCircle },
    };
    return badges[estado] || badges.pendiente;
  };

  const tabs: { value: TabEstado; label: string; count?: number }[] = [
    { value: "", label: "Todas" },
    { value: "pendiente", label: "Pendientes", count: estadisticas?.pendientes },
    { value: "aprobada", label: "Aprobadas", count: estadisticas?.aprobadas },
    { value: "rechazada", label: "Rechazadas", count: estadisticas?.rechazadas },
  ];

  return (
    <div className="space-y-8">
      {/* KPIs */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card className={estadisticas?.pendientes ? "border-amber-300 bg-amber-50" : ""}>
          <CardContent className="p-5">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-warm-500">Pendientes</p>
                <p className={`text-3xl font-bold mt-1 ${estadisticas?.pendientes ? "text-amber-600" : "text-warm-900"}`}>
                  {estadisticas?.pendientes || 0}
                </p>
                <p className="text-xs text-warm-400 mt-1">por aprobar</p>
              </div>
              <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${estadisticas?.pendientes ? "bg-amber-100" : "bg-warm-100"}`}>
                <Clock className={`w-6 h-6 ${estadisticas?.pendientes ? "text-amber-600" : "text-warm-600"}`} />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-5">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-warm-500">Próximos 7 días</p>
                <p className="text-3xl font-bold text-horizon-600 mt-1">
                  {estadisticas?.proximas_7_dias || 0}
                </p>
                <p className="text-xs text-warm-400 mt-1">vacaciones</p>
              </div>
              <div className="w-12 h-12 bg-horizon-100 rounded-xl flex items-center justify-center">
                <CalendarCheck className="w-6 h-6 text-horizon-600" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-5">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-warm-500">Aprobadas</p>
                <p className="text-3xl font-bold text-green-600 mt-1">
                  {estadisticas?.aprobadas || 0}
                </p>
                <p className="text-xs text-warm-400 mt-1">este periodo</p>
              </div>
              <div className="w-12 h-12 bg-green-100 rounded-xl flex items-center justify-center">
                <CheckCircle className="w-6 h-6 text-green-600" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-5">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-warm-500">Rechazadas</p>
                <p className="text-3xl font-bold text-warm-900 mt-1">
                  {estadisticas?.rechazadas || 0}
                </p>
                <p className="text-xs text-warm-400 mt-1">este periodo</p>
              </div>
              <div className="w-12 h-12 bg-warm-100 rounded-xl flex items-center justify-center">
                <XCircle className="w-6 h-6 text-warm-600" />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Alerta de pendientes */}
      {pendientes.length > 0 && filtroTab !== "pendiente" && (
        <div className="bg-amber-50 border border-amber-200 rounded-xl p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <AlertCircle className="w-5 h-5 text-amber-600 flex-shrink-0" />
              <p className="font-medium text-amber-800">
                {pendientes.length} solicitud{pendientes.length !== 1 ? "es" : ""} pendiente{pendientes.length !== 1 ? "s" : ""} de aprobación
              </p>
            </div>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setFiltroTab("pendiente")}
              className="text-amber-700 hover:text-amber-800 hover:bg-amber-100"
            >
              Ver pendientes
              <ChevronRight className="w-4 h-4 ml-1" />
            </Button>
          </div>
        </div>
      )}

      {/* Solicitudes del equipo */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-base flex items-center gap-2">
            <Users className="w-5 h-5 text-warm-500" />
            Solicitudes del Equipo
          </CardTitle>
        </CardHeader>
        <CardContent>
          {/* Tabs */}
          <div className="flex gap-1 mb-4 border-b border-warm-200">
            {tabs.map((tab) => (
              <button
                key={tab.value}
                onClick={() => setFiltroTab(tab.value)}
                className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
                  filtroTab === tab.value
                    ? "border-horizon-600 text-horizon-600"
                    : "border-transparent text-warm-500 hover:text-warm-700"
                }`}
              >
                {tab.label}
                {tab.count !== undefined && tab.count > 0 && (
                  <span className={`ml-1.5 px-1.5 py-0.5 text-xs rounded-full ${
                    filtroTab === tab.value ? "bg-horizon-100 text-horizon-700" : "bg-warm-100 text-warm-600"
                  }`}>
                    {tab.count}
                  </span>
                )}
              </button>
            ))}
          </div>

          {/* Table */}
          {isLoading ? (
            <div className="flex justify-center py-8">
              <Loader2 className="w-6 h-6 animate-spin text-horizon-500" />
            </div>
          ) : solicitudesList.length === 0 ? (
            <div className="py-8 text-center text-warm-500">
              No hay solicitudes {filtroTab ? `con estado "${filtroTab}"` : ""}
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-warm-100">
                    <th className="text-left text-xs font-medium text-warm-500 uppercase tracking-wider px-4 py-3">
                      Empleado
                    </th>
                    <th className="text-left text-xs font-medium text-warm-500 uppercase tracking-wider px-4 py-3">
                      Periodo
                    </th>
                    <th className="text-center text-xs font-medium text-warm-500 uppercase tracking-wider px-4 py-3">
                      Días
                    </th>
                    <th className="text-left text-xs font-medium text-warm-500 uppercase tracking-wider px-4 py-3">
                      Estado
                    </th>
                    <th className="text-right text-xs font-medium text-warm-500 uppercase tracking-wider px-4 py-3">
                      Acciones
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-warm-100">
                  {solicitudesList.map((solicitud) => {
                    const badge = getEstadoBadge(solicitud.estado);
                    const BadgeIcon = badge.icon;

                    return (
                      <tr key={solicitud.id} className="hover:bg-warm-50 transition-colors">
                        <td className="px-4 py-4">
                          <div className="flex items-center gap-3">
                            <div className="w-10 h-10 bg-horizon-100 rounded-full flex items-center justify-center">
                              <User className="w-5 h-5 text-horizon-600" />
                            </div>
                            <div>
                              <p className="font-medium text-warm-900">
                                {solicitud.empleado_nombre || "Sin nombre"}
                              </p>
                              <p className="text-sm text-warm-500">
                                {solicitud.empleado_puesto || "-"}
                              </p>
                            </div>
                          </div>
                        </td>
                        <td className="px-4 py-4">
                          <p className="text-warm-900">{formatDate(solicitud.fecha_inicio)}</p>
                          <p className="text-sm text-warm-500">al {formatDate(solicitud.fecha_fin)}</p>
                        </td>
                        <td className="px-4 py-4 text-center">
                          <span className="text-lg font-semibold text-warm-900">
                            {solicitud.dias_solicitados}
                          </span>
                        </td>
                        <td className="px-4 py-4">
                          <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${badge.bg} ${badge.text}`}>
                            <BadgeIcon className="w-3 h-3" />
                            {solicitud.estado_display || solicitud.estado.charAt(0).toUpperCase() + solicitud.estado.slice(1)}
                          </span>
                        </td>
                        <td className="px-4 py-4">
                          <div className="flex items-center justify-end gap-2">
                            {solicitud.estado === "pendiente" && solicitud.puede_aprobar && (
                              <>
                                <Button
                                  size="sm"
                                  variant="ghost"
                                  onClick={() => {
                                    setSolicitudSeleccionada(solicitud);
                                    setShowAprobarModal(true);
                                  }}
                                  className="text-green-600 hover:text-green-700 hover:bg-green-50"
                                >
                                  <CheckCircle className="w-4 h-4 mr-1" />
                                  Aprobar
                                </Button>
                                <Button
                                  size="sm"
                                  variant="ghost"
                                  onClick={() => {
                                    setSolicitudSeleccionada(solicitud);
                                    setShowRechazarModal(true);
                                  }}
                                  className="text-red-600 hover:text-red-700 hover:bg-red-50"
                                >
                                  <XCircle className="w-4 h-4 mr-1" />
                                  Rechazar
                                </Button>
                              </>
                            )}
                          </div>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Sección personal del manager */}
      <div className="border-t border-warm-200 pt-8">
        <h2 className="text-lg font-semibold text-warm-900 mb-4">Mis Vacaciones</h2>
        <EmployeeView />
      </div>

      {/* Modal Aprobar */}
      <Dialog open={showAprobarModal} onOpenChange={setShowAprobarModal}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <CheckCircle className="w-5 h-5 text-green-600" />
              Aprobar solicitud
            </DialogTitle>
            <DialogDescription>
              Confirma la aprobación de esta solicitud de vacaciones
            </DialogDescription>
          </DialogHeader>

          {solicitudSeleccionada && (
            <div className="py-4">
              <div className="bg-warm-50 rounded-lg p-4 space-y-2">
                <p className="font-medium text-warm-900">
                  {solicitudSeleccionada.empleado_nombre}
                </p>
                <p className="text-sm text-warm-600">
                  {formatDate(solicitudSeleccionada.fecha_inicio)} al{" "}
                  {formatDate(solicitudSeleccionada.fecha_fin)}
                </p>
                <p className="text-lg font-semibold text-green-600">
                  {solicitudSeleccionada.dias_solicitados} días de vacaciones
                </p>
              </div>
            </div>
          )}

          <DialogFooter className="gap-2">
            <Button
              variant="outline"
              onClick={() => {
                setShowAprobarModal(false);
                setSolicitudSeleccionada(null);
              }}
            >
              Cancelar
            </Button>
            <Button
              onClick={() => solicitudSeleccionada && aprobarMutation.mutate(solicitudSeleccionada.id)}
              disabled={aprobarMutation.isPending}
              className="bg-green-600 hover:bg-green-700"
            >
              {aprobarMutation.isPending ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Aprobando...
                </>
              ) : (
                <>
                  <CheckCircle className="w-4 h-4 mr-2" />
                  Aprobar
                </>
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Modal Rechazar */}
      <Dialog open={showRechazarModal} onOpenChange={setShowRechazarModal}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <XCircle className="w-5 h-5 text-red-600" />
              Rechazar solicitud
            </DialogTitle>
            <DialogDescription>
              Indica el motivo del rechazo (obligatorio)
            </DialogDescription>
          </DialogHeader>

          {solicitudSeleccionada && (
            <div className="py-4 space-y-4">
              <div className="bg-warm-50 rounded-lg p-4">
                <p className="font-medium text-warm-900">
                  {solicitudSeleccionada.empleado_nombre}
                </p>
                <p className="text-sm text-warm-600">
                  {formatDate(solicitudSeleccionada.fecha_inicio)} al{" "}
                  {formatDate(solicitudSeleccionada.fecha_fin)} ({solicitudSeleccionada.dias_solicitados} días)
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-warm-700 mb-1">
                  Motivo del rechazo *
                </label>
                <textarea
                  value={motivoRechazo}
                  onChange={(e) => setMotivoRechazo(e.target.value)}
                  placeholder="Explica el motivo del rechazo..."
                  rows={3}
                  className="w-full px-3 py-2 border border-warm-300 rounded-lg text-warm-900 bg-white placeholder:text-warm-400 resize-none focus:ring-2 focus:ring-horizon-500 focus:border-horizon-500"
                />
              </div>
            </div>
          )}

          <DialogFooter className="gap-2">
            <Button
              variant="outline"
              onClick={() => {
                setShowRechazarModal(false);
                setSolicitudSeleccionada(null);
                setMotivoRechazo("");
              }}
            >
              Cancelar
            </Button>
            <Button
              variant="danger"
              onClick={() =>
                solicitudSeleccionada &&
                rechazarMutation.mutate({
                  id: solicitudSeleccionada.id,
                  motivo: motivoRechazo,
                })
              }
              disabled={rechazarMutation.isPending || !motivoRechazo.trim()}
            >
              {rechazarMutation.isPending ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Rechazando...
                </>
              ) : (
                <>
                  <XCircle className="w-4 h-4 mr-2" />
                  Rechazar
                </>
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
