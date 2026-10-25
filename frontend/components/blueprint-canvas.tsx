"use client";

import "@xyflow/react/dist/style.css";

import {
  Background,
  BackgroundVariant,
  Controls,
  Handle,
  Position,
  ReactFlow,
  type Edge,
  type Node,
  type NodeProps,
} from "@xyflow/react";
import { useMemo } from "react";

import {
  CATEGORY_COLORS,
  NEUTRAL_HEADER_COLOR,
  NEUTRAL_PIN_COLOR,
  pinColor,
} from "@/lib/blueprint-style";
import type { CatalogNode, CatalogPin, NormalizedGraph } from "@/lib/node-catalog";

type BlueprintNodeData = {
  title: string;
  definition: CatalogNode | null;
  [key: string]: unknown;
};

function ExecShape({ color }: { color: string }) {
  return (
    <svg width="12" height="12" viewBox="0 0 12 12" aria-hidden data-shape="exec">
      <polygon points="1,1 7,1 11,6 7,11 1,11" fill="none" stroke={color} strokeWidth="2" />
    </svg>
  );
}

function DataShape({ color }: { color: string }) {
  return (
    <span
      aria-hidden
      data-shape="data"
      className="inline-block h-2.5 w-2.5 rounded-full"
      style={{ backgroundColor: color }}
    />
  );
}

function PinRow({ pin }: { pin: CatalogPin }) {
  const color = pinColor(pin.type);
  const isInput = pin.direction === "input";
  const shape = pin.type === "exec" ? <ExecShape color={color} /> : <DataShape color={color} />;
  return (
    <div
      data-testid={`pin-${pin.direction}-${pin.name}`}
      data-pin-type={pin.type}
      className={`relative flex items-center gap-1.5 py-0.5 text-xs text-content-primary ${
        isInput ? "justify-start pl-3" : "justify-end pr-3"
      }`}
    >
      <Handle
        id={pin.name}
        type={isInput ? "target" : "source"}
        position={isInput ? Position.Left : Position.Right}
        isConnectable={false}
        style={{ background: color, border: "none", width: 8, height: 8 }}
      />
      {isInput && shape}
      {pin.label && <span>{pin.label}</span>}
      {!isInput && shape}
    </div>
  );
}

function BlueprintNode({ data }: NodeProps<Node<BlueprintNodeData>>) {
  const { title, definition } = data;
  const inputs = definition?.pins.filter((p) => p.direction === "input") ?? [];
  const outputs = definition?.pins.filter((p) => p.direction === "output") ?? [];
  const header = definition
    ? (CATEGORY_COLORS[definition.category] ?? NEUTRAL_HEADER_COLOR)
    : NEUTRAL_HEADER_COLOR;

  return (
    <div
      data-testid="bp-node"
      data-known={definition ? "true" : "false"}
      className="min-w-36 overflow-hidden rounded-md border border-border-subtle bg-surface-1 shadow-lg"
    >
      <div
        className="px-3 py-1.5 text-sm font-semibold text-white"
        style={{ backgroundColor: header }}
      >
        {title}
      </div>
      {definition ? (
        <div className="flex justify-between gap-6 py-1">
          <div>{inputs.map((p) => <PinRow key={p.name} pin={p} />)}</div>
          <div>{outputs.map((p) => <PinRow key={p.name} pin={p} />)}</div>
        </div>
      ) : (
        <>
          {/* Node inconnu : version neutre, avec des points d'accroche génériques. */}
          <Handle type="target" position={Position.Left} isConnectable={false} />
          <Handle type="source" position={Position.Right} isConnectable={false} />
          <p className="px-3 py-2 text-xs text-content-muted">Node non répertorié</p>
        </>
      )}
    </div>
  );
}

const nodeTypes = { blueprint: BlueprintNode };

const hasPin = (def: CatalogNode | null, name: string | undefined, direction: string) =>
  !!name && !!def?.pins.some((p) => p.name === name && p.direction === direction);

export function buildFlow(graph: NormalizedGraph, catalog: CatalogNode[]) {
  const byId = new Map(catalog.map((n) => [n.id, n]));
  const defs = new Map<string, CatalogNode | null>();

  const nodes: Node<BlueprintNodeData>[] = graph.nodes.map((n, i) => {
    const def = byId.get(n.type) ?? null;
    defs.set(n.id, def);
    return {
      id: n.id,
      type: "blueprint",
      position: n.position ?? { x: (i % 4) * 260, y: Math.floor(i / 4) * 180 },
      draggable: false,
      data: { title: n.label ?? def?.label ?? n.type, definition: def },
    };
  });

  const edges: Edge[] = graph.edges
    .filter((e) => defs.has(e.from) && defs.has(e.to))
    .map((e, i) => {
      const sourceDef = defs.get(e.from) ?? null;
      const targetDef = defs.get(e.to) ?? null;
      const known = hasPin(sourceDef, e.from_pin, "output");
      const type = known
        ? sourceDef?.pins.find((p) => p.name === e.from_pin && p.direction === "output")?.type
        : undefined;
      return {
        id: `e${i}-${e.from}-${e.to}`,
        source: e.from,
        target: e.to,
        sourceHandle: known ? e.from_pin : undefined,
        targetHandle: hasPin(targetDef, e.to_pin, "input") ? e.to_pin : undefined,
        type: "default",
        style: { stroke: type ? pinColor(type) : NEUTRAL_PIN_COLOR, strokeWidth: 2 },
        data: { pinType: type ?? null },
      };
    });

  return { nodes, edges };
}

/** Canvas Blueprint en lecture seule : aucune édition, vue déplaçable et zoomable. */
export default function BlueprintCanvas({
  graph,
  catalog,
}: {
  graph: NormalizedGraph;
  catalog: CatalogNode[];
}) {
  const { nodes, edges } = useMemo(() => buildFlow(graph, catalog), [graph, catalog]);
  return (
    <div
      role="region"
      aria-label="Canvas Blueprint (lecture seule)"
      className="h-[28rem] w-full overflow-hidden rounded border border-border-subtle bg-surface-0"
    >
      <ReactFlow
        nodes={nodes}
        edges={edges}
        nodeTypes={nodeTypes}
        nodesDraggable={false}
        nodesConnectable={false}
        elementsSelectable={false}
        fitView
        minZoom={0.2}
        maxZoom={2}
        colorMode="dark"
        proOptions={{ hideAttribution: true }}
      >
        <Background variant={BackgroundVariant.Lines} gap={24} color="#1b2130" />
        <Controls showInteractive={false} />
      </ReactFlow>
    </div>
  );
}
