"use client";

import { useEffect, type ReactNode } from "react";

import { restoreSession } from "@/lib/session";

/** Restaure la session une fois au chargement de l'application. */
export function SessionProvider({ children }: { children: ReactNode }) {
  useEffect(() => {
    void restoreSession();
  }, []);
  return <>{children}</>;
}
