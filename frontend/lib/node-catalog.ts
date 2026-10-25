import { apiClient } from "@/lib/api-client";

export type CatalogPin = {
  name: string;
  label: string;
  direction: "input" | "output";
  type: string;
  /** Absent du catalogue actuel : prévu pour les pins obligatoires. */
  required?: boolean;
};

export type CatalogNode = {
  id: string;
  label: string;
  category: string;
  pins: CatalogPin[];
};

export type GraphNode = {
  id: string;
  type: string;
  label?: string;
  position?: { x: number; y: number };
  properties?: Record<string, unknown>;
};

export type GraphEdge = { from: string; to: string; from_pin?: string; to_pin?: string };

export type NormalizedGraph = { nodes: GraphNode[]; edges: GraphEdge[] };

export const fetchNodeCatalog = () => apiClient.get<CatalogNode[]>("node-catalog/");

/** Clé du graphe de départ dans le contenu public, par type d'exercice de production. */
const START_GRAPH_KEY: Record<string, string> = {
  E: "initial_graph",
  G: "initial_graph",
  F: "broken_graph",
  H: "partial_graph",
};

export function isGraphExerciseType(type: string): boolean {
  return type in START_GRAPH_KEY;
}

/** Graphe de départ d'un exercice (jamais la solution), ou un graphe vide. */
export function startGraph(type: string, content: Record<string, unknown>): NormalizedGraph {
  const raw = content[START_GRAPH_KEY[type] ?? ""] as Partial<NormalizedGraph> | undefined;
  return { nodes: raw?.nodes ?? [], edges: raw?.edges ?? [] };
}
