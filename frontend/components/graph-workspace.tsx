"use client";

import { useQuery } from "@tanstack/react-query";
import { Suspense, lazy, useMemo } from "react";

import { paletteTypes } from "@/lib/graph-editing";
import { fetchNodeCatalog, startGraph } from "@/lib/node-catalog";

// Chargé à la demande : le canvas n'est jamais dans le bundle initial.
const LazyEditor = lazy(() => import("@/components/blueprint-editor"));

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
      <p className="text-sm text-content-secondary">
        Clic droit pour ajouter un node, tire depuis un pin pour relier, Suppr pour effacer. L&apos;envoi de ta solution sera bientôt disponible.
      </p>
      {catalog.isError ? (
        <p role="alert" className="text-content-secondary">
          Impossible de charger le canvas. Vérifie ta connexion et réessaie.
        </p>
      ) : !catalog.data ? (
        <p role="status" className="text-content-muted">Chargement...</p>
      ) : (
        <Suspense fallback={<p role="status" className="text-content-muted">Chargement...</p>}>
          <LazyEditor
            graph={graph}
            catalog={catalog.data}
            palette={paletteTypes(content)}
            lockedNodeIds={
              Array.isArray(content.locked_node_ids) ? (content.locked_node_ids as string[]) : []
            }
          />
        </Suspense>
      )}
    </div>
  );
}
