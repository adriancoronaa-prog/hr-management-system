"use client";

import { useState, useEffect } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import Link from "next/link";
import api from "@/lib/api";
import { useAuthStore } from "@/stores/auth-store";
import { formatDate } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import {
  SolicitudVacaciones,
  ResumenVacaciones,
  EstadisticasVacaciones,
} from "@/types";
import {
  Calendar,
  Plus,
  Clock,
  CheckCircle,
  XCircle,
  AlertCircle,
  User,
  ChevronRight,
  Loader2,
  Palmtree,
  X,
} from "lucide-react";

export default function VacacionesPage() {
  const { user, empresaActual } = useAuthStore();
  const queryClient = useQueryClient();
  const [mounted, setMounted] = useState(false);
  const [filtroEstado, setFiltroEstado] = useState<string>("");
  const [showAprobarModal, setShowAprobarModal] = useState(false);
  const [showRechazarModal, setShowRechazarModal] = useState(false);
  const [solicitudSeleccionada, setSolicitudSeleccionada] =
    useState<SolicitudVacaciones | null>(null);
  const [motivoRechazo, setMotivoRechazo] = useState("");

  useEffect(() => {
    setMounted(true);
  }, []);

  const canManage =
    user?.rol === "admin" ||
    user?.rol === "rrhh" ||
    user?.rol === "empleador";

  // Query para solicitudes
  const { data: solicitudes, isLoading } = useQuery<SolicitudVacaciones[]>({
    queryKey: ["vacaciones", empresaActual?.id, filtroEstado],
    queryFn: async () => {
      let url = "/vacaciones/solicitudes/";
      if (filtroEstado) url += `?estado=${filtroEstado}`;
      const response = await api.get(url);
      const data = response.data;
      return Array.isArray(data) ? data : data?.results || [];
    },
    enabled: mounted && !!empresaActual?.id,
  });

  // Query para resumen del usuario actual
  const { data: miResumen } = useQuery<ResumenVacaciones>({
    queryKey: ["vacaciones-resumen", user?.id],
    queryFn: async () => {
      const response = await api.get("/vacaciones/solicitudes/resumen/");
      return response.data;
    },
    enabled: mounted && !!user,
  });

  // Query para estadisticas
  const { data: estadisticas } = useQuery<EstadisticasVacaciones>({
    queryKey: ["vacaciones-estadisticas", empresaActual?.id],
    queryFn: async () => {
      const response = await api.get("/vacaciones/solicitudes/estadisticas/");
      return response.data;
    },
    enabled: mounted && canManage && !!empresaActual?.id,
  });

  // Mutation para aprobar
  const aprobarMutation = useMutation({
    mutationFn: async (id: string) => {
      const response = await api.post(`/vacaciones/solicitudes/${id}/aprobar/`);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["vacaciones"] });
      queryClient.invalidateQueries({ queryKey: ["vacaciones-estadisticas"] });
      setShowAprobarModal(false);
      setSolicitudSeleccionada(null);
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
      queryClient.invalidateQueries({ queryKey: ["vacaciones"] });
      queryClient.invalidateQueries({ queryKey: ["vacaciones-estadisticas"] });
      setShowRechazarModal(false);
      setSolicitudSeleccionada(null);
      setMotivoRechazo("");
    },
  });

  if (!mounted) return null;

  const solicitudesList = solicitudes || [];
  const pendientes = solicitudesList.filter((s) => s.estado === "pendiente");

  const getEstadoBadge = (estado: string) => {
    const badges: Record<
      string,
      { bg: string; text: string; icon: typeof Clock }
    > = {
      pendiente: { bg: "bg-amber-100", text: "text-amber-700", icon: Clock },
      aprobada: { bg: "bg-green-100", text: "text-green-700", icon: CheckCircle },
      rechazada: { bg: "bg-red-100", text: "text-red-700", icon: XCircle },
      cancelada: { bg: "bg-warm-100", text: "text-warm-600", icon: XCircle },
    };
    return badges[estado] || badges.pendiente;
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <Loader2 className="w-8 h-8 animate-spin text-horizon-500" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-display font-semibold text-warm-900">
            Vacaciones
          </h1>
          <p className="text-sm text-warm-500 mt-1">
            Gestion de solicitudes de vacaciones
          </p>
        </div>
        <Link href="/vacaciones/solicitar">
          <Button>
            <Plus className="w-4 h-4 mr-2" />
            Solicitar vacaciones
          </Button>
        </Link>
      </div>

      {/* Resumen del usuario */}
      {miResumen && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-white rounded-xl border border-warm-200 p-5">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-warm-500">Dias disponibles</p>
                <p className="text-3xl font-semibold text-green-600 mt-1">
                  {miResumen.total_disponible}
                </p>
                <p className="text-xs text-warm-400 mt-1">
                  {miResumen.dias_correspondientes_anio_actual} este ano
                </p>
              </div>
              <div className="w-12 h-12 bg-green-100 rounded-xl flex items-center justify-center">
                <Palmtree className="w-6 h-6 text-green-600" />
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl border border-warm-200 p-5">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-warm-500">Dias tomados</p>
                <p className="text-3xl font-semibold text-warm-900 mt-1">
                  {miResumen.dias_tomados_anio_actual}
                </p>
                <p className="text-xs text-warm-400 mt-1">Este ano</p>
              </div>
              <div className="w-12 h-12 bg-horizon-100 rounded-xl flex items-center justify-center">
                <Calendar className="w-6 h-6 text-horizon-600" />
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl border border-warm-200 p-5">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-warm-500">Antiguedad</p>
                <p className="text-3xl font-semibold text-warm-900 mt-1">
                  {miResumen.antiguedad_anios}
                </p>
                <p className="text-xs text-warm-400 mt-1">
                  ano{miResumen.antiguedad_anios !== 1 ? "s" : ""}
                </p>
              </div>
              <div className="w-12 h-12 bg-warm-100 rounded-xl flex items-center justify-center">
                <User className="w-6 h-6 text-warm-600" />
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl border border-warm-200 p-5">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-warm-500">Pendientes anteriores</p>
                <p className="text-3xl font-semibold text-amber-600 mt-1">
                  {miResumen.dias_pendientes_anteriores}
                </p>
                <p className="text-xs text-warm-400 mt-1">dias</p>
              </div>
              <div className="w-12 h-12 bg-amber-100 rounded-xl flex items-center justify-center">
                <Clock className="w-6 h-6 text-amber-600" />
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Alerta de solicitudes pendientes para aprobar */}
      {canManage && pendientes.length > 0 && (
        <div className="bg-amber-50 border border-amber-200 rounded-xl p-4">
          <div className="flex items-center gap-3">
            <AlertCircle className="w-5 h-5 text-amber-600 flex-shrink-0" />
            <p className="font-medium text-amber-800">
              {pendientes.length} solicitud
              {pendientes.length !== 1 ? "es" : ""} pendiente
              {pendientes.length !== 1 ? "s" : ""} de aprobacion
            </p>
          </div>
        </div>
      )}

      {/* Estadisticas para managers */}
      {canManage && estadisticas && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 text-center">
            <p className="text-2xl font-semibold text-amber-700">
              {estadisticas.pendientes}
            </p>
            <p className="text-sm text-amber-600">Pendientes</p>
          </div>
          <div className="bg-green-50 border border-green-200 rounded-lg p-4 text-center">
            <p className="text-2xl font-semibold text-green-700">
              {estadisticas.aprobadas}
            </p>
            <p className="text-sm text-green-600">Aprobadas</p>
          </div>
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-center">
            <p className="text-2xl font-semibold text-red-700">
              {estadisticas.rechazadas}
            </p>
            <p className="text-sm text-red-600">Rechazadas</p>
          </div>
          <div className="bg-horizon-50 border border-horizon-200 rounded-lg p-4 text-center">
            <p className="text-2xl font-semibold text-horizon-700">
              {estadisticas.proximas_7_dias}
            </p>
            <p className="text-sm text-horizon-600">Proximos 7 dias</p>
          </div>
        </div>
      )}

      {/* Filtros */}
      <div className="flex gap-4">
        <select
          value={filtroEstado}
          onChange={(e) => setFiltroEstado(e.target.value)}
          className="px-4 py-2 border border-warm-300 rounded-lg text-warm-900 bg-white focus:ring-2 focus:ring-horizon-500 focus:border-horizon-500"
        >
          <option value="">Todos los estados</option>
          <option value="pendiente">Pendientes</option>
          <option value="aprobada">Aprobadas</option>
          <option value="rechazada">Rechazadas</option>
          <option value="cancelada">Canceladas</option>
        </select>
      </div>

      {/* Lista de solicitudes */}
      {solicitudesList.length === 0 ? (
        <div className="bg-white rounded-xl border border-warm-200 p-12 text-center">
          <Palmtree className="w-16 h-16 text-warm-300 mx-auto mb-4" />
          <h2 className="text-lg font-semibold text-warm-900">
            Sin solicitudes de vacaciones
          </h2>
          <p className="text-warm-500 mt-2 max-w-md mx-auto">
            No hay solicitudes de vacaciones registradas.
          </p>
          <Link href="/vacaciones/solicitar">
            <Button className="mt-4">
              <Plus className="w-4 h-4 mr-2" />
              Solicitar vacaciones
            </Button>
          </Link>
        </div>
      ) : (
        <div className="bg-white rounded-xl border border-warm-200 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-warm-100 bg-warm-50">
                  <th className="text-left text-xs font-medium text-warm-500 uppercase tracking-wider px-4 py-3">
                    Empleado
                  </th>
                  <th className="text-left text-xs font-medium text-warm-500 uppercase tracking-wider px-4 py-3">
                    Periodo
                  </th>
                  <th className="text-center text-xs font-medium text-warm-500 uppercase tracking-wider px-4 py-3">
                    Dias
                  </th>
                  <th className="text-left text-xs font-medium text-warm-500 uppercase tracking-wider px-4 py-3">
                    Estado
                  </th>
                  <th className="text-left text-xs font-medium text-warm-500 uppercase tracking-wider px-4 py-3">
                    Fecha solicitud
                  </th>
                  <th className="px-4 py-3"></th>
                </tr>
              </thead>
              <tbody className="divide-y divide-warm-100">
                {solicitudesList.map((solicitud) => {
                  const badge = getEstadoBadge(solicitud.estado);
                  const BadgeIcon = badge.icon;

                  return (
                    <tr
                      key={solicitud.id}
                      className="hover:bg-warm-50 transition-colors"
                    >
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
                        <p className="text-warm-900">
                          {formatDate(solicitud.fecha_inicio)}
                        </p>
                        <p className="text-sm text-warm-500">
                          al {formatDate(solicitud.fecha_fin)}
                        </p>
                      </td>
                      <td className="px-4 py-4 text-center">
                        <span className="text-lg font-semibold text-warm-900">
                          {solicitud.dias_solicitados}
                        </span>
                      </td>
                      <td className="px-4 py-4">
                        <span
                          className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${badge.bg} ${badge.text}`}
                        >
                          <BadgeIcon className="w-3 h-3" />
                          {solicitud.estado_display ||
                            solicitud.estado.charAt(0).toUpperCase() +
                              solicitud.estado.slice(1)}
                        </span>
                      </td>
                      <td className="px-4 py-4 text-sm text-warm-500">
                        {formatDate(solicitud.created_at)}
                      </td>
                      <td className="px-4 py-4">
                        <div className="flex items-center gap-2">
                          {solicitud.estado === "pendiente" &&
                            solicitud.puede_aprobar && (
                              <>
                                <button
                                  type="button"
                                  onClick={() => {
                                    setSolicitudSeleccionada(solicitud);
                                    setShowAprobarModal(true);
                                  }}
                                  className="text-green-600 hover:text-green-700 text-sm font-medium"
                                >
                                  Aprobar
                                </button>
                                <button
                                  type="button"
                                  onClick={() => {
                                    setSolicitudSeleccionada(solicitud);
                                    setShowRechazarModal(true);
                                  }}
                                  className="text-red-600 hover:text-red-700 text-sm font-medium"
                                >
                                  Rechazar
                                </button>
                              </>
                            )}
                          <Link
                            href={`/vacaciones/${solicitud.id}`}
                            className="text-horizon-600 hover:text-horizon-700"
                          >
                            <ChevronRight className="w-5 h-5" />
                          </Link>
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Modal Aprobar */}
      {showAprobarModal && solicitudSeleccionada && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl max-w-md w-full p-6 shadow-xl">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-warm-900 flex items-center gap-2">
                <CheckCircle className="w-5 h-5 text-green-600" />
                Aprobar solicitud
              </h3>
              <button
                type="button"
                onClick={() => {
                  setShowAprobarModal(false);
                  setSolicitudSeleccionada(null);
                }}
                className="text-warm-400 hover:text-warm-600"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <p className="text-sm text-warm-600 mb-4">
              ¿Aprobar las vacaciones de{" "}
              <strong>{solicitudSeleccionada.empleado_nombre}</strong> del{" "}
              {formatDate(solicitudSeleccionada.fecha_inicio)} al{" "}
              {formatDate(solicitudSeleccionada.fecha_fin)}?
            </p>

            <div className="p-3 bg-green-50 rounded-lg mb-4">
              <p className="text-green-800 font-medium text-center">
                {solicitudSeleccionada.dias_solicitados} dias de vacaciones
              </p>
            </div>

            <div className="flex gap-3">
              <Button
                variant="outline"
                onClick={() => {
                  setShowAprobarModal(false);
                  setSolicitudSeleccionada(null);
                }}
                className="flex-1"
              >
                Cancelar
              </Button>
              <Button
                onClick={() => aprobarMutation.mutate(solicitudSeleccionada.id)}
                disabled={aprobarMutation.isPending}
                className="flex-1 bg-green-600 hover:bg-green-700"
              >
                {aprobarMutation.isPending ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Aprobando...
                  </>
                ) : (
                  "Aprobar"
                )}
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* Modal Rechazar */}
      {showRechazarModal && solicitudSeleccionada && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl max-w-md w-full p-6 shadow-xl">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-warm-900 flex items-center gap-2">
                <XCircle className="w-5 h-5 text-red-600" />
                Rechazar solicitud
              </h3>
              <button
                type="button"
                onClick={() => {
                  setShowRechazarModal(false);
                  setSolicitudSeleccionada(null);
                  setMotivoRechazo("");
                }}
                className="text-warm-400 hover:text-warm-600"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <p className="text-sm text-warm-600 mb-4">
              Rechazar las vacaciones de{" "}
              <strong>{solicitudSeleccionada.empleado_nombre}</strong>
            </p>

            <div className="mb-4">
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

            <div className="flex gap-3">
              <Button
                variant="outline"
                onClick={() => {
                  setShowRechazarModal(false);
                  setSolicitudSeleccionada(null);
                  setMotivoRechazo("");
                }}
                className="flex-1"
              >
                Cancelar
              </Button>
              <Button
                variant="danger"
                onClick={() =>
                  rechazarMutation.mutate({
                    id: solicitudSeleccionada.id,
                    motivo: motivoRechazo,
                  })
                }
                disabled={rechazarMutation.isPending || !motivoRechazo.trim()}
                className="flex-1"
              >
                {rechazarMutation.isPending ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Rechazando...
                  </>
                ) : (
                  "Rechazar"
                )}
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
