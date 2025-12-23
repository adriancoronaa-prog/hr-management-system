"use client";

import { useState, useRef, useEffect } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { notificacionesApi } from "@/lib/api";
import { cn } from "@/lib/utils";
import type { Notificacion } from "@/types/notificacion";
import {
  Bell,
  CheckCheck,
  Calendar,
  FileText,
  Receipt,
  Info,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Loader2,
  Users,
  Briefcase,
  MessageSquare,
} from "lucide-react";

const getIcon = (tipo: string) => {
  const icons: Record<string, React.ComponentType<{ className?: string }>> = {
    solicitud: FileText,
    aprobacion: CheckCircle,
    rechazo: XCircle,
    alerta: AlertTriangle,
    recordatorio: Calendar,
    confirmacion: CheckCircle,
    nomina: Receipt,
    documento: FileText,
    sistema: Info,
    vacaciones: Calendar,
    contrato: FileText,
    empleado: Users,
    empresa: Briefcase,
    chat: MessageSquare,
  };
  return icons[tipo] || Info;
};

const getPrioridadColor = (prioridad: string) => {
  switch (prioridad) {
    case "urgente":
      return "bg-red-100 text-red-600";
    case "alta":
      return "bg-orange-100 text-orange-600";
    case "media":
      return "bg-horizon-100 text-horizon-600";
    default:
      return "bg-gray-100 text-gray-500";
  }
};

export function NotificationsDropdown() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  const { data: countData } = useQuery({
    queryKey: ["notificaciones-count"],
    queryFn: notificacionesApi.getNoLeidasCount,
    refetchInterval: 30000,
  });

  const { data: notificaciones, isLoading } = useQuery<Notificacion[]>({
    queryKey: ["notificaciones-recientes"],
    queryFn: notificacionesApi.getRecientes,
    enabled: isOpen,
  });

  const marcarLeidaMutation = useMutation({
    mutationFn: notificacionesApi.marcarLeida,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["notificaciones-count"] });
      queryClient.invalidateQueries({ queryKey: ["notificaciones-recientes"] });
    },
  });

  const marcarTodasMutation = useMutation({
    mutationFn: notificacionesApi.marcarTodasLeidas,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["notificaciones-count"] });
      queryClient.invalidateQueries({ queryKey: ["notificaciones-recientes"] });
    },
  });

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(event.target as Node)
      ) {
        setIsOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const handleNotificacionClick = (notif: Notificacion) => {
    if (!notif.leida) {
      marcarLeidaMutation.mutate(notif.id);
    }
    if (notif.url_destino) {
      router.push(notif.url_destino);
    }
    setIsOpen(false);
  };

  const count = countData?.count || 0;

  return (
    <div className="relative" ref={dropdownRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="relative p-2 text-warm-500 hover:text-warm-700 hover:bg-warm-100 rounded-lg transition-colors"
        title="Notificaciones"
      >
        <Bell className="h-5 w-5" strokeWidth={1.5} />
        {count > 0 && (
          <span className="absolute -top-0.5 -right-0.5 flex h-4 w-4 items-center justify-center rounded-full bg-red-500 text-[10px] font-medium text-white">
            {count > 9 ? "9+" : count}
          </span>
        )}
      </button>

      {isOpen && (
        <div className="absolute right-0 mt-2 w-80 bg-white rounded-xl shadow-xl border border-warm-200 z-50 overflow-hidden">
          <div className="flex items-center justify-between px-4 py-3 border-b border-warm-100 bg-warm-50">
            <h3 className="font-semibold text-warm-900">Notificaciones</h3>
            {count > 0 && (
              <button
                onClick={() => marcarTodasMutation.mutate()}
                className="text-xs text-horizon-600 hover:text-horizon-700 flex items-center gap-1"
                disabled={marcarTodasMutation.isPending}
              >
                <CheckCheck className="h-3 w-3" />
                Marcar todas
              </button>
            )}
          </div>

          <div className="max-h-96 overflow-y-auto">
            {isLoading ? (
              <div className="flex items-center justify-center py-8">
                <Loader2 className="h-6 w-6 animate-spin text-warm-400" />
              </div>
            ) : notificaciones && notificaciones.length > 0 ? (
              <div className="divide-y divide-warm-100">
                {notificaciones.map((notif) => {
                  const Icon = getIcon(notif.tipo);
                  return (
                    <button
                      key={notif.id}
                      onClick={() => handleNotificacionClick(notif)}
                      className={cn(
                        "w-full px-4 py-3 text-left hover:bg-warm-50 transition-colors flex gap-3",
                        !notif.leida && "bg-horizon-50/50"
                      )}
                    >
                      <div
                        className={cn(
                          "flex-shrink-0 w-9 h-9 rounded-full flex items-center justify-center",
                          getPrioridadColor(notif.prioridad)
                        )}
                      >
                        <Icon className="h-4 w-4" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <p
                          className={cn(
                            "text-sm",
                            notif.leida
                              ? "text-warm-600"
                              : "text-warm-900 font-medium"
                          )}
                        >
                          {notif.titulo}
                        </p>
                        <p className="text-xs text-warm-500 line-clamp-2 mt-0.5">
                          {notif.mensaje}
                        </p>
                        <p className="text-xs text-warm-400 mt-1">
                          {new Date(notif.created_at).toLocaleDateString(
                            "es-MX",
                            {
                              day: "numeric",
                              month: "short",
                              hour: "2-digit",
                              minute: "2-digit",
                            }
                          )}
                        </p>
                      </div>
                      {!notif.leida && (
                        <div className="flex-shrink-0 w-2 h-2 rounded-full bg-horizon-500 mt-2" />
                      )}
                    </button>
                  );
                })}
              </div>
            ) : (
              <div className="py-8 text-center text-warm-500">
                <Bell className="h-8 w-8 mx-auto mb-2 text-warm-300" />
                <p className="text-sm">No tienes notificaciones</p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
