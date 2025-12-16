import { create } from "zustand";
import { chatApi } from "@/lib/api";
import type { Message, ActionResponse } from "@/types";
import { generateId } from "@/lib/utils";

interface ChatState {
  messages: Message[];
  conversationId: string | null;
  isLoading: boolean;
  error: string | null;
  pendingAction: ActionResponse | null;
  isOpen: boolean;
  sendMessage: (content: string, file?: File) => Promise<void>;
  confirmAction: (confirm: boolean) => Promise<void>;
  clearMessages: () => void;
  setConversationId: (id: string | null) => void;
  setIsOpen: (open: boolean) => void;
  toggleOpen: () => void;
}

export const useChatStore = create<ChatState>((set, get) => ({
  messages: [],
  conversationId: null,
  isLoading: false,
  error: null,
  pendingAction: null,
  isOpen: false,

  setIsOpen: (open: boolean) => set({ isOpen: open }),

  toggleOpen: () => set((state) => ({ isOpen: !state.isOpen })),

  sendMessage: async (content: string, file?: File) => {
    const { conversationId } = get();

    // Add user message immediately
    const userMessage: Message = {
      id: generateId(),
      role: "user",
      content,
      timestamp: new Date().toISOString(),
      archivo_nombre: file?.name,
      tipo_archivo: file?.type,
    };

    set((state) => ({
      messages: [...state.messages, userMessage],
      isLoading: true,
      error: null,
    }));

    try {
      const response = await chatApi.sendMessage(
        content,
        conversationId || undefined,
        file
      );

      // Create assistant message
      const assistantMessage: Message = {
        id: response.mensaje_id || generateId(),
        role: "assistant",
        content: response.respuesta,
        timestamp: new Date().toISOString(),
        accion: response.accion_ejecutada,
      };

      set((state) => ({
        messages: [...state.messages, assistantMessage],
        conversationId: response.conversacion_id,
        isLoading: false,
        pendingAction: response.requiere_confirmacion
          ? response.accion_pendiente
          : null,
      }));

      // Handle file download if present
      if (response.accion_ejecutada?.archivo) {
        const { nombre, contenido_base64, tipo } =
          response.accion_ejecutada.archivo;
        const blob = base64ToBlob(contenido_base64, tipo);
        downloadBlob(blob, nombre);
      }
    } catch (error) {
      set({
        isLoading: false,
        error: "Error al enviar mensaje. Intenta de nuevo.",
      });
    }
  },

  confirmAction: async (confirm: boolean) => {
    const { conversationId } = get();
    if (!conversationId) return;

    set({ isLoading: true });

    try {
      const response = await chatApi.confirmAction(conversationId, confirm);

      if (response.respuesta) {
        const message: Message = {
          id: generateId(),
          role: "assistant",
          content: response.respuesta,
          timestamp: new Date().toISOString(),
          accion: response.resultado,
        };

        set((state) => ({
          messages: [...state.messages, message],
          isLoading: false,
          pendingAction: null,
        }));

        // Handle file download if present
        if (response.resultado?.archivo) {
          const { nombre, contenido_base64, tipo } = response.resultado.archivo;
          const blob = base64ToBlob(contenido_base64, tipo);
          downloadBlob(blob, nombre);
        }
      } else {
        set({ isLoading: false, pendingAction: null });
      }
    } catch {
      set({
        isLoading: false,
        error: "Error al confirmar accion",
      });
    }
  },

  clearMessages: () => {
    set({
      messages: [],
      conversationId: null,
      error: null,
      pendingAction: null,
    });
  },

  setConversationId: (id: string | null) => {
    set({ conversationId: id });
  },
}));

// Helper functions
function base64ToBlob(base64: string, mimeType: string): Blob {
  const byteCharacters = atob(base64);
  const byteNumbers = new Array(byteCharacters.length);
  for (let i = 0; i < byteCharacters.length; i++) {
    byteNumbers[i] = byteCharacters.charCodeAt(i);
  }
  const byteArray = new Uint8Array(byteNumbers);
  return new Blob([byteArray], { type: mimeType });
}

function downloadBlob(blob: Blob, filename: string): void {
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  window.URL.revokeObjectURL(url);
  document.body.removeChild(a);
}
