"use client";

import * as React from "react";
import { useEffect, useRef, useState } from "react";
import { Loader2 } from "lucide-react";
import { MessageBubble } from "./message-bubble";
import { ChatInput } from "./chat-input";
import { useChatStore } from "@/stores/chat-store";
import { cn } from "@/lib/utils";

interface ChatContainerProps {
  compact?: boolean;
  className?: string;
}

export function ChatContainer({ compact = false, className = "" }: ChatContainerProps) {
  const { messages, isLoading, sendMessage, pendingAction, confirmAction } =
    useChatStore();
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  // Scroll to bottom on new messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = async (content: string, file?: File) => {
    if (!content.trim() && !file) return;
    await sendMessage(content, file);
  };

  if (!mounted) {
    return null;
  }

  return (
    <div className={cn("flex h-full flex-col", compact && "rounded-b-lg", className)}>
      {/* Messages area */}
      <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-4">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center px-4">
            <div className="w-12 h-12 rounded-full bg-horizon-100 flex items-center justify-center mb-4">
              <span className="text-horizon-600 font-semibold text-lg">IA</span>
            </div>
            <h3 className="text-lg font-semibold text-warm-800 mb-2">
              Asistente de RRHH
            </h3>
            <p className="text-sm text-warm-500 max-w-sm">
              Puedo ayudarte con empleados, nomina, contratos, vacaciones, reportes y mas. Escribe tu consulta o arrastra un archivo.
            </p>
            <div className="mt-6 flex flex-wrap justify-center gap-2">
              {[
                "Ver empleados activos",
                "Calcular nomina",
                "Solicitudes pendientes",
                "Generar constancia",
              ].map((suggestion) => (
                <button
                  key={suggestion}
                  onClick={() => handleSend(suggestion)}
                  className="px-3 py-1.5 text-xs font-medium text-horizon-700 bg-horizon-50 hover:bg-horizon-100 rounded-full transition-colors"
                >
                  {suggestion}
                </button>
              ))}
            </div>
          </div>
        ) : (
          <>
            {messages.map((message) => (
              <MessageBubble key={message.id} message={message} />
            ))}

            {/* Loading indicator */}
            {isLoading && (
              <div className="flex items-center gap-2 text-warm-500">
                <Loader2 className="h-4 w-4 animate-spin" strokeWidth={1.5} />
                <span className="text-sm">Procesando...</span>
              </div>
            )}

            {/* Pending action confirmation */}
            {pendingAction && (
              <div className="rounded-lg border border-amber-200 bg-amber-50 p-4">
                <p className="mb-3 text-sm text-warm-700">
                  Se requiere confirmacion para ejecutar esta accion.
                </p>
                <div className="flex gap-2">
                  <button
                    onClick={() => confirmAction(true)}
                    disabled={isLoading}
                    className="rounded-md bg-sage-600 px-4 py-2 text-sm font-medium text-white hover:bg-sage-700 disabled:opacity-50"
                  >
                    Confirmar
                  </button>
                  <button
                    onClick={() => confirmAction(false)}
                    disabled={isLoading}
                    className="rounded-md border border-warm-300 bg-white px-4 py-2 text-sm font-medium text-warm-700 hover:bg-warm-50 disabled:opacity-50"
                  >
                    Cancelar
                  </button>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </>
        )}
      </div>

      {/* Input area */}
      <ChatInput
        onSend={handleSend}
        disabled={isLoading}
        placeholder={compact ? "Escribe..." : "Escribe un mensaje..."}
      />
    </div>
  );
}
