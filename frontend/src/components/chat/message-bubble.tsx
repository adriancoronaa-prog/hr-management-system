"use client";

import * as React from "react";
import { motion } from "framer-motion";
import { FileText, Download } from "lucide-react";
import { cn, formatRelativeTime } from "@/lib/utils";
import { Avatar } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import { useAuthStore } from "@/stores/auth-store";
import type { Message } from "@/types";

interface MessageBubbleProps {
  message: Message;
}

export function MessageBubble({ message }: MessageBubbleProps) {
  const { user } = useAuthStore();
  const isUser = message.role === "user";

  const handleDownload = () => {
    if (message.accion?.archivo) {
      const { nombre, contenido_base64, tipo } = message.accion.archivo;
      const byteCharacters = atob(contenido_base64);
      const byteNumbers = new Array(byteCharacters.length);
      for (let i = 0; i < byteCharacters.length; i++) {
        byteNumbers[i] = byteCharacters.charCodeAt(i);
      }
      const byteArray = new Uint8Array(byteNumbers);
      const blob = new Blob([byteArray], { type: tipo });

      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = nombre;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    }
  };

  // Formatear contenido con markdown basico
  const formatContent = (content: string) => {
    // Convertir **texto** a negrita
    let formatted = content.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
    // Convertir saltos de linea
    formatted = formatted.replace(/\n/g, "<br />");
    // Convertir listas con -
    formatted = formatted.replace(/^- (.+)$/gm, '<li class="ml-4">$1</li>');

    return formatted;
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.2 }}
      className={cn(
        "flex w-full",
        isUser ? "justify-end" : "justify-start"
      )}
    >
      <div className={cn("flex gap-3 max-w-[85%] sm:max-w-[75%]", isUser && "flex-row-reverse")}>
        <Avatar
          name={isUser ? user?.nombre : "IA"}
          size="sm"
          className={cn(
            "shrink-0",
            !isUser && "bg-horizon-100 text-horizon-700"
          )}
        />

        <div className="space-y-1">
          <div
            className={cn(
              "rounded-2xl px-4 py-3",
              isUser
                ? "bg-horizon-600 text-white rounded-br-md"
                : "bg-warm-100 text-warm-900 rounded-bl-md"
            )}
          >
            {/* File attachment indicator */}
            {message.archivo_nombre && (
              <div
                className={cn(
                  "mb-2 flex items-center gap-2 text-sm",
                  isUser ? "text-horizon-200" : "text-warm-500"
                )}
              >
                <FileText className="h-4 w-4" strokeWidth={1.5} />
                <span>{message.archivo_nombre}</span>
              </div>
            )}

            {/* Message content with basic markdown */}
            <div
              className={cn(
                "text-sm leading-relaxed",
                isUser ? "text-white" : "text-warm-800"
              )}
              dangerouslySetInnerHTML={{ __html: formatContent(message.content) }}
            />

            {/* Action result */}
            {message.accion?.success && message.accion.mensaje && (
              <div
                className={cn(
                  "mt-2 rounded border p-2 text-sm",
                  isUser
                    ? "border-horizon-500 bg-horizon-700"
                    : "border-sage-200 bg-sage-50 text-sage-700"
                )}
              >
                {message.accion.mensaje}
              </div>
            )}

            {/* File download button */}
            {message.accion?.archivo && (
              <Button
                variant={isUser ? "secondary" : "outline"}
                size="sm"
                className="mt-2"
                onClick={handleDownload}
              >
                <Download className="mr-2 h-4 w-4" strokeWidth={1.5} />
                Descargar {message.accion.archivo.nombre}
              </Button>
            )}
          </div>

          {/* Timestamp */}
          <p
            className={cn(
              "text-xs text-warm-400",
              isUser && "text-right"
            )}
          >
            {formatRelativeTime(message.timestamp)}
          </p>
        </div>
      </div>
    </motion.div>
  );
}
