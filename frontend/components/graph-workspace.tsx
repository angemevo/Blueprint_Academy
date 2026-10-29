"use client";

import { useQuery } from "@tanstack/react-query";
import { Suspense, lazy, useCallback, useMemo } from "react";

import { paletteTypes } from "@/lib/graph-editing";
import {
  fetchNodeCatalog,
  startGraph,
  type NormalizedGraph,
} from "@/lib/node-catalog";

/** Empreinte du graphe sans les positions : détecte un vrai changement de structure. */
function signature(g: NormalizedGraph): string {
  const nodes = g.nodes
    .map((n) => JSON.stringify([n.id, n.type, n.label ?? null, n.properties ?? null]))
    .sort();
  const edges = g.edges
    .map((e) => JSON.stringify([e.from, e.to, e.from_pin ?? null, e.to_pin ?? null]))
    .sort();
  return JSON.stringify([nodes, edges]);
}

// Chargé à la demande : le canvas n'est jamais dans le bundle initial.
const LazyEditor = lazy(() => import("@/components/blueprint-editor"));

/**
 * Espace des types de production. Produit le graphe normalisé comme soumission,
 * ou null s'il est vide (E, G) ou inchangé (F, H).
 */
export function GraphWorkspace({
  type,
  content,
  disabled,
  onChange,
}: {
  type: string;
  content: Record<string, unknown>;
  disabled: boolean;
  onChange: (submission: Record<string, unknown> | null) => void;
}) {
  const graph = useMemo(() => startGraph(type, content), [type, content]);
  const handle = useCallback(
    (g: NormalizedGraph) => {
      const empty = g.nodes.length === 0;
      const unchanged = graph.nodes.length > 0 && signature(g) === signature(graph);
      onChange(empty || unchanged ? null : { nodes: g.nodes, edges: g.edges });
    },
    [graph, onChange],
  );
  const catalog = useQuery({ queryKey: ["node-catalog"], queryFn: fetchNodeCatalog });

  return (
    <div className="space-y-3">
      <p className="text-sm text-content-secondary">
        Clic droit pour ajouter un node, tire depuis un pin pour relier, Suppr pour effacer.
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
            readOnly={disabled}
            onChange={handle}
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
