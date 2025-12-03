"use client";

import * as React from "react";
import { useRef, useState, useCallback } from "react";
import { Paperclip, ArrowUp, X, FileText, Image } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

interface ChatInputProps {
  onSend: (message: string, file?: File) => void;
  disabled?: boolean;
  placeholder?: string;
}

export function ChatInput({
  onSend,
  disabled = false,
  placeholder = "Escribe un mensaje...",
}: ChatInputProps) {
  const [message, setMessage] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const adjustTextareaHeight = useCallback(() => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = "auto";
      const maxHeight = 120; // ~4 lines
      textarea.style.height = `${Math.min(textarea.scrollHeight, maxHeight)}px`;
    }
  }, []);

  const handleSubmit = () => {
    const trimmedMessage = message.trim();
    if (!trimmedMessage && !file) return;

    onSend(trimmedMessage, file || undefined);
    setMessage("");
    setFile(null);

    // Reset textarea height
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleFileSelect = (selectedFile: File) => {
    const allowedTypes = [
      "application/pdf",
      "image/jpeg",
      "image/png",
      "image/gif",
      "image/webp",
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
      "application/msword",
      "text/plain",
      "text/csv",
    ];

    if (allowedTypes.includes(selectedFile.type) || selectedFile.type.startsWith("image/")) {
      setFile(selectedFile);
    } else {
      alert("Tipo de archivo no soportado. Usa PDF, imagenes o documentos Word.");
    }
  };

  const handleInputFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      handleFileSelect(selectedFile);
    }
    // Reset input
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);

    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile) {
      handleFileSelect(droppedFile);
    }
  }, []);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const removeFile = () => {
    setFile(null);
  };

  const getFileIcon = () => {
    if (!file) return Paperclip;
    if (file.type.startsWith("image/")) return Image;
    return FileText;
  };

  const FileIcon = getFileIcon();

  return (
    <div
      className={cn(
        "relative border-t border-warm-200 bg-white p-3 sm:p-4 transition-colors",
        isDragging && "bg-horizon-50 border-horizon-300"
      )}
      onDrop={handleDrop}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
    >
      {/* File preview */}
      {file && (
        <div className="mb-2 flex items-center gap-2 rounded-lg bg-warm-50 px-3 py-2">
          <FileIcon className="h-4 w-4 text-warm-500" strokeWidth={1.5} />
          <span className="flex-1 truncate text-sm text-warm-700">
            {file.name}
          </span>
          <button
            onClick={removeFile}
            className="rounded p-1 text-warm-400 hover:bg-warm-200 hover:text-warm-600 transition-colors"
          >
            <X className="h-4 w-4" strokeWidth={1.5} />
          </button>
        </div>
      )}

      {/* Input area */}
      <div className="flex items-end gap-2">
        {/* Hidden file input */}
        <input
          ref={fileInputRef}
          type="file"
          className="hidden"
          onChange={handleInputFileSelect}
          accept=".pdf,.doc,.docx,.txt,.csv,.jpg,.jpeg,.png,.gif,.webp"
        />

        {/* Attach button */}
        <Button
          variant="ghost"
          size="icon"
          className="shrink-0"
          onClick={() => fileInputRef.current?.click()}
          disabled={disabled}
          title="Adjuntar archivo"
        >
          <Paperclip className="h-5 w-5" strokeWidth={1.5} />
        </Button>

        {/* Textarea */}
        <div className="relative flex-1">
          <textarea
            ref={textareaRef}
            value={message}
            onChange={(e) => {
              setMessage(e.target.value);
              adjustTextareaHeight();
            }}
            onKeyDown={handleKeyDown}
            placeholder={isDragging ? "Suelta el archivo aqui..." : placeholder}
            disabled={disabled}
            rows={1}
            className={cn(
              "w-full resize-none rounded-xl bg-warm-50 px-4 py-2.5 text-sm text-warm-900 placeholder:text-warm-400 focus:outline-none focus:ring-2 focus:ring-horizon-500 disabled:cursor-not-allowed disabled:opacity-50",
              "max-h-[120px] overflow-y-auto"
            )}
            style={{ minHeight: "42px" }}
          />
        </div>

        {/* Send button */}
        <Button
          size="icon"
          className="shrink-0"
          onClick={handleSubmit}
          disabled={disabled || (!message.trim() && !file)}
        >
          <ArrowUp className="h-5 w-5" strokeWidth={1.5} />
        </Button>
      </div>

      {/* Drag overlay */}
      {isDragging && (
        <div className="absolute inset-0 flex items-center justify-center bg-horizon-50/90 border-2 border-dashed border-horizon-400 rounded-lg pointer-events-none m-2">
          <p className="text-horizon-600 font-medium">Suelta el archivo aqui</p>
        </div>
      )}
    </div>
  );
}
