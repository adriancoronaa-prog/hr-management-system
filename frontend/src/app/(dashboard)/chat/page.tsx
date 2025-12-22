"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

export default function ChatPage() {
  const router = useRouter();

  useEffect(() => {
    // El chat ahora es el widget flotante (Copilot)
    router.replace("/");
  }, [router]);

  return null;
}
