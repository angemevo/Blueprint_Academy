"use client";

import { useQuery } from "@tanstack/react-query";
import { Suspense, lazy, useMemo } from "react";

import { fetchNodeCatalog, startGraph } from "@/lib/node-catalog";

// Chargé à la demande : le canvas n'est jamais dans le bundle initial.
const LazyCanvas = lazy(() => import("@/components/blueprint-canvas"));

/** Espace des types de production : graphe de départ en lecture seule. */
export function GraphWorkspace({
  type,
  content,
}: {
  type: string;
  content: Record<string, unknown>;
}) {
  const graph = useMemo(() => startGraph(type, content), [type, content]);
  const catalog = useQuery({ queryKey: ["node-catalog"], queryFn: fetchNodeCatalog });

  return (
    <div className="space-y-3">
      <p role="status" className="text-sm text-content-secondary">
        Édition bientôt disponible : pour l&apos;instant, tu peux observer le graphe de départ.
      </p>
      {catalog.isError ? (
        <p role="alert" className="text-content-secondary">
          Impossible de charger le canvas. Vérifie ta connexion et réessaie.
        </p>
      ) : !catalog.data ? (
        <p role="status" className="text-content-muted">Chargement...</p>
      ) : (
        <Suspense fallback={<p role="status" className="text-content-muted">Chargement...</p>}>
          <LazyCanvas graph={graph} catalog={catalog.data} />
        </Suspense>
      )}
    </div>
  );
}
