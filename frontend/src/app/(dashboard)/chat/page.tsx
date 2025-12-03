"use client";

import * as React from "react";
import { RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";
import { ChatContainer } from "@/components/chat/chat-container";
import { useChatStore } from "@/stores/chat-store";

export default function ChatPage() {
  const { clearMessages, messages } = useChatStore();

  return (
    <div className="h-[calc(100vh-4rem)] flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-warm-200 bg-white px-4 py-3 rounded-t-xl">
        <div>
          <h2 className="font-medium text-warm-900">Asistente IA</h2>
          <p className="text-sm text-warm-500">
            97 acciones disponibles
          </p>
        </div>
        {messages.length > 0 && (
          <Button variant="ghost" size="sm" onClick={clearMessages}>
            <RefreshCw className="mr-2 h-4 w-4" strokeWidth={1.5} />
            Nueva conversacion
          </Button>
        )}
      </div>

      {/* Chat */}
      <div className="flex-1 flex flex-col bg-white rounded-b-xl border border-t-0 border-warm-200 shadow-subtle overflow-hidden">
        <ChatContainer />
      </div>
    </div>
  );
}
