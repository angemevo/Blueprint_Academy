"use client";

import "@xyflow/react/dist/style.css";

import {
  Background,
  BackgroundVariant,
  Controls,
  ReactFlow,
  applyEdgeChanges,
  applyNodeChanges,
  type Connection,
  type Edge,
  type EdgeChange,
  type Node,
  type NodeChange,
  type ReactFlowInstance,
} from "@xyflow/react";
import { useCallback, useMemo, useRef, useState } from "react";

import { buildFlow, nodeTypes } from "@/components/blueprint-canvas";
import { pinColor } from "@/lib/blueprint-style";
import {
  addLink,
  checkLink,
  compileGraph,
  filterPalette,
  normalizeGraph,
} from "@/lib/graph-editing";
import type { CatalogNode, NormalizedGraph } from "@/lib/node-catalog";

type Props = {
  graph: NormalizedGraph;
  catalog: CatalogNode[];
  /** Types autorisés par l'exercice ; null = tout le catalogue. */
  palette?: string[] | null;
  lockedNodeIds?: string[];
  onChange?: (graph: NormalizedGraph) => void;
};

/** Canvas d'édition : ajout par clic droit, liens, suppression, compilation locale. */
export default function BlueprintEditor({
  graph, catalog, palette = null, lockedNodeIds = [], onChange,
}: Props) {
  const locked = useMemo(() => new Set(lockedNodeIds), [lockedNodeIds]);
  const initial = useMemo(() => {
    const flow = buildFlow(graph, catalog);
    const nodes = flow.nodes.map((n) => ({
      ...n,
      draggable: !locked.has(n.id),
      deletable: !locked.has(n.id),
      data: { ...n.data, gtype: graph.nodes.find((g) => g.id === n.id)?.type },
    }));
    return { nodes: nodes as Node[], edges: flow.edges };
  }, [graph, catalog, locked]);

  const [nodes, setNodes] = useState<Node[]>(initial.nodes);
  const [edges, setEdges] = useState<Edge[]>(initial.edges);
  const [menu, setMenu] = useState<{ x: number; y: number; fx: number; fy: number } | null>(null);
  const [query, setQuery] = useState("");
  const [message, setMessage] = useState<string | null>(null);
  const [compiled, setCompiled] = useState<string[] | null>(null);
  const flowRef = useRef<ReactFlowInstance | null>(null);
  const counter = useRef(0);

  const toGraph = useCallback(
    (ns: Node[], es: Edge[]): NormalizedGraph =>
      normalizeGraph({
        nodes: ns.map((n) => ({
          id: n.id, type: String(n.data.gtype), position: n.position,
        })),
        edges: es.map((e) => ({
          from: e.source, to: e.target,
          from_pin: e.sourceHandle ?? undefined, to_pin: e.targetHandle ?? undefined,
        })),
      }),
    [],
  );
  const commit = (ns: Node[], es: Edge[]) => {
    setNodes(ns);
    setEdges(es);
    onChange?.(toGraph(ns, es));
  };

  const onNodesChange = (changes: NodeChange[]) => {
    // Un node verrouillé ne se supprime pas (le serveur le revérifie).
    const safe = changes.filter((c) => !(c.type === "remove" && locked.has(c.id)));
    commit(applyNodeChanges(safe, nodes), edges);
  };
  const onEdgesChange = (changes: EdgeChange[]) => commit(nodes, applyEdgeChanges(changes, edges));

  const onConnect = (c: Connection) => {
    const link = {
      from: c.source, to: c.target, from_pin: c.sourceHandle ?? "", to_pin: c.targetHandle ?? "",
    };
    const current = toGraph(nodes, edges);
    const error = checkLink(current, catalog, link);
    if (error) return setMessage(error);
    setMessage(null);
    const next = addLink(current, catalog, link);
    const color = pinColor(
      catalog.find((n) => n.id === current.nodes.find((x) => x.id === link.from)?.type)
        ?.pins.find((p) => p.name === link.from_pin)?.type ?? "",
    );
    const es: Edge[] = next.edges.map((e, i) => ({
      id: `l${i}-${e.from}-${e.to}-${e.to_pin}`,
      source: e.from, target: e.to, sourceHandle: e.from_pin, targetHandle: e.to_pin,
      style: { stroke: color, strokeWidth: 2 },
    }));
    commit(nodes, es);
  };

  const addNode = (def: CatalogNode) => {
    if (!menu) return;
    counter.current += 1;
    const node: Node = {
      id: `new_${counter.current}`,
      type: "blueprint",
      position: { x: menu.fx, y: menu.fy },
      data: { title: def.label, definition: def, gtype: def.id },
    };
    commit([...nodes, node], edges);
    setMenu(null);
    setQuery("");
  };

  const results = filterPalette(catalog, palette, query);

  return (
    <div className="space-y-2">
      <div className="flex items-center gap-3">
        <button
          type="button"
          className="rounded bg-accent px-3 py-1 text-sm font-semibold text-white"
          onClick={() => setCompiled(compileGraph(toGraph(nodes, edges), catalog))}
        >
          Compiler
        </button>
        {message && <p role="alert" className="text-sm text-red-400">{message}</p>}
      </div>
      <div
        role="region"
        aria-label="Canvas Blueprint (édition)"
        className="relative h-[28rem] w-full overflow-hidden rounded border border-border-subtle bg-surface-0"
      >
        <ReactFlow
          nodes={nodes}
          edges={edges}
          nodeTypes={nodeTypes}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          onInit={(i) => (flowRef.current = i)}
          onPaneContextMenu={(e) => {
            e.preventDefault();
            const rect = (e.currentTarget as HTMLElement).getBoundingClientRect();
            const f = flowRef.current?.screenToFlowPosition({ x: e.clientX, y: e.clientY });
            setMenu({
              x: e.clientX - rect.left, y: e.clientY - rect.top,
              fx: f?.x ?? e.clientX - rect.left, fy: f?.y ?? e.clientY - rect.top,
            });
          }}
          onPaneClick={() => setMenu(null)}
          deleteKeyCode={["Delete", "Backspace"]}
          fitView
          minZoom={0.2}
          maxZoom={2}
          colorMode="dark"
          proOptions={{ hideAttribution: true }}
        >
          <Background variant={BackgroundVariant.Lines} gap={24} color="#1b2130" />
          <Controls showInteractive={false} />
        </ReactFlow>
        {menu && (
          <div
            role="dialog"
            aria-label="Ajouter un node"
            className="absolute z-10 w-64 rounded border border-border-subtle bg-surface-1 p-2 shadow-lg"
            style={{ left: menu.x, top: menu.y }}
          >
            <input
              autoFocus
              aria-label="Rechercher un node"
              placeholder="Rechercher un node..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              className="mb-1 w-full rounded bg-surface-0 px-2 py-1 text-sm"
            />
            <ul className="max-h-48 overflow-y-auto" role="listbox">
              {results.map((def) => (
                <li key={def.id}>
                  <button
                    type="button"
                    role="option"
                    aria-selected={false}
                    className="w-full px-2 py-1 text-left text-sm hover:bg-surface-0"
                    onClick={() => addNode(def)}
                  >
                    {def.label}
                  </button>
                </li>
              ))}
              {results.length === 0 && (
                <li className="px-2 py-1 text-sm text-content-muted">Aucun node trouvé.</li>
              )}
            </ul>
          </div>
        )}
      </div>
      {compiled && (
        <ul role="status" aria-label="Résultat de la compilation" className="text-sm">
          {compiled.length === 0 ? (
            <li className="text-green-400">Compilation réussie : aucune erreur locale.</li>
          ) : (
            compiled.map((m) => <li key={m} className="text-red-400">{m}</li>)
          )}
        </ul>
      )}
    </div>
  );
}
