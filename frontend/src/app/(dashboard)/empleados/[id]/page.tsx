"use client";

import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import Link from "next/link";
import api from "@/lib/api";
import { useAuthStore } from "@/stores/auth-store";
import { formatDate, formatCurrency } from "@/lib/utils";
import { Avatar } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Empleado } from "@/types";
import {
  ArrowLeft,
  Edit,
  MoreVertical,
  User,
  FileText,
  Phone,
  MapPin,
  Briefcase,
  DollarSign,
  Users,
  Calendar,
  Building2,
  Mail,
  CreditCard,
  AlertTriangle,
  Loader2,
  UserX,
  Download,
  Plus,
  Trash2,
  Upload,
  X,
} from "lucide-react";

const estadoBadgeVariant: Record<string, "default" | "success" | "warning" | "error"> = {
  activo: "success",
  baja: "error",
  incapacidad: "warning",
};

export default function EmpleadoDetallePage() {
  const params = useParams();
  const router = useRouter();
  const queryClient = useQueryClient();
  const { user } = useAuthStore();
  const [mounted, setMounted] = useState(false);
  const [showEstadoModal, setShowEstadoModal] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);

  // Estados para el modal de cambio de estado
  const [nuevoEstado, setNuevoEstado] = useState("");
  const [fechaCambio, setFechaCambio] = useState(new Date().toISOString().split("T")[0]);
  const [tipoBaja, setTipoBaja] = useState("");
  const [motivoCambio, setMotivoCambio] = useState("");

  // Estados para modal de subir documento
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [uploadingFile, setUploadingFile] = useState<File | null>(null);
  const [docTipo, setDocTipo] = useState("");
  const [docNombre, setDocNombre] = useState("");

  const empleadoId = params.id as string;

  useEffect(() => {
    setMounted(true);
  }, []);

  const { data: empleado, isLoading, error } = useQuery<Empleado>({
    queryKey: ["empleado", empleadoId],
    queryFn: async () => {
      const response = await api.get(`/empleados/${empleadoId}/`);
      return response.data;
    },
    enabled: mounted && !!empleadoId,
  });

  // Query para documentos del empleado
  interface DocumentoEmpleado {
    id: string;
    tipo: string;
    tipo_display: string;
    nombre: string;
    archivo: string;
    archivo_url: string;
    fecha_documento?: string;
    fecha_vencimiento?: string;
    estatus: string;
    estatus_display: string;
    created_at: string;
  }

  const { data: documentos, isLoading: loadingDocs } = useQuery<DocumentoEmpleado[]>({
    queryKey: ["empleado-documentos", empleadoId],
    queryFn: async () => {
      const response = await api.get(`/empleados/${empleadoId}/documentos/`);
      return response.data;
    },
    enabled: mounted && !!empleadoId,
  });

  // Mutation para subir documento
  const subirDocumentoMutation = useMutation({
    mutationFn: async () => {
      if (!uploadingFile) throw new Error("No hay archivo seleccionado");

      const formData = new FormData();
      formData.append("archivo", uploadingFile);
      formData.append("tipo", docTipo);
      formData.append("nombre", docNombre || uploadingFile.name);

      const response = await api.post(`/empleados/${empleadoId}/documentos/`, formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["empleado-documentos", empleadoId] });
      setShowUploadModal(false);
      setUploadingFile(null);
      setDocTipo("");
      setDocNombre("");
    },
  });

  // Mutation para eliminar documento
  const eliminarDocumentoMutation = useMutation({
    mutationFn: async (docId: string) => {
      // URL correcta: incluir empleadoId en la ruta
      await api.delete(`/empleados/${empleadoId}/documentos/${docId}/`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["empleado-documentos", empleadoId] });
    },
  });

  // Mutation para cambiar estado
  const cambiarEstadoMutation = useMutation({
    mutationFn: async () => {
      const data: Record<string, unknown> = {
        estado: nuevoEstado,
      };

      if (nuevoEstado === "baja") {
        data.fecha_baja = fechaCambio;
        data.tipo_baja = tipoBaja;
        data.motivo_baja = motivoCambio;
      } else if (nuevoEstado === "activo") {
        // Limpiar datos de baja al reactivar
        data.fecha_baja = null;
        data.tipo_baja = "";
        data.motivo_baja = "";
      }

      const response = await api.patch(`/empleados/${empleadoId}/`, data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["empleado", empleadoId] });
      queryClient.invalidateQueries({ queryKey: ["empleados"] });
      setShowEstadoModal(false);
      setNuevoEstado("");
      setTipoBaja("");
      setMotivoCambio("");
    },
  });

  const canEdit = user?.rol === "admin" || user?.rol === "rrhh" || user?.rol === "empleador";

  if (!mounted) return null;

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <Loader2 className="w-8 h-8 animate-spin text-horizon-500" />
      </div>
    );
  }

  if (error || !empleado) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] text-center">
        <AlertTriangle className="w-16 h-16 text-amber-500 mb-4" />
        <h1 className="text-xl font-semibold text-warm-900">Empleado no encontrado</h1>
        <p className="text-warm-500 mt-2">El empleado que buscas no existe o no tienes acceso.</p>
        <Link href="/empleados">
          <Button variant="outline" className="mt-4">
            Volver a empleados
          </Button>
        </Link>
      </div>
    );
  }

  const getNombreCompleto = () => {
    if (empleado.nombre_completo) return empleado.nombre_completo;
    const partes = [empleado.nombre, empleado.apellido_paterno, empleado.apellido_materno].filter(Boolean);
    return partes.join(" ") || "Sin nombre";
  };

  return (
    <div className="max-w-5xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <Link
          href="/empleados"
          className="inline-flex items-center text-sm text-warm-500 hover:text-warm-700 mb-4"
        >
          <ArrowLeft className="w-4 h-4 mr-1" />
          Volver a empleados
        </Link>

        <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4">
          <div className="flex items-start gap-4">
            <Avatar name={getNombreCompleto()} src={empleado.foto} size="xl" />
            <div>
              <h1 className="text-2xl font-display font-semibold text-warm-900">
                {getNombreCompleto()}
              </h1>
              <p className="text-warm-500">{empleado.puesto || "Sin puesto asignado"}</p>
              <div className="flex items-center gap-2 mt-2">
                <Badge
                  variant={estadoBadgeVariant[empleado.estado] || "default"}
                  className={
                    empleado.estado === "baja"
                      ? "bg-red-100 text-red-800 border-red-300 px-3 py-1"
                      : empleado.estado === "incapacidad"
                      ? "bg-amber-100 text-amber-800 border-amber-300 px-3 py-1"
                      : empleado.estado === "activo"
                      ? "bg-green-100 text-green-800 border-green-300 px-3 py-1"
                      : ""
                  }
                >
                  {empleado.estado === "activo" ? "Activo" :
                   empleado.estado === "baja" ? "Dado de baja" :
                   empleado.estado === "incapacidad" ? "En incapacidad" :
                   String(empleado.estado).charAt(0).toUpperCase() + String(empleado.estado).slice(1)}
                </Badge>
                {empleado.departamento && (
                  <span className="text-sm text-warm-500">{empleado.departamento}</span>
                )}
              </div>
            </div>
          </div>

          {canEdit && (
            <div className="flex gap-2 relative">
              <Link href={`/empleados/${empleadoId}/editar`}>
                <Button variant="outline">
                  <Edit className="w-4 h-4 mr-2" />
                  Editar
                </Button>
              </Link>
              <div className="relative">
                <Button
                  variant="outline"
                  onClick={() => setMenuOpen(!menuOpen)}
                >
                  <MoreVertical className="w-4 h-4" />
                </Button>
                {menuOpen && (
                  <div className="absolute right-0 mt-2 w-52 bg-white rounded-lg shadow-lg border border-warm-200 py-1 z-10">
                    <button
                      onClick={() => {
                        setMenuOpen(false);
                        setNuevoEstado("");
                        setShowEstadoModal(true);
                      }}
                      className="w-full px-4 py-2 text-left text-sm text-warm-700 hover:bg-warm-50 flex items-center gap-2"
                    >
                      <Users className="w-4 h-4" />
                      Cambiar estado
                    </button>
                    {empleado.estado === "activo" && (
                      <>
                        <button
                          onClick={() => {
                            setMenuOpen(false);
                            setNuevoEstado("incapacidad");
                            setShowEstadoModal(true);
                          }}
                          className="w-full px-4 py-2 text-left text-sm text-amber-600 hover:bg-amber-50 flex items-center gap-2"
                        >
                          <AlertTriangle className="w-4 h-4" />
                          Registrar incapacidad
                        </button>
                        <button
                          onClick={() => {
                            setMenuOpen(false);
                            setNuevoEstado("baja");
                            setShowEstadoModal(true);
                          }}
                          className="w-full px-4 py-2 text-left text-sm text-red-600 hover:bg-red-50 flex items-center gap-2"
                        >
                          <UserX className="w-4 h-4" />
                          Dar de baja
                        </button>
                      </>
                    )}
                    {(empleado.estado === "baja" || empleado.estado === "incapacidad") && (
                      <button
                        onClick={() => {
                          setMenuOpen(false);
                          setNuevoEstado("activo");
                          setShowEstadoModal(true);
                        }}
                        className="w-full px-4 py-2 text-left text-sm text-green-600 hover:bg-green-50 flex items-center gap-2"
                      >
                        <User className="w-4 h-4" />
                        Reactivar empleado
                      </button>
                    )}
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Contenido */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Columna principal */}
        <div className="lg:col-span-2 space-y-6">
          {/* Datos personales */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-lg">
                <User className="w-5 h-5 text-horizon-600" />
                Datos personales
              </CardTitle>
            </CardHeader>
            <CardContent>
              <dl className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <dt className="text-warm-500">Nombre completo</dt>
                  <dd className="font-medium text-warm-900">{getNombreCompleto()}</dd>
                </div>
                <div>
                  <dt className="text-warm-500">Fecha de nacimiento</dt>
                  <dd className="font-medium text-warm-900">{formatDate(empleado.fecha_nacimiento)}</dd>
                </div>
                <div>
                  <dt className="text-warm-500">Genero</dt>
                  <dd className="font-medium text-warm-900">
                    {empleado.genero === "M" ? "Masculino" : empleado.genero === "F" ? "Femenino" : empleado.genero || "-"}
                  </dd>
                </div>
                <div>
                  <dt className="text-warm-500">Estado civil</dt>
                  <dd className="font-medium text-warm-900 capitalize">{empleado.estado_civil || "-"}</dd>
                </div>
              </dl>
            </CardContent>
          </Card>

          {/* Documentos */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-lg">
                <FileText className="w-5 h-5 text-horizon-600" />
                Documentos oficiales
              </CardTitle>
            </CardHeader>
            <CardContent>
              <dl className="grid grid-cols-2 md:grid-cols-3 gap-4 text-sm">
                <div>
                  <dt className="text-warm-500">RFC</dt>
                  <dd className="font-medium text-warm-900 font-mono">{empleado.rfc || "-"}</dd>
                </div>
                <div>
                  <dt className="text-warm-500">CURP</dt>
                  <dd className="font-medium text-warm-900 font-mono text-xs">{empleado.curp || "-"}</dd>
                </div>
                <div>
                  <dt className="text-warm-500">NSS (IMSS)</dt>
                  <dd className="font-medium text-warm-900 font-mono">{empleado.nss_imss || "-"}</dd>
                </div>
              </dl>
            </CardContent>
          </Card>

          {/* Contacto */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-lg">
                <Phone className="w-5 h-5 text-horizon-600" />
                Contacto
              </CardTitle>
            </CardHeader>
            <CardContent>
              <dl className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <dt className="text-warm-500">Email personal</dt>
                  <dd className="font-medium text-warm-900">{empleado.email_personal || "-"}</dd>
                </div>
                <div>
                  <dt className="text-warm-500">Email corporativo</dt>
                  <dd className="font-medium text-warm-900">{empleado.email_corporativo || "-"}</dd>
                </div>
                <div>
                  <dt className="text-warm-500">Telefono</dt>
                  <dd className="font-medium text-warm-900">{empleado.telefono_personal || "-"}</dd>
                </div>
                {empleado.emergencia_nombre && (
                  <div className="col-span-2 pt-2 border-t border-warm-100">
                    <dt className="text-warm-500 mb-1">Contacto de emergencia</dt>
                    <dd className="font-medium text-warm-900">
                      {empleado.emergencia_nombre}
                      {empleado.emergencia_parentesco && ` (${empleado.emergencia_parentesco})`}
                      {empleado.emergencia_telefono && ` - ${empleado.emergencia_telefono}`}
                    </dd>
                  </div>
                )}
              </dl>
            </CardContent>
          </Card>

          {/* Direccion */}
          {(empleado.direccion_calle || empleado.direccion_colonia) && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-lg">
                  <MapPin className="w-5 h-5 text-horizon-600" />
                  Direccion
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-warm-900">
                  {[
                    empleado.direccion_calle,
                    empleado.direccion_numero && `#${empleado.direccion_numero}`,
                  ].filter(Boolean).join(" ")}
                </p>
                <p className="text-warm-500 text-sm">
                  {[
                    empleado.direccion_colonia,
                    empleado.direccion_cp && `C.P. ${empleado.direccion_cp}`,
                  ].filter(Boolean).join(", ")}
                </p>
                <p className="text-warm-500 text-sm">
                  {[empleado.direccion_municipio, empleado.direccion_estado].filter(Boolean).join(", ")}
                </p>
              </CardContent>
            </Card>
          )}
        </div>

        {/* Columna lateral */}
        <div className="space-y-6">
          {/* Datos laborales */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-lg">
                <Briefcase className="w-5 h-5 text-horizon-600" />
                Datos laborales
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center gap-3">
                <Building2 className="w-4 h-4 text-warm-400" />
                <div>
                  <p className="text-xs text-warm-500">Empresa</p>
                  <p className="font-medium text-warm-900">{empleado.empresa_nombre || "-"}</p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <Calendar className="w-4 h-4 text-warm-400" />
                <div>
                  <p className="text-xs text-warm-500">Fecha de ingreso</p>
                  <p className="font-medium text-warm-900">{formatDate(empleado.fecha_ingreso)}</p>
                </div>
              </div>
              {empleado.antiguedad_anos !== undefined && (
                <div className="flex items-center gap-3">
                  <Users className="w-4 h-4 text-warm-400" />
                  <div>
                    <p className="text-xs text-warm-500">Antiguedad</p>
                    <p className="font-medium text-warm-900">
                      {empleado.antiguedad_anos} {empleado.antiguedad_anos === 1 ? "año" : "años"}
                    </p>
                  </div>
                </div>
              )}
              <div className="pt-2 border-t border-warm-100 space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-warm-500">Tipo de contrato</span>
                  <span className="font-medium text-warm-900 capitalize">
                    {empleado.tipo_contrato?.replace("_", " ") || "-"}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-warm-500">Jornada</span>
                  <span className="font-medium text-warm-900 capitalize">{empleado.jornada || "-"}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-warm-500">Modalidad</span>
                  <span className="font-medium text-warm-900 capitalize">{empleado.modalidad || "-"}</span>
                </div>
              </div>
              {empleado.jefe_directo_nombre && (
                <div className="pt-2 border-t border-warm-100">
                  <p className="text-xs text-warm-500">Reporta a</p>
                  <p className="font-medium text-warm-900">{empleado.jefe_directo_nombre}</p>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Salario */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-lg">
                <DollarSign className="w-5 h-5 text-horizon-600" />
                Salario
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div>
                <p className="text-xs text-warm-500">Salario diario</p>
                <p className="text-xl font-semibold text-warm-900">
                  {formatCurrency(empleado.salario_diario)}
                </p>
              </div>
              <div>
                <p className="text-xs text-warm-500">Salario mensual</p>
                <p className="text-lg font-medium text-warm-700">
                  {formatCurrency(empleado.salario_mensual)}
                </p>
              </div>
            </CardContent>
          </Card>

          {/* Datos bancarios */}
          {(empleado.banco || empleado.clabe) && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-lg">
                  <CreditCard className="w-5 h-5 text-horizon-600" />
                  Datos bancarios
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-warm-500">Banco</span>
                  <span className="font-medium text-warm-900">{empleado.banco || "-"}</span>
                </div>
                {empleado.clabe && (
                  <div>
                    <p className="text-warm-500">CLABE</p>
                    <p className="font-mono text-warm-900 text-xs">{empleado.clabe}</p>
                  </div>
                )}
              </CardContent>
            </Card>
          )}

          {/* Info de baja si aplica */}
          {empleado.estado === "baja" && empleado.fecha_baja && (
            <Card className="border-red-200 bg-red-50">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-lg text-red-800">
                  <UserX className="w-5 h-5" />
                  Informacion de baja
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-red-600">Fecha de baja</span>
                  <span className="font-medium text-red-800">{formatDate(empleado.fecha_baja)}</span>
                </div>
                {empleado.tipo_baja && (
                  <div className="flex justify-between">
                    <span className="text-red-600">Tipo</span>
                    <span className="font-medium text-red-800 capitalize">
                      {empleado.tipo_baja.replace("_", " ")}
                    </span>
                  </div>
                )}
                {empleado.motivo_baja && (
                  <div className="pt-2 border-t border-red-200">
                    <p className="text-red-600">Motivo</p>
                    <p className="text-red-800">{empleado.motivo_baja}</p>
                  </div>
                )}
              </CardContent>
            </Card>
          )}
        </div>
      </div>

      {/* Documentos del empleado */}
      <Card className="mt-6">
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-2 text-lg">
              <FileText className="w-5 h-5 text-horizon-600" />
              Expediente digital
            </CardTitle>
            {canEdit && (
              <Button
                variant="outline"
                size="sm"
                onClick={() => setShowUploadModal(true)}
              >
                <Plus className="w-4 h-4 mr-1" />
                Subir documento
              </Button>
            )}
          </div>
        </CardHeader>
        <CardContent>
          {loadingDocs ? (
            <div className="flex justify-center py-8">
              <Loader2 className="w-6 h-6 animate-spin text-warm-400" />
            </div>
          ) : documentos && documentos.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
              {documentos.map((doc) => (
                <div
                  key={doc.id}
                  className="border border-warm-200 rounded-lg p-3 hover:border-horizon-300 transition-colors group"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex items-center gap-2 min-w-0 flex-1">
                      <div className="w-10 h-10 bg-horizon-100 rounded-lg flex items-center justify-center flex-shrink-0">
                        <FileText className="w-5 h-5 text-horizon-600" />
                      </div>
                      <div className="min-w-0 flex-1">
                        <p className="font-medium text-warm-900 text-sm truncate" title={doc.nombre}>
                          {doc.nombre}
                        </p>
                        <p className="text-xs text-warm-500">{doc.tipo_display}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                      <a
                        href={doc.archivo_url || doc.archivo}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="p-1 text-horizon-600 hover:text-horizon-700 hover:bg-horizon-50 rounded"
                        title="Descargar"
                      >
                        <Download className="w-4 h-4" />
                      </a>
                      {canEdit && (
                        <button
                          type="button"
                          onClick={() => {
                            if (confirm("¿Eliminar este documento?")) {
                              eliminarDocumentoMutation.mutate(doc.id);
                            }
                          }}
                          className="p-1 text-red-500 hover:text-red-700 hover:bg-red-50 rounded"
                          title="Eliminar"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      )}
                    </div>
                  </div>
                  {doc.fecha_vencimiento && (
                    <p className="text-xs text-warm-400 mt-2">
                      Vigencia: {formatDate(doc.fecha_vencimiento)}
                    </p>
                  )}
                  <p className="text-xs text-warm-400 mt-1">
                    {formatDate(doc.created_at)}
                  </p>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <FileText className="w-12 h-12 text-warm-300 mx-auto mb-2" />
              <p className="text-warm-500">No hay documentos en el expediente</p>
              {canEdit && (
                <button
                  type="button"
                  onClick={() => setShowUploadModal(true)}
                  className="text-horizon-600 hover:text-horizon-700 text-sm mt-2"
                >
                  Subir primer documento
                </button>
              )}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Modal de cambio de estado */}
      {showEstadoModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl shadow-xl max-w-md w-full">
            <div className="p-6 border-b border-warm-200">
              <h2 className="text-lg font-semibold text-warm-900 flex items-center gap-2">
                {nuevoEstado === "baja" ? (
                  <>
                    <UserX className="w-5 h-5 text-red-500" />
                    Dar de baja al empleado
                  </>
                ) : nuevoEstado === "activo" ? (
                  <>
                    <User className="w-5 h-5 text-green-500" />
                    Reactivar empleado
                  </>
                ) : (
                  <>
                    <Users className="w-5 h-5 text-horizon-500" />
                    Cambiar estado del empleado
                  </>
                )}
              </h2>
            </div>
            <div className="p-6 space-y-4">
              {/* Selector de estado (solo si no viene preseleccionado) */}
              {!nuevoEstado && (
                <div>
                  <label className="block text-sm font-medium text-warm-700 mb-1">
                    Nuevo estado
                  </label>
                  <select
                    value={nuevoEstado}
                    onChange={(e) => setNuevoEstado(e.target.value)}
                    className="w-full rounded-md border border-warm-300 px-3 py-2 text-sm text-warm-900 bg-white focus:border-horizon-500 focus:outline-none focus:ring-1 focus:ring-horizon-500"
                  >
                    <option value="">Seleccionar estado...</option>
                    {empleado.estado !== "activo" && (
                      <option value="activo">Activo</option>
                    )}
                    {empleado.estado !== "baja" && (
                      <option value="baja">Baja</option>
                    )}
                    {empleado.estado !== "incapacidad" && (
                      <option value="incapacidad">Incapacidad</option>
                    )}
                  </select>
                </div>
              )}

              {/* Mensaje de confirmacion para reactivar */}
              {nuevoEstado === "activo" && (
                <div className="p-4 bg-green-50 rounded-lg border border-green-200">
                  <p className="text-sm text-green-800">
                    El empleado sera reactivado y podra volver a trabajar normalmente.
                    Se eliminaran los datos de baja anteriores.
                  </p>
                </div>
              )}

              {/* Campos para baja */}
              {nuevoEstado === "baja" && (
                <>
                  <div>
                    <label className="block text-sm font-medium text-warm-700 mb-1">
                      Fecha de baja
                    </label>
                    <input
                      type="date"
                      value={fechaCambio}
                      onChange={(e) => setFechaCambio(e.target.value)}
                      className="w-full rounded-md border border-warm-300 px-3 py-2 text-sm text-warm-900 bg-white focus:border-horizon-500 focus:outline-none focus:ring-1 focus:ring-horizon-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-warm-700 mb-1">
                      Tipo de baja
                    </label>
                    <select
                      value={tipoBaja}
                      onChange={(e) => setTipoBaja(e.target.value)}
                      className="w-full rounded-md border border-warm-300 px-3 py-2 text-sm text-warm-900 bg-white focus:border-horizon-500 focus:outline-none focus:ring-1 focus:ring-horizon-500"
                    >
                      <option value="">Seleccionar tipo...</option>
                      <option value="renuncia_voluntaria">Renuncia voluntaria</option>
                      <option value="despido_justificado">Despido justificado</option>
                      <option value="despido_injustificado">Despido injustificado</option>
                      <option value="termino_contrato">Termino de contrato</option>
                      <option value="jubilacion">Jubilacion</option>
                      <option value="fallecimiento">Fallecimiento</option>
                      <option value="mutuo_acuerdo">Mutuo acuerdo</option>
                      <option value="otro">Otro</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-warm-700 mb-1">
                      Motivo (opcional)
                    </label>
                    <textarea
                      value={motivoCambio}
                      onChange={(e) => setMotivoCambio(e.target.value)}
                      rows={3}
                      placeholder="Describe el motivo de la baja..."
                      className="w-full rounded-md border border-warm-300 px-3 py-2 text-sm text-warm-900 bg-white placeholder:text-warm-400 focus:border-horizon-500 focus:outline-none focus:ring-1 focus:ring-horizon-500"
                    />
                  </div>
                </>
              )}

              {/* Campos para incapacidad */}
              {nuevoEstado === "incapacidad" && (
                <div className="p-4 bg-amber-50 rounded-lg border border-amber-200">
                  <p className="text-sm text-amber-800">
                    El empleado sera marcado como en incapacidad.
                    Podras gestionar los detalles de la incapacidad desde el modulo de incidencias.
                  </p>
                </div>
              )}
            </div>
            <div className="p-6 border-t border-warm-200 flex justify-end gap-3">
              <Button
                variant="outline"
                onClick={() => {
                  setShowEstadoModal(false);
                  setNuevoEstado("");
                  setTipoBaja("");
                  setMotivoCambio("");
                }}
                disabled={cambiarEstadoMutation.isPending}
              >
                Cancelar
              </Button>
              <Button
                variant={nuevoEstado === "baja" ? "danger" : nuevoEstado === "activo" ? "success" : "primary"}
                onClick={() => cambiarEstadoMutation.mutate()}
                disabled={
                  cambiarEstadoMutation.isPending ||
                  !nuevoEstado ||
                  (nuevoEstado === "baja" && (!fechaCambio || !tipoBaja))
                }
              >
                {cambiarEstadoMutation.isPending ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Procesando...
                  </>
                ) : nuevoEstado === "baja" ? (
                  "Confirmar baja"
                ) : nuevoEstado === "activo" ? (
                  "Reactivar empleado"
                ) : (
                  "Cambiar estado"
                )}
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* Modal de subir documento */}
      {showUploadModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl shadow-xl max-w-md w-full">
            <div className="p-6 border-b border-warm-200 flex items-center justify-between">
              <h2 className="text-lg font-semibold text-warm-900 flex items-center gap-2">
                <Upload className="w-5 h-5 text-horizon-600" />
                Subir documento
              </h2>
              <button
                type="button"
                onClick={() => {
                  setShowUploadModal(false);
                  setUploadingFile(null);
                  setDocTipo("");
                  setDocNombre("");
                }}
                className="text-warm-400 hover:text-warm-600"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            <div className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-medium text-warm-700 mb-1">
                  Tipo de documento *
                </label>
                <select
                  value={docTipo}
                  onChange={(e) => setDocTipo(e.target.value)}
                  className="w-full rounded-md border border-warm-300 px-3 py-2 text-sm text-warm-900 bg-white focus:border-horizon-500 focus:outline-none focus:ring-1 focus:ring-horizon-500"
                >
                  <option value="">Seleccionar tipo...</option>
                  <option value="ine">INE / Identificacion oficial</option>
                  <option value="curp">CURP</option>
                  <option value="rfc">Constancia RFC</option>
                  <option value="nss">Numero de Seguro Social</option>
                  <option value="comprobante_domicilio">Comprobante de domicilio</option>
                  <option value="acta_nacimiento">Acta de nacimiento</option>
                  <option value="contrato">Contrato laboral</option>
                  <option value="alta_imss">Alta IMSS</option>
                  <option value="mod_salario">Modificacion de salario IMSS</option>
                  <option value="carta_renuncia">Carta de renuncia</option>
                  <option value="finiquito">Finiquito</option>
                  <option value="constancia">Constancia laboral</option>
                  <option value="incapacidad">Incapacidad IMSS</option>
                  <option value="recibo">Recibo de nomina</option>
                  <option value="cfdi">CFDI Nomina</option>
                  <option value="evaluacion">Evaluacion de desempeño</option>
                  <option value="capacitacion">Constancia de capacitacion</option>
                  <option value="otro">Otro</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-warm-700 mb-1">
                  Nombre del documento
                </label>
                <input
                  type="text"
                  value={docNombre}
                  onChange={(e) => setDocNombre(e.target.value)}
                  placeholder="Ej: INE Juan Perez 2024"
                  className="w-full rounded-md border border-warm-300 px-3 py-2 text-sm text-warm-900 bg-white placeholder:text-warm-400 focus:border-horizon-500 focus:outline-none focus:ring-1 focus:ring-horizon-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-warm-700 mb-1">
                  Archivo *
                </label>
                {uploadingFile ? (
                  <div className="flex items-center gap-2 p-3 bg-warm-50 rounded-md border border-warm-200">
                    <FileText className="w-5 h-5 text-horizon-600" />
                    <span className="text-sm text-warm-700 truncate flex-1">
                      {uploadingFile.name}
                    </span>
                    <button
                      type="button"
                      onClick={() => setUploadingFile(null)}
                      className="text-warm-400 hover:text-warm-600"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  </div>
                ) : (
                  <label className="flex flex-col items-center justify-center w-full h-32 border-2 border-dashed border-warm-300 rounded-lg cursor-pointer hover:border-horizon-400 hover:bg-warm-50 transition-colors">
                    <Upload className="w-8 h-8 text-warm-400 mb-2" />
                    <span className="text-sm text-warm-500">
                      Haz clic para seleccionar archivo
                    </span>
                    <span className="text-xs text-warm-400 mt-1">
                      PDF, JPG, PNG (max. 10MB)
                    </span>
                    <input
                      type="file"
                      className="hidden"
                      accept=".pdf,.jpg,.jpeg,.png,.doc,.docx"
                      onChange={(e) => {
                        const file = e.target.files?.[0];
                        if (file) {
                          setUploadingFile(file);
                          if (!docNombre) {
                            setDocNombre(file.name.replace(/\.[^/.]+$/, ""));
                          }
                        }
                      }}
                    />
                  </label>
                )}
              </div>
            </div>
            <div className="p-6 border-t border-warm-200 flex justify-end gap-3">
              <Button
                variant="outline"
                onClick={() => {
                  setShowUploadModal(false);
                  setUploadingFile(null);
                  setDocTipo("");
                  setDocNombre("");
                }}
                disabled={subirDocumentoMutation.isPending}
              >
                Cancelar
              </Button>
              <Button
                onClick={() => subirDocumentoMutation.mutate()}
                disabled={subirDocumentoMutation.isPending || !uploadingFile || !docTipo}
              >
                {subirDocumentoMutation.isPending ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Subiendo...
                  </>
                ) : (
                  <>
                    <Upload className="w-4 h-4 mr-2" />
                    Subir documento
                  </>
                )}
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
