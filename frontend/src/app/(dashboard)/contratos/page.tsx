"use client";

import { useState, useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import api from "@/lib/api";
import { useAuthStore } from "@/stores/auth-store";
import { formatCurrency, formatDate } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Contrato } from "@/types";
import {
  FileText,
  Plus,
  Search,
  AlertTriangle,
  CheckCircle,
  Clock,
  XCircle,
  ChevronRight,
  Users,
  Loader2,
  RefreshCw,
  FileX,
} from "lucide-react";

export default function ContratosPage() {
  const { empresaActual } = useAuthStore();
  const [mounted, setMounted] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");
  const [filtroEstado, setFiltroEstado] = useState<string>("");
  const [filtroTipo, setFiltroTipo] = useState<string>("");

  useEffect(() => {
    setMounted(true);
  }, []);

  // Query para resumen de contratos
  const { data: resumen } = useQuery({
    queryKey: ["contratos-resumen", empresaActual?.id],
    queryFn: async () => {
      const response = await api.get("/contratos/resumen/");
      return response.data;
    },
    enabled: mounted && !!empresaActual?.id,
  });

  // Query para contratos
  const { data: contratos, isLoading } = useQuery<Contrato[]>({
    queryKey: ["contratos", empresaActual?.id, filtroEstado, filtroTipo],
    queryFn: async () => {
      let url = "/contratos/";
      const params = new URLSearchParams();
      if (filtroEstado) params.append("estado", filtroEstado);
      if (filtroTipo) params.append("tipo_contrato", filtroTipo);
      if (params.toString()) url += `?${params.toString()}`;

      const response = await api.get(url);
      const data = response.data;
      return Array.isArray(data) ? data : data?.results || [];
    },
    enabled: mounted && !!empresaActual?.id,
  });

  // Query para contratos por vencer (proximos 30 dias)
  const { data: contratosPorVencer } = useQuery<Contrato[]>({
    queryKey: ["contratos-por-vencer", empresaActual?.id],
    queryFn: async () => {
      const response = await api.get("/contratos/?por_vencer=30");
      const data = response.data;
      return Array.isArray(data) ? data : data?.results || [];
    },
    enabled: mounted && !!empresaActual?.id,
  });

  if (!mounted) return null;

  const contratosList = contratos || [];
  const porVencerList = contratosPorVencer || [];

  // Filtrar por busqueda
  const contratosFiltrados = contratosList.filter((contrato) => {
    if (!searchTerm) return true;
    const searchLower = searchTerm.toLowerCase();
    return (
      contrato.empleado_nombre?.toLowerCase().includes(searchLower) ||
      contrato.tipo_contrato?.toLowerCase().includes(searchLower) ||
      contrato.puesto?.toLowerCase().includes(searchLower)
    );
  });

  const getEstadoBadge = (estado: string) => {
    const badges: Record<string, { bg: string; text: string; icon: typeof CheckCircle }> = {
      vigente: { bg: "bg-green-100", text: "text-green-700", icon: CheckCircle },
      vencido: { bg: "bg-red-100", text: "text-red-700", icon: XCircle },
      renovado: { bg: "bg-blue-100", text: "text-blue-700", icon: RefreshCw },
      cancelado: { bg: "bg-warm-100", text: "text-warm-600", icon: XCircle },
      terminado: { bg: "bg-warm-200", text: "text-warm-700", icon: FileX },
    };
    return badges[estado] || { bg: "bg-amber-100", text: "text-amber-700", icon: Clock };
  };

  const getTipoLabel = (tipo: string) => {
    const labels: Record<string, string> = {
      indefinido: "Indefinido",
      temporal: "Temporal",
      obra: "Obra det.",
      tiempo: "Tiempo det.",
      capacitacion: "Capacitacion",
      prueba: "Prueba",
    };
    return labels[tipo] || tipo;
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
          <h1 className="text-2xl font-display font-semibold text-warm-900">Contratos</h1>
          <p className="text-sm text-warm-500 mt-1">
            {contratosList.length} contrato{contratosList.length !== 1 ? "s" : ""} registrado
            {contratosList.length !== 1 ? "s" : ""}
          </p>
        </div>
        <Link href="/contratos/nuevo">
          <Button>
            <Plus className="w-4 h-4 mr-2" />
            Nuevo contrato
          </Button>
        </Link>
      </div>

      {/* Resumen */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-xl border border-warm-200 p-5">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-warm-500">Vigentes</p>
              <p className="text-2xl font-semibold text-green-600 mt-1">
                {resumen?.vigentes || 0}
              </p>
            </div>
            <div className="w-12 h-12 bg-green-100 rounded-xl flex items-center justify-center">
              <CheckCircle className="w-6 h-6 text-green-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl border border-warm-200 p-5">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-warm-500">Por vencer (30 dias)</p>
              <p className="text-2xl font-semibold text-amber-600 mt-1">
                {resumen?.por_vencer_30_dias || 0}
              </p>
            </div>
            <div className="w-12 h-12 bg-amber-100 rounded-xl flex items-center justify-center">
              <AlertTriangle className="w-6 h-6 text-amber-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl border border-warm-200 p-5">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-warm-500">Vencidos</p>
              <p className="text-2xl font-semibold text-red-600 mt-1">
                {resumen?.vencidos || 0}
              </p>
            </div>
            <div className="w-12 h-12 bg-red-100 rounded-xl flex items-center justify-center">
              <XCircle className="w-6 h-6 text-red-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl border border-warm-200 p-5">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-warm-500">Renovados</p>
              <p className="text-2xl font-semibold text-blue-600 mt-1">
                {resumen?.renovados || 0}
              </p>
            </div>
            <div className="w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center">
              <RefreshCw className="w-6 h-6 text-blue-600" />
            </div>
          </div>
        </div>
      </div>

      {/* Alerta de contratos por vencer */}
      {porVencerList.length > 0 && (
        <div className="bg-amber-50 border border-amber-200 rounded-xl p-4">
          <div className="flex items-start gap-3">
            <AlertTriangle className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" />
            <div className="flex-1">
              <p className="font-medium text-amber-800">
                {porVencerList.length} contrato{porVencerList.length !== 1 ? "s" : ""} por vencer
              </p>
              <p className="text-sm text-amber-700 mt-1">
                Los siguientes contratos vencen en los proximos 30 dias y requieren atencion:
              </p>
              <div className="mt-3 space-y-2">
                {porVencerList.slice(0, 3).map((contrato) => {
                  const dias = contrato.dias_para_vencer;
                  return (
                    <Link
                      key={contrato.id}
                      href={`/contratos/${contrato.id}`}
                      className="flex items-center justify-between bg-white rounded-lg p-2 hover:bg-amber-100 transition-colors"
                    >
                      <span className="text-sm text-warm-900">
                        {contrato.empleado_nombre} - {getTipoLabel(contrato.tipo_contrato)}
                      </span>
                      <span className="text-sm font-medium text-amber-700">
                        {dias === 0
                          ? "Vence hoy"
                          : dias === 1
                          ? "Vence manana"
                          : `${dias} dias`}
                      </span>
                    </Link>
                  );
                })}
              </div>
              {porVencerList.length > 3 && (
                <p className="text-sm text-amber-600 mt-2">
                  Y {porVencerList.length - 3} mas...
                </p>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Filtros */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-warm-400" />
          <input
            type="text"
            placeholder="Buscar por empleado, tipo o puesto..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-warm-300 rounded-lg text-warm-900 bg-white placeholder:text-warm-400 focus:ring-2 focus:ring-horizon-500 focus:border-horizon-500"
          />
        </div>
        <select
          value={filtroEstado}
          onChange={(e) => setFiltroEstado(e.target.value)}
          className="px-4 py-2 border border-warm-300 rounded-lg text-warm-900 bg-white focus:ring-2 focus:ring-horizon-500 focus:border-horizon-500"
        >
          <option value="">Todos los estados</option>
          <option value="vigente">Vigentes</option>
          <option value="vencido">Vencidos</option>
          <option value="renovado">Renovados</option>
          <option value="terminado">Terminados</option>
          <option value="cancelado">Cancelados</option>
        </select>
        <select
          value={filtroTipo}
          onChange={(e) => setFiltroTipo(e.target.value)}
          className="px-4 py-2 border border-warm-300 rounded-lg text-warm-900 bg-white focus:ring-2 focus:ring-horizon-500 focus:border-horizon-500"
        >
          <option value="">Todos los tipos</option>
          <option value="indefinido">Indefinido</option>
          <option value="temporal">Temporal</option>
          <option value="obra">Obra determinada</option>
          <option value="tiempo">Tiempo determinado</option>
          <option value="capacitacion">Capacitacion</option>
          <option value="prueba">Periodo de prueba</option>
        </select>
      </div>

      {/* Lista de contratos */}
      {contratosFiltrados.length === 0 ? (
        <div className="bg-white rounded-xl border border-warm-200 p-12 text-center">
          <FileText className="w-16 h-16 text-warm-300 mx-auto mb-4" />
          <h2 className="text-lg font-semibold text-warm-900">
            {searchTerm ? "Sin resultados" : "Sin contratos registrados"}
          </h2>
          <p className="text-warm-500 mt-2 max-w-md mx-auto">
            {searchTerm
              ? `No se encontraron contratos con "${searchTerm}"`
              : "Crea el primer contrato para comenzar a gestionar los acuerdos laborales."}
          </p>
          {!searchTerm && (
            <Link href="/contratos/nuevo">
              <Button className="mt-4">
                <Plus className="w-4 h-4 mr-2" />
                Crear contrato
              </Button>
            </Link>
          )}
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
                    Tipo
                  </th>
                  <th className="text-left text-xs font-medium text-warm-500 uppercase tracking-wider px-4 py-3">
                    Vigencia
                  </th>
                  <th className="text-left text-xs font-medium text-warm-500 uppercase tracking-wider px-4 py-3">
                    Estado
                  </th>
                  <th className="text-right text-xs font-medium text-warm-500 uppercase tracking-wider px-4 py-3">
                    Salario
                  </th>
                  <th className="px-4 py-3"></th>
                </tr>
              </thead>
              <tbody className="divide-y divide-warm-100">
                {contratosFiltrados.map((contrato) => {
                  const badge = getEstadoBadge(contrato.estado);
                  const BadgeIcon = badge.icon;
                  const dias = contrato.dias_para_vencer;
                  const porVencer =
                    dias !== null &&
                    dias !== undefined &&
                    dias >= 0 &&
                    dias <= 30 &&
                    contrato.estado === "vigente";

                  return (
                    <tr key={contrato.id} className="hover:bg-warm-50 transition-colors">
                      <td className="px-4 py-4">
                        <div className="flex items-center gap-3">
                          <div className="w-10 h-10 bg-horizon-100 rounded-full flex items-center justify-center">
                            <Users className="w-5 h-5 text-horizon-600" />
                          </div>
                          <div>
                            <p className="font-medium text-warm-900">
                              {contrato.empleado_nombre || "Sin nombre"}
                            </p>
                            <p className="text-sm text-warm-500">
                              {contrato.puesto || "Sin puesto"}
                            </p>
                          </div>
                        </div>
                      </td>
                      <td className="px-4 py-4">
                        <span className="px-2 py-1 bg-warm-100 text-warm-700 rounded text-sm">
                          {contrato.tipo_contrato_display || getTipoLabel(contrato.tipo_contrato)}
                        </span>
                      </td>
                      <td className="px-4 py-4">
                        <div className="text-sm">
                          <p className="text-warm-900">{formatDate(contrato.fecha_inicio)}</p>
                          <p className="text-warm-500">
                            {contrato.fecha_fin
                              ? `al ${formatDate(contrato.fecha_fin)}`
                              : "Indefinido"}
                          </p>
                          {porVencer && (
                            <p className="text-amber-600 text-xs font-medium mt-1">
                              Vence en {dias} dia{dias !== 1 ? "s" : ""}
                            </p>
                          )}
                        </div>
                      </td>
                      <td className="px-4 py-4">
                        <span
                          className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${badge.bg} ${badge.text}`}
                        >
                          <BadgeIcon className="w-3 h-3" />
                          {contrato.estado_display ||
                            contrato.estado?.charAt(0).toUpperCase() + contrato.estado?.slice(1)}
                        </span>
                      </td>
                      <td className="px-4 py-4 text-right">
                        <p className="font-medium text-warm-900">
                          {contrato.salario_mensual
                            ? formatCurrency(contrato.salario_mensual)
                            : "-"}
                        </p>
                        <p className="text-xs text-warm-500">mensual</p>
                      </td>
                      <td className="px-4 py-4 text-right">
                        <Link
                          href={`/contratos/${contrato.id}`}
                          className="text-horizon-600 hover:text-horizon-700"
                        >
                          <ChevronRight className="w-5 h-5" />
                        </Link>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
