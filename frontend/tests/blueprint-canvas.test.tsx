import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import { readFileSync } from "node:fs";
import { afterEach, beforeAll, describe, expect, it, vi } from "vitest";

import BlueprintCanvas, { buildFlow } from "@/components/blueprint-canvas";
import { ExerciseWorkspace } from "@/components/exercise-workspace";
import type { ExerciseDetail } from "@/lib/exercises";
import type { CatalogNode, NormalizedGraph } from "@/lib/node-catalog";

beforeAll(() => {
  class RO {
    observe() {}
    unobserve() {}
    disconnect() {}
  }
  vi.stubGlobal("ResizeObserver", RO);
  vi.stubGlobal(
    "DOMMatrixReadOnly",
    class {
      m22 = 1;
    },
  );
});
afterEach(() => vi.restoreAllMocks());

const catalog: CatalogNode[] = [
  {
    id: "K2Node_Event:ReceiveBeginPlay", label: "Event BeginPlay", category: "events",
    pins: [{ name: "then", label: "", direction: "output", type: "exec" }],
  },
  {
    id: "K2Node_CallFunction:PrintString", label: "Print String", category: "functions",
    pins: [
      { name: "execute", label: "", direction: "input", type: "exec" },
      { name: "InString", label: "In String", direction: "input", type: "string" },
      { name: "then", label: "", direction: "output", type: "exec" },
    ],
  },
];

const graph: NormalizedGraph = {
  nodes: [
    { id: "n1", type: "K2Node_Event:ReceiveBeginPlay", position: { x: 0, y: 0 } },
    { id: "n2", type: "K2Node_CallFunction:PrintString", position: { x: 300, y: 0 } },
    { id: "n3", type: "K2Node_Inconnu", label: "Mystère", position: { x: 600, y: 0 } },
  ],
  edges: [
    { from: "n1", to: "n2", from_pin: "then", to_pin: "execute" },
    { from: "n2", to: "n3", from_pin: "then" },
  ],
};

describe("BlueprintCanvas", () => {
  it("affiche nodes, pins exec / données et node inconnu sans planter", () => {
    render(<BlueprintCanvas graph={graph} catalog={catalog} />);
    expect(screen.getByText("Event BeginPlay")).toBeInTheDocument();
    expect(screen.getByText("Print String")).toBeInTheDocument();
    expect(screen.getByText("In String")).toBeInTheDocument();
    const exec = screen.getAllByTestId("pin-input-execute")[0];
    expect(exec?.querySelector("[data-shape='exec']")).not.toBeNull();
    const data = screen.getByTestId("pin-input-InString");
    expect(data.getAttribute("data-pin-type")).toBe("string");
    expect(data.querySelector("[data-shape='data']")).not.toBeNull();
    expect(screen.getByText("Mystère")).toBeInTheDocument();
    const unknown = screen.getAllByTestId("bp-node").find((n) => n.dataset.known === "false");
    expect(unknown).toBeDefined();
  });
});

describe("chargement à la demande", () => {
  it("le canvas n'est importé que dynamiquement", () => {
    for (const f of ["components/graph-workspace.tsx", "components/exercise-workspace.tsx"]) {
      const src = readFileSync(f, "utf8");
      expect(src).not.toMatch(/^import .*blueprint-canvas/m);
    }
    expect(readFileSync("components/graph-workspace.tsx", "utf8")).toContain(
      'import("@/components/blueprint-canvas")',
    );
  });
});

describe("buildFlow", () => {
  it("crée les liens colorés selon le type du pin source", () => {
    const { nodes, edges } = buildFlow(graph, catalog);
    expect(nodes).toHaveLength(3);
    expect(edges).toHaveLength(2);
    expect(edges[0]?.sourceHandle).toBe("then");
    expect(edges[0]?.targetHandle).toBe("execute");
    expect(edges[0]?.style?.stroke).toBe("#ffffff");
  });

  it("ignore un lien vers un node absent", () => {
    const { edges } = buildFlow({ nodes: graph.nodes, edges: [{ from: "n1", to: "zz" }] }, catalog);
    expect(edges).toHaveLength(0);
  });
});

describe("ExerciseWorkspace (production)", () => {
  it("type H : charge le canvas à la demande, lecture seule, sans solution", async () => {
    const spy = vi.spyOn(globalThis, "fetch").mockResolvedValue(
      new Response(JSON.stringify(catalog), {
        status: 200, headers: { "content-type": "application/json" },
      }),
    );
    const ex: ExerciseDetail = {
      id: 9, type: "H", title: "Compléter", difficulty: "beginner", time_limit_seconds: null,
      max_attempts: null, xp_reward: 10, hints_count: 0,
      content: { prompt: "Complète le graphe.", partial_graph: graph },
    };
    const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
    render(
      <QueryClientProvider client={client}>
        <ExerciseWorkspace exercise={ex} />
      </QueryClientProvider>,
    );
    expect(screen.getByText(/Édition bientôt disponible/)).toBeInTheDocument();
    expect(await screen.findByText("Print String")).toBeInTheDocument();
    expect(String(spy.mock.calls[0]?.[0])).toContain("node-catalog/");
    expect(screen.queryByRole("button", { name: "Valider" })).not.toBeInTheDocument();
  });
});
