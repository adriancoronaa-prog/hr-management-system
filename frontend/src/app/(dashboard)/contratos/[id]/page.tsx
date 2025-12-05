"use client";

import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import Link from "next/link";
import api from "@/lib/api";
import { useAuthStore } from "@/stores/auth-store";
import { formatCurrency, formatDate } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Contrato, TIPO_CONTRATO_LARGO_OPTIONS } from "@/types";
import {
  ArrowLeft,
  FileText,
  User,
  Calendar,
  DollarSign,
  Briefcase,
  Clock,
  CheckCircle,
  XCircle,
  AlertTriangle,
  Edit,
  RefreshCw,
  MoreVertical,
  Trash2,
  Download,
  Building2,
  Loader2,
  X,
  Upload,
  Eye,
} from "lucide-react";

export default function DetalleContratoPage() {
  const params = useParams();
  const router = useRouter();
  const queryClient = useQueryClient();
  const { user, empresaActual } = useAuthStore();
  const [mounted, setMounted] = useState(false);
  const [showRenovarModal, setShowRenovarModal] = useState(false);
  const [showTerminarModal, setShowTerminarModal] = useState(false);
  const [motivoTerminacion, setMotivoTerminacion] = useState("");
  const [fechaTerminacion, setFechaTerminacion] = useState(new Date().toISOString().split("T")[0]);
  const [nuevaFechaInicio, setNuevaFechaInicio] = useState("");
  const [nuevaFechaFin, setNuevaFechaFin] = useState("");
  const [menuOpen, setMenuOpen] = useState(false);
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [archivoSeleccionado, setArchivoSeleccionado] = useState<File | null>(null);
  const [uploadError, setUploadError] = useState("");

  const contratoId = params.id as string;

  useEffect(() => {
    setMounted(true);
  }, []);

  const canEdit = user?.rol === "admin" || user?.rol === "rrhh" || user?.rol === "empleador";

  // Cargar contrato
  const { data: contrato, isLoading, error } = useQuery<Contrato>({
    queryKey: ["contrato", contratoId],
    queryFn: async () => {
      const response = await api.get(`/contratos/${contratoId}/`);
      return response.data;
    },
    enabled: mounted && !!contratoId,
  });

  // Mutation para renovar
  const renovarMutation = useMutation({
    mutationFn: async () => {
      const response = await api.post(`/contratos/${contratoId}/renovar/`, {
        fecha_inicio: nuevaFechaInicio || undefined,
        fecha_fin: nuevaFechaFin || undefined,
      });
      return response.data;
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["contrato", contratoId] });
      queryClient.invalidateQueries({ queryKey: ["contratos"] });
      queryClient.invalidateQueries({ queryKey: ["contratos-resumen"] });
      setShowRenovarModal(false);
      if (data.id) {
        router.push(`/contratos/${data.id}`);
      }
    },
    onError: (error: unknown) => {
      const axiosError = error as { response?: { data?: Record<string, unknown> } };
      alert("Error al renovar: " + JSON.stringify(axiosError.response?.data || "Error desconocido"));
    },
  });

  // Mutation para terminar
  const terminarMutation = useMutation({
    mutationFn: async () => {
      const response = await api.post(`/contratos/${contratoId}/terminar/`, {
        motivo: motivoTerminacion,
        fecha: fechaTerminacion,
      });
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["contrato", contratoId] });
      queryClient.invalidateQueries({ queryKey: ["contratos"] });
      queryClient.invalidateQueries({ queryKey: ["contratos-resumen"] });
      setShowTerminarModal(false);
    },
  });

  // Mutation para eliminar
  const eliminarMutation = useMutation({
    mutationFn: async () => {
      await api.delete(`/contratos/${contratoId}/`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["contratos"] });
      router.push("/contratos");
    },
  });

  // Mutation para subir documento
  const subirDocumentoMutation = useMutation({
    mutationFn: async (archivo: File) => {
      const formData = new FormData();
      formData.append("archivo", archivo);

      const response = await api.post(
        `/contratos/${contratoId}/subir_documento/`,
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      );
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["contrato", contratoId] });
      setShowUploadModal(false);
      setArchivoSeleccionado(null);
      setUploadError("");
    },
    onError: (error: unknown) => {
      const axiosError = error as { response?: { data?: { error?: string } } };
      setUploadError(axiosError.response?.data?.error || "Error al subir archivo");
    },
  });

  // Mutation para eliminar documento
  const eliminarDocumentoMutation = useMutation({
    mutationFn: async () => {
      await api.delete(`/contratos/${contratoId}/eliminar_documento/`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["contrato", contratoId] });
    },
  });

  const handleUploadArchivo = () => {
    if (!archivoSeleccionado) return;
    subirDocumentoMutation.mutate(archivoSeleccionado);
  };

  if (!mounted) return null;

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <Loader2 className="w-8 h-8 animate-spin text-horizon-500" />
      </div>
    );
  }

  if (error || !contrato) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] text-center">
        <AlertTriangle className="w-16 h-16 text-red-500 mb-4" />
        <h1 className="text-xl font-semibold text-warm-900">Contrato no encontrado</h1>
        <p className="text-warm-500 mt-2">El contrato que buscas no existe o no tienes acceso.</p>
        <Link href="/contratos">
          <Button variant="outline" className="mt-4">
            Volver a contratos
          </Button>
        </Link>
      </div>
    );
  }

  const getEstadoBadge = (estado: string) => {
    const badges: Record<string, { bg: string; text: string; icon: typeof CheckCircle; label: string }> = {
      vigente: { bg: "bg-green-100", text: "text-green-700", icon: CheckCircle, label: "Vigente" },
      vencido: { bg: "bg-red-100", text: "text-red-700", icon: XCircle, label: "Vencido" },
      renovado: { bg: "bg-blue-100", text: "text-blue-700", icon: RefreshCw, label: "Renovado" },
      cancelado: { bg: "bg-warm-100", text: "text-warm-600", icon: XCircle, label: "Cancelado" },
      terminado: { bg: "bg-warm-200", text: "text-warm-700", icon: XCircle, label: "Terminado" },
    };
    return badges[estado] || { bg: "bg-amber-100", text: "text-amber-700", icon: Clock, label: "Borrador" };
  };

  const getTipoLabel = (tipo: string) => {
    const option = TIPO_CONTRATO_LARGO_OPTIONS.find((o) => o.value === tipo);
    return option?.label || tipo;
  };

  const badge = getEstadoBadge(contrato.estado);
  const BadgeIcon = badge.icon;

  const dias = contrato.dias_para_vencer;
  const porVencer = dias !== null && dias !== undefined && dias >= 0 && dias <= 30 && contrato.estado === "vigente";

  return (
    <div className="max-w-4xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <Link
          href="/contratos"
          className="inline-flex items-center text-sm text-warm-500 hover:text-warm-700 mb-4"
        >
          <ArrowLeft className="w-4 h-4 mr-1" />
          Volver a contratos
        </Link>
      </div>

      {/* Card principal */}
      <Card className="mb-6">
        <CardContent className="p-6">
          <div className="flex items-start justify-between">
            <div className="flex items-center gap-4">
              <div className="w-16 h-16 bg-horizon-100 rounded-xl flex items-center justify-center">
                <FileText className="w-8 h-8 text-horizon-600" />
              </div>
              <div>
                <h1 className="text-xl font-display font-semibold text-warm-900">
                  Contrato {getTipoLabel(contrato.tipo_contrato)}
                </h1>
                <Link
                  href={`/empleados/${contrato.empleado}`}
                  className="text-horizon-600 hover:text-horizon-700 font-medium"
                >
                  {contrato.empleado_nombre}
                </Link>
                <div className="flex items-center gap-3 mt-2">
                  <span
                    className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-sm font-medium ${badge.bg} ${badge.text}`}
                  >
                    <BadgeIcon className="w-4 h-4" />
                    {badge.label}
                  </span>
                  {porVencer && (
                    <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-sm font-medium bg-amber-100 text-amber-700">
                      <AlertTriangle className="w-4 h-4" />
                      Vence en {dias} dia{dias !== 1 ? "s" : ""}
                    </span>
                  )}
                </div>
              </div>
            </div>

            {canEdit && (
              <div className="relative">
                <Button variant="outline" onClick={() => setMenuOpen(!menuOpen)}>
                  <MoreVertical className="w-4 h-4" />
                </Button>
                {menuOpen && (
                  <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-warm-200 py-1 z-10">
                    <Link
                      href={`/contratos/${contratoId}/editar`}
                      className="flex items-center gap-2 px-4 py-2 text-sm text-warm-700 hover:bg-warm-50"
                      onClick={() => setMenuOpen(false)}
                    >
                      <Edit className="w-4 h-4" />
                      Editar
                    </Link>
                    {contrato.estado === "vigente" && (
                      <button
                        type="button"
                        onClick={() => {
                          setMenuOpen(false);
                          setNuevaFechaInicio(contrato.fecha_fin || new Date().toISOString().split("T")[0]);
                          setShowRenovarModal(true);
                        }}
                        className="flex items-center gap-2 px-4 py-2 text-sm text-warm-700 hover:bg-warm-50 w-full text-left"
                      >
                        <RefreshCw className="w-4 h-4" />
                        Renovar
                      </button>
                    )}
                    {contrato.documento_url && (
                      <a
                        href={contrato.documento_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center gap-2 px-4 py-2 text-sm text-warm-700 hover:bg-warm-50"
                        onClick={() => setMenuOpen(false)}
                      >
                        <Download className="w-4 h-4" />
                        Descargar PDF
                      </a>
                    )}
                    <div className="border-t border-warm-100 my-1" />
                    {contrato.estado === "vigente" && (
                      <button
                        type="button"
                        onClick={() => {
                          setMenuOpen(false);
                          setShowTerminarModal(true);
                        }}
                        className="flex items-center gap-2 px-4 py-2 text-sm text-amber-600 hover:bg-amber-50 w-full text-left"
                      >
                        <XCircle className="w-4 h-4" />
                        Terminar contrato
                      </button>
                    )}
                    {(contrato.estado === "vencido" || contrato.estado === "terminado") && (
                      <button
                        type="button"
                        onClick={() => {
                          setMenuOpen(false);
                          if (confirm("¿Eliminar este contrato? Esta accion no se puede deshacer.")) {
                            eliminarMutation.mutate();
                          }
                        }}
                        className="flex items-center gap-2 px-4 py-2 text-sm text-red-600 hover:bg-red-50 w-full text-left"
                      >
                        <Trash2 className="w-4 h-4" />
                        Eliminar
                      </button>
                    )}
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Motivo de terminacion */}
          {contrato.estado === "terminado" && contrato.motivo_terminacion && (
            <div className="mt-4 p-3 bg-warm-50 border border-warm-200 rounded-lg">
              <p className="text-sm text-warm-700">
                <strong>Motivo de terminacion:</strong> {contrato.motivo_terminacion}
              </p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Grid de informacion */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Vigencia */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-lg">
              <Calendar className="w-5 h-5 text-horizon-600" />
              Vigencia
            </CardTitle>
          </CardHeader>
          <CardContent>
            <dl className="space-y-3">
              <div className="flex justify-between">
                <dt className="text-sm text-warm-500">Tipo de contrato</dt>
                <dd className="text-sm text-warm-900 font-medium">
                  {getTipoLabel(contrato.tipo_contrato)}
                </dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-sm text-warm-500">Fecha de inicio</dt>
                <dd className="text-sm text-warm-900">{formatDate(contrato.fecha_inicio)}</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-sm text-warm-500">Fecha de fin</dt>
                <dd className="text-sm text-warm-900">
                  {contrato.fecha_fin ? formatDate(contrato.fecha_fin) : "Indefinido"}
                </dd>
              </div>
              {contrato.fecha_firma && (
                <div className="flex justify-between">
                  <dt className="text-sm text-warm-500">Fecha de firma</dt>
                  <dd className="text-sm text-warm-900">{formatDate(contrato.fecha_firma)}</dd>
                </div>
              )}
              {contrato.jornada && (
                <div className="flex justify-between">
                  <dt className="text-sm text-warm-500">Jornada</dt>
                  <dd className="text-sm text-warm-900 capitalize">{contrato.jornada}</dd>
                </div>
              )}
              {contrato.horario && (
                <div className="flex justify-between">
                  <dt className="text-sm text-warm-500">Horario</dt>
                  <dd className="text-sm text-warm-900">{contrato.horario}</dd>
                </div>
              )}
            </dl>
          </CardContent>
        </Card>

        {/* Puesto */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-lg">
              <Briefcase className="w-5 h-5 text-horizon-600" />
              Puesto
            </CardTitle>
          </CardHeader>
          <CardContent>
            <dl className="space-y-3">
              {contrato.puesto && (
                <div className="flex justify-between">
                  <dt className="text-sm text-warm-500">Puesto</dt>
                  <dd className="text-sm text-warm-900 font-medium">{contrato.puesto}</dd>
                </div>
              )}
              {contrato.departamento && (
                <div className="flex justify-between">
                  <dt className="text-sm text-warm-500">Departamento</dt>
                  <dd className="text-sm text-warm-900">{contrato.departamento}</dd>
                </div>
              )}
              <div className="flex justify-between">
                <dt className="text-sm text-warm-500">Empresa</dt>
                <dd className="text-sm text-warm-900 flex items-center gap-1">
                  <Building2 className="w-4 h-4 text-warm-400" />
                  {contrato.empresa_nombre || empresaActual?.razon_social}
                </dd>
              </div>
            </dl>
          </CardContent>
        </Card>

        {/* Condiciones economicas */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-lg">
              <DollarSign className="w-5 h-5 text-horizon-600" />
              Condiciones economicas
            </CardTitle>
          </CardHeader>
          <CardContent>
            <dl className="space-y-3">
              {contrato.salario_mensual && (
                <div className="flex justify-between">
                  <dt className="text-sm text-warm-500">Salario mensual</dt>
                  <dd className="text-sm text-warm-900 font-semibold">
                    {formatCurrency(contrato.salario_mensual)}
                  </dd>
                </div>
              )}
              {contrato.salario_diario && (
                <div className="flex justify-between">
                  <dt className="text-sm text-warm-500">Salario diario</dt>
                  <dd className="text-sm text-warm-900">{formatCurrency(contrato.salario_diario)}</dd>
                </div>
              )}
              {!contrato.salario_mensual && !contrato.salario_diario && (
                <p className="text-sm text-warm-400">Sin informacion de salario registrada</p>
              )}
            </dl>
          </CardContent>
        </Card>

        {/* Empleado */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-lg">
              <User className="w-5 h-5 text-horizon-600" />
              Empleado
            </CardTitle>
          </CardHeader>
          <CardContent>
            <Link
              href={`/empleados/${contrato.empleado}`}
              className="flex items-center gap-3 p-3 rounded-lg border border-warm-100 hover:border-horizon-300 hover:bg-warm-50 transition-colors"
            >
              <div className="w-12 h-12 bg-horizon-100 rounded-full flex items-center justify-center text-horizon-700 font-semibold">
                {contrato.empleado_nombre?.charAt(0) || "?"}
              </div>
              <div>
                <p className="font-medium text-warm-900">{contrato.empleado_nombre}</p>
                <p className="text-sm text-warm-500">{contrato.puesto || "Ver perfil"}</p>
              </div>
            </Link>
          </CardContent>
        </Card>

        {/* Condiciones especiales */}
        {contrato.condiciones_especiales && (
          <Card className="lg:col-span-2">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-lg">
                <FileText className="w-5 h-5 text-horizon-600" />
                Condiciones especiales
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-warm-700 whitespace-pre-wrap">{contrato.condiciones_especiales}</p>
            </CardContent>
          </Card>
        )}

        {/* Historial de renovaciones */}
        {contrato.numero_renovaciones && contrato.numero_renovaciones > 0 && (
          <Card className="lg:col-span-2">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-lg">
                <RefreshCw className="w-5 h-5 text-horizon-600" />
                Informacion de renovacion
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-warm-700">
                Este contrato ha sido renovado {contrato.numero_renovaciones} vez
                {contrato.numero_renovaciones !== 1 ? "es" : ""}
                {contrato.contrato_anterior && (
                  <>
                    {" · "}
                    <Link
                      href={`/contratos/${contrato.contrato_anterior}`}
                      className="text-horizon-600 hover:text-horizon-700"
                    >
                      Ver contrato anterior
                    </Link>
                  </>
                )}
              </p>
            </CardContent>
          </Card>
        )}
      </div>

      {/* Documento del contrato */}
      <Card className="mt-6">
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-2 text-lg">
              <FileText className="w-5 h-5 text-horizon-600" />
              Documento del contrato
            </CardTitle>
            {canEdit && !contrato.documento_firmado_url && (
              <Button
                variant="outline"
                size="sm"
                onClick={() => setShowUploadModal(true)}
              >
                <Upload className="w-4 h-4 mr-1" />
                Subir contrato firmado
              </Button>
            )}
          </div>
        </CardHeader>
        <CardContent>
          {contrato.documento_firmado_url ? (
            <div className="border border-warm-200 rounded-lg p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 bg-red-100 rounded-lg flex items-center justify-center">
                    <FileText className="w-6 h-6 text-red-600" />
                  </div>
                  <div>
                    <p className="font-medium text-warm-900">Contrato firmado</p>
                    <p className="text-sm text-warm-500">
                      {contrato.fecha_firma ? `Firmado el ${formatDate(contrato.fecha_firma)}` : "Documento adjunto"}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <a
                    href={contrato.documento_firmado_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-1 px-3 py-1.5 text-sm font-medium text-warm-700 bg-warm-100 hover:bg-warm-200 rounded-lg transition-colors"
                  >
                    <Eye className="w-4 h-4" />
                    Ver
                  </a>
                  <a
                    href={contrato.documento_firmado_url}
                    download
                    className="inline-flex items-center gap-1 px-3 py-1.5 text-sm font-medium text-warm-700 bg-warm-100 hover:bg-warm-200 rounded-lg transition-colors"
                  >
                    <Download className="w-4 h-4" />
                    Descargar
                  </a>
                  {canEdit && (
                    <button
                      type="button"
                      onClick={() => {
                        if (confirm("¿Eliminar el documento del contrato?")) {
                          eliminarDocumentoMutation.mutate();
                        }
                      }}
                      className="inline-flex items-center gap-1 px-3 py-1.5 text-sm font-medium text-red-600 bg-red-50 hover:bg-red-100 rounded-lg transition-colors"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  )}
                </div>
              </div>

              {/* Preview/Info del archivo */}
              <div className="mt-4 p-4 bg-warm-50 rounded-lg">
                <div className="flex items-center justify-center gap-4">
                  <div className="text-center">
                    {contrato.documento_firmado_url?.toLowerCase().endsWith(".pdf") ? (
                      <>
                        <div className="w-16 h-16 bg-red-100 rounded-xl flex items-center justify-center mx-auto mb-2">
                          <FileText className="w-8 h-8 text-red-600" />
                        </div>
                        <p className="text-sm text-warm-600">Documento PDF</p>
                        <a
                          href={contrato.documento_firmado_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-horizon-600 hover:text-horizon-700 text-sm font-medium"
                        >
                          Abrir en nueva pestana →
                        </a>
                      </>
                    ) : (
                      <img
                        src={contrato.documento_firmado_url}
                        alt="Contrato firmado"
                        className="max-w-full max-h-96 rounded-lg border border-warm-200"
                      />
                    )}
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <div className="text-center py-8 border-2 border-dashed border-warm-200 rounded-lg">
              <FileText className="w-12 h-12 text-warm-300 mx-auto mb-2" />
              <p className="text-warm-500">No hay documento adjunto</p>
              {canEdit && (
                <button
                  type="button"
                  onClick={() => setShowUploadModal(true)}
                  className="text-horizon-600 hover:text-horizon-700 text-sm mt-2"
                >
                  Subir contrato firmado
                </button>
              )}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Modal Subir Documento */}
      {showUploadModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl max-w-md w-full p-6 shadow-xl">
            <h3 className="text-lg font-semibold text-warm-900 mb-2 flex items-center gap-2">
              <Upload className="w-5 h-5 text-horizon-600" />
              Subir contrato firmado
            </h3>
            <p className="text-sm text-warm-500 mb-4">
              Sube el PDF o imagen del contrato firmado para {contrato.empleado_nombre}
            </p>

            {uploadError && (
              <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-600">
                {uploadError}
              </div>
            )}

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-warm-700 mb-1">
                  Archivo *
                </label>
                <input
                  type="file"
                  onChange={(e) => {
                    setArchivoSeleccionado(e.target.files?.[0] || null);
                    setUploadError("");
                  }}
                  accept=".pdf,.jpg,.jpeg,.png"
                  className="w-full px-3 py-2 border border-warm-300 rounded-lg text-warm-900 bg-white file:mr-4 file:py-1 file:px-3 file:rounded file:border-0 file:bg-horizon-100 file:text-horizon-700 hover:file:bg-horizon-200"
                />
                <p className="text-xs text-warm-400 mt-1">PDF, JPG o PNG (max. 10MB)</p>
              </div>

              {archivoSeleccionado && (
                <div className="p-3 bg-warm-50 rounded-lg">
                  <p className="text-sm text-warm-700">
                    <strong>Archivo:</strong> {archivoSeleccionado.name}
                  </p>
                  <p className="text-xs text-warm-500">
                    Tamano: {(archivoSeleccionado.size / 1024 / 1024).toFixed(2)} MB
                  </p>
                </div>
              )}
            </div>

            <div className="flex gap-3 mt-6">
              <Button
                variant="outline"
                onClick={() => {
                  setShowUploadModal(false);
                  setArchivoSeleccionado(null);
                  setUploadError("");
                }}
                className="flex-1"
              >
                Cancelar
              </Button>
              <Button
                onClick={handleUploadArchivo}
                disabled={!archivoSeleccionado || subirDocumentoMutation.isPending}
                className="flex-1"
              >
                {subirDocumentoMutation.isPending ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Subiendo...
                  </>
                ) : (
                  "Subir contrato"
                )}
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* Modal Renovar */}
      {showRenovarModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl max-w-md w-full shadow-xl">
            <div className="p-6 border-b border-warm-200 flex items-center justify-between">
              <h3 className="text-lg font-semibold text-warm-900 flex items-center gap-2">
                <RefreshCw className="w-5 h-5 text-horizon-600" />
                Renovar contrato
              </h3>
              <button
                type="button"
                onClick={() => setShowRenovarModal(false)}
                className="text-warm-400 hover:text-warm-600"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            <div className="p-6">
              <p className="text-sm text-warm-500 mb-4">
                Se creara un nuevo contrato basado en este, marcando el actual como renovado.
              </p>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-warm-700 mb-1">
                    Fecha de inicio del nuevo contrato
                  </label>
                  <input
                    type="date"
                    value={nuevaFechaInicio}
                    onChange={(e) => setNuevaFechaInicio(e.target.value)}
                    className="w-full px-3 py-2 border border-warm-300 rounded-lg text-warm-900 bg-white focus:ring-2 focus:ring-horizon-500 focus:border-horizon-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-warm-700 mb-1">
                    Nueva fecha de fin
                  </label>
                  <input
                    type="date"
                    value={nuevaFechaFin}
                    onChange={(e) => setNuevaFechaFin(e.target.value)}
                    className="w-full px-3 py-2 border border-warm-300 rounded-lg text-warm-900 bg-white focus:ring-2 focus:ring-horizon-500 focus:border-horizon-500"
                  />
                  <p className="text-xs text-warm-400 mt-1">Dejar vacio para contrato indefinido</p>
                </div>
              </div>
            </div>
            <div className="p-6 border-t border-warm-200 flex gap-3">
              <Button variant="outline" onClick={() => setShowRenovarModal(false)} className="flex-1">
                Cancelar
              </Button>
              <Button
                onClick={() => renovarMutation.mutate()}
                disabled={renovarMutation.isPending || !nuevaFechaInicio}
                className="flex-1"
              >
                {renovarMutation.isPending ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Procesando...
                  </>
                ) : (
                  "Renovar"
                )}
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* Modal Terminar */}
      {showTerminarModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl max-w-md w-full shadow-xl">
            <div className="p-6 border-b border-warm-200 flex items-center justify-between">
              <h3 className="text-lg font-semibold text-warm-900 flex items-center gap-2">
                <XCircle className="w-5 h-5 text-amber-600" />
                Terminar contrato
              </h3>
              <button
                type="button"
                onClick={() => setShowTerminarModal(false)}
                className="text-warm-400 hover:text-warm-600"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            <div className="p-6">
              <p className="text-sm text-warm-500 mb-4">
                Esta accion marcara el contrato como terminado. No se puede deshacer.
              </p>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-warm-700 mb-1">
                    Fecha de terminacion
                  </label>
                  <input
                    type="date"
                    value={fechaTerminacion}
                    onChange={(e) => setFechaTerminacion(e.target.value)}
                    className="w-full px-3 py-2 border border-warm-300 rounded-lg text-warm-900 bg-white focus:ring-2 focus:ring-horizon-500 focus:border-horizon-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-warm-700 mb-1">
                    Motivo de terminacion
                  </label>
                  <textarea
                    value={motivoTerminacion}
                    onChange={(e) => setMotivoTerminacion(e.target.value)}
                    placeholder="Describe el motivo..."
                    rows={3}
                    className="w-full px-3 py-2 border border-warm-300 rounded-lg text-warm-900 bg-white placeholder:text-warm-400 focus:ring-2 focus:ring-horizon-500 focus:border-horizon-500 resize-none"
                  />
                </div>
              </div>
            </div>
            <div className="p-6 border-t border-warm-200 flex gap-3">
              <Button variant="outline" onClick={() => setShowTerminarModal(false)} className="flex-1">
                Cancelar
              </Button>
              <Button
                variant="danger"
                onClick={() => terminarMutation.mutate()}
                disabled={terminarMutation.isPending}
                className="flex-1"
              >
                {terminarMutation.isPending ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Procesando...
                  </>
                ) : (
                  "Confirmar terminacion"
                )}
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
