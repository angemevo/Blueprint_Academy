"use client";

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useState, type ReactNode } from "react";

/**
 * Fournisseurs globaux de l'application.
 *
 * TanStack Query gere l'etat serveur. L'etat client leger passera par Zustand
 * (dossier `stores/`), sans provider a monter ici.
 */
export function AppProviders({ children }: { children: ReactNode }) {
  // Un QueryClient par montage : evite de partager le cache entre requetes SSR.
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 30_000,
            retry: 1,
            refetchOnWindowFocus: false,
          },
        },
      }),
  );

  return (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );
}
