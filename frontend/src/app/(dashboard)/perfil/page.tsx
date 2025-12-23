"use client";

import { useState, useEffect } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { usuariosApi } from "@/lib/api";
import { UsuarioPerfil } from "@/types/usuario";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import {
  User,
  Mail,
  Building2,
  Shield,
  Calendar,
  Lock,
  Save,
  Loader2,
  CheckCircle2,
  AlertCircle,
  Bell,
  BellOff,
  Briefcase,
} from "lucide-react";

export default function PerfilPage() {
  const queryClient = useQueryClient();
  const [isEditing, setIsEditing] = useState(false);
  const [showPasswordForm, setShowPasswordForm] = useState(false);
  const [nombre, setNombre] = useState("");
  const [apellido, setApellido] = useState("");
  const [notificacionesEmail, setNotificacionesEmail] = useState(true);
  const [notificacionesPush, setNotificacionesPush] = useState(true);
  const [passwordActual, setPasswordActual] = useState("");
  const [passwordNuevo, setPasswordNuevo] = useState("");
  const [passwordConfirmacion, setPasswordConfirmacion] = useState("");
  const [mensaje, setMensaje] = useState<{
    tipo: "success" | "error";
    texto: string;
  } | null>(null);

  const { data: perfil, isLoading } = useQuery<UsuarioPerfil>({
    queryKey: ["perfil"],
    queryFn: usuariosApi.getPerfil,
  });

  // Sincronizar estado local cuando llegan los datos
  useEffect(() => {
    if (perfil) {
      setNombre(perfil.nombre || "");
      setApellido(perfil.apellido || "");
      setNotificacionesEmail(perfil.notificaciones_email ?? true);
      setNotificacionesPush(perfil.notificaciones_push ?? true);
    }
  }, [perfil]);

  const actualizarMutation = useMutation({
    mutationFn: usuariosApi.actualizarPerfil,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["perfil"] });
      setIsEditing(false);
      setMensaje({ tipo: "success", texto: "Perfil actualizado correctamente" });
      setTimeout(() => setMensaje(null), 3000);
    },
    onError: () => {
      setMensaje({ tipo: "error", texto: "Error al actualizar perfil" });
    },
  });

  const passwordMutation = useMutation({
    mutationFn: usuariosApi.cambiarPassword,
    onSuccess: () => {
      setShowPasswordForm(false);
      setPasswordActual("");
      setPasswordNuevo("");
      setPasswordConfirmacion("");
      setMensaje({
        tipo: "success",
        texto: "Contrasena cambiada correctamente",
      });
      setTimeout(() => setMensaje(null), 3000);
    },
    onError: (error: any) => {
      const errorMsg =
        error.response?.data?.error ||
        error.response?.data?.detail ||
        "Error al cambiar contrasena";
      setMensaje({ tipo: "error", texto: errorMsg });
    },
  });

  const handleGuardarPerfil = () => {
    actualizarMutation.mutate({
      first_name: nombre,
      last_name: apellido,
      notificaciones_email: notificacionesEmail,
      notificaciones_push: notificacionesPush,
    });
  };

  const handleCambiarPassword = () => {
    if (passwordNuevo !== passwordConfirmacion) {
      setMensaje({ tipo: "error", texto: "Las contrasenas no coinciden" });
      return;
    }
    if (passwordNuevo.length < 8) {
      setMensaje({
        tipo: "error",
        texto: "La contrasena debe tener al menos 8 caracteres",
      });
      return;
    }
    passwordMutation.mutate({
      password_actual: passwordActual,
      password_nuevo: passwordNuevo,
    });
  };

  const getRolColor = (rol: string) => {
    switch (rol) {
      case "administrador":
        return "bg-purple-100 text-purple-800";
      case "empleador":
        return "bg-blue-100 text-blue-800";
      case "empleado":
        return "bg-green-100 text-green-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Loader2 className="h-8 w-8 animate-spin text-horizon-600" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-gray-900">Mi Perfil</h1>
        <p className="text-gray-500 mt-1">
          Administra tu informacion personal y seguridad
        </p>
      </div>

      {/* Mensaje de feedback */}
      {mensaje && (
        <div
          className={`flex items-center gap-2 p-4 rounded-lg ${
            mensaje.tipo === "success"
              ? "bg-green-50 text-green-800"
              : "bg-red-50 text-red-800"
          }`}
        >
          {mensaje.tipo === "success" ? (
            <CheckCircle2 className="h-5 w-5" />
          ) : (
            <AlertCircle className="h-5 w-5" />
          )}
          <span>{mensaje.texto}</span>
        </div>
      )}

      <div className="grid gap-6 md:grid-cols-2">
        {/* Informacion Personal */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <User className="h-5 w-5" />
              Informacion Personal
            </CardTitle>
            <CardDescription>Tu informacion basica de cuenta</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {isEditing ? (
              <>
                <div>
                  <label className="text-sm font-medium text-gray-700">
                    Nombre
                  </label>
                  <Input
                    value={nombre}
                    onChange={(e) => setNombre(e.target.value)}
                    className="mt-1"
                  />
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-700">
                    Apellido
                  </label>
                  <Input
                    value={apellido}
                    onChange={(e) => setApellido(e.target.value)}
                    className="mt-1"
                  />
                </div>
                <div className="space-y-3 pt-2">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Bell className="h-4 w-4 text-gray-500" />
                      <Label htmlFor="notif-email">Notificaciones por email</Label>
                    </div>
                    <Switch
                      id="notif-email"
                      checked={notificacionesEmail}
                      onCheckedChange={setNotificacionesEmail}
                    />
                  </div>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <BellOff className="h-4 w-4 text-gray-500" />
                      <Label htmlFor="notif-push">Notificaciones push</Label>
                    </div>
                    <Switch
                      id="notif-push"
                      checked={notificacionesPush}
                      onCheckedChange={setNotificacionesPush}
                    />
                  </div>
                </div>
                <div className="flex gap-2 pt-2">
                  <Button
                    onClick={handleGuardarPerfil}
                    disabled={actualizarMutation.isPending}
                  >
                    {actualizarMutation.isPending ? (
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    ) : (
                      <Save className="h-4 w-4 mr-2" />
                    )}
                    Guardar
                  </Button>
                  <Button variant="outline" onClick={() => setIsEditing(false)}>
                    Cancelar
                  </Button>
                </div>
              </>
            ) : (
              <>
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 rounded-full bg-gradient-to-br from-horizon-500 to-horizon-700 flex items-center justify-center text-white text-lg font-semibold">
                    {perfil?.nombre?.[0]?.toUpperCase() || "U"}
                  </div>
                  <div>
                    <p className="font-medium text-gray-900">
                      {perfil?.nombre_completo || perfil?.email}
                    </p>
                    <Badge className={getRolColor(perfil?.rol || "")}>
                      {perfil?.rol_display || perfil?.rol}
                    </Badge>
                  </div>
                </div>

                <div className="space-y-3 pt-4 border-t">
                  <div className="flex items-center gap-3 text-sm">
                    <Mail className="h-4 w-4 text-gray-400" />
                    <span>{perfil?.email}</span>
                  </div>

                  {perfil?.fecha_registro && (
                    <div className="flex items-center gap-3 text-sm">
                      <Calendar className="h-4 w-4 text-gray-400" />
                      <span>
                        Miembro desde{" "}
                        {new Date(perfil.fecha_registro).toLocaleDateString(
                          "es-MX"
                        )}
                      </span>
                    </div>
                  )}

                  {perfil?.ultimo_acceso && (
                    <div className="flex items-center gap-3 text-sm text-gray-500">
                      <span className="ml-7">
                        Ultimo acceso:{" "}
                        {new Date(perfil.ultimo_acceso).toLocaleString("es-MX")}
                      </span>
                    </div>
                  )}
                </div>

                <Button
                  variant="outline"
                  onClick={() => setIsEditing(true)}
                  className="w-full mt-4"
                >
                  Editar informacion
                </Button>
              </>
            )}
          </CardContent>
        </Card>

        {/* Informacion Laboral (si tiene empleado vinculado) */}
        {perfil?.empleado && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Briefcase className="h-5 w-5" />
                Informacion Laboral
              </CardTitle>
              <CardDescription>Tu perfil como empleado</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex items-center gap-3 text-sm">
                <User className="h-4 w-4 text-gray-400" />
                <span className="font-medium">
                  {perfil.empleado.nombre_completo}
                </span>
              </div>
              {perfil.empleado.puesto && (
                <div className="flex items-center gap-3 text-sm">
                  <Briefcase className="h-4 w-4 text-gray-400" />
                  <span>{perfil.empleado.puesto}</span>
                </div>
              )}
              {perfil.empleado.departamento && (
                <div className="flex items-center gap-3 text-sm text-gray-600">
                  <span className="ml-7">{perfil.empleado.departamento}</span>
                </div>
              )}
              {perfil.empleado.empresa && (
                <div className="flex items-center gap-3 text-sm">
                  <Building2 className="h-4 w-4 text-gray-400" />
                  <span>{perfil.empleado.empresa}</span>
                </div>
              )}
              {perfil.empleado.fecha_ingreso && (
                <div className="flex items-center gap-3 text-sm">
                  <Calendar className="h-4 w-4 text-gray-400" />
                  <span>
                    Ingreso:{" "}
                    {new Date(perfil.empleado.fecha_ingreso).toLocaleDateString(
                      "es-MX"
                    )}
                  </span>
                </div>
              )}
            </CardContent>
          </Card>
        )}

        {/* Empresas Asignadas (si es empleador) */}
        {perfil?.empresas && perfil.empresas.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Building2 className="h-5 w-5" />
                Empresas Asignadas
              </CardTitle>
              <CardDescription>Empresas a las que tienes acceso</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {perfil.empresas.map((empresa) => (
                  <div
                    key={empresa.id}
                    className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg"
                  >
                    <Building2 className="h-5 w-5 text-gray-400" />
                    <p className="font-medium text-gray-900">{empresa.nombre}</p>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Seguridad */}
        <Card className={perfil?.empleado || (perfil?.empresas && perfil.empresas.length > 0) ? "" : "md:col-span-2"}>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Shield className="h-5 w-5" />
              Seguridad
            </CardTitle>
            <CardDescription>Administra tu contrasena</CardDescription>
          </CardHeader>
          <CardContent>
            {showPasswordForm ? (
              <div className="space-y-4 max-w-md">
                <div>
                  <label className="text-sm font-medium text-gray-700">
                    Contrasena actual
                  </label>
                  <Input
                    type="password"
                    value={passwordActual}
                    onChange={(e) => setPasswordActual(e.target.value)}
                    className="mt-1"
                  />
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-700">
                    Nueva contrasena
                  </label>
                  <Input
                    type="password"
                    value={passwordNuevo}
                    onChange={(e) => setPasswordNuevo(e.target.value)}
                    className="mt-1"
                  />
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-700">
                    Confirmar nueva contrasena
                  </label>
                  <Input
                    type="password"
                    value={passwordConfirmacion}
                    onChange={(e) => setPasswordConfirmacion(e.target.value)}
                    className="mt-1"
                  />
                </div>
                <div className="flex gap-2">
                  <Button
                    onClick={handleCambiarPassword}
                    disabled={passwordMutation.isPending}
                  >
                    {passwordMutation.isPending ? (
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    ) : (
                      <Lock className="h-4 w-4 mr-2" />
                    )}
                    Cambiar contrasena
                  </Button>
                  <Button
                    variant="outline"
                    onClick={() => setShowPasswordForm(false)}
                  >
                    Cancelar
                  </Button>
                </div>
              </div>
            ) : (
              <Button variant="outline" onClick={() => setShowPasswordForm(true)}>
                <Lock className="h-4 w-4 mr-2" />
                Cambiar contrasena
              </Button>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
