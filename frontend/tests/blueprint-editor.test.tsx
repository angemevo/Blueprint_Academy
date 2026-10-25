import { fireEvent, render, screen } from "@testing-library/react";
import { beforeAll, describe, expect, it, vi } from "vitest";

import { buildFlow } from "@/components/blueprint-canvas";
import BlueprintEditor from "@/components/blueprint-editor";
import { addLink, checkLink, compileGraph, filterPalette, normalizeGraph } from "@/lib/graph-editing";
import type { CatalogNode, NormalizedGraph } from "@/lib/node-catalog";

beforeAll(() => {
  vi.stubGlobal("ResizeObserver", class { observe() {} unobserve() {} disconnect() {} });
  vi.stubGlobal("DOMMatrixReadOnly", class { m22 = 1; });
});

const catalog: CatalogNode[] = [
  { id: "Begin", label: "Event BeginPlay", category: "events",
    pins: [{ name: "then", label: "", direction: "output", type: "exec" }] },
  { id: "Print", label: "Print String", category: "functions",
    pins: [
      { name: "execute", label: "", direction: "input", type: "exec" },
      { name: "InString", label: "In String", direction: "input", type: "string" },
      { name: "then", label: "", direction: "output", type: "exec" },
    ] },
  { id: "Str", label: "Make Literal String", category: "functions",
    pins: [{ name: "Value", label: "", direction: "output", type: "string" }] },
];
const graph: NormalizedGraph = {
  nodes: [{ id: "n1", type: "Begin" }, { id: "n2", type: "Print" }, { id: "n3", type: "Str" }],
  edges: [],
};
const link = (from: string, to: string, from_pin: string, to_pin: string) => ({ from, to, from_pin, to_pin });

describe("édition du graphe", () => {
  it("ajoute un node via le menu de clic droit, filtré par la palette", () => {
    const onChange = vi.fn();
    render(<BlueprintEditor graph={{ nodes: [], edges: [] }} catalog={catalog} palette={["Print"]} onChange={onChange} />);
    fireEvent.contextMenu(document.querySelector(".react-flow__pane")!);
    expect(screen.queryByText("Event BeginPlay")).toBeNull();
    fireEvent.click(screen.getByRole("option", { name: "Print String" }));
    expect(onChange).toHaveBeenLastCalledWith(
      expect.objectContaining({ nodes: [expect.objectContaining({ type: "Print" })] }),
    );
    expect(screen.getByText("Print String")).toBeInTheDocument();
  });

  it("filtre le catalogue par texte sans palette", () => {
    expect(filterPalette(catalog, null, "string").map((n) => n.id)).toEqual(["Print", "Str"]);
  });

  it("accepte un lien valide et le normalise", () => {
    const l = link("n1", "n2", "then", "execute");
    expect(checkLink(graph, catalog, l)).toBeNull();
    const next = addLink(graph, catalog, l);
    expect(normalizeGraph(next).edges).toEqual([l]);
  });

  it("refuse les liens incohérents avec un message clair", () => {
    expect(checkLink(graph, catalog, link("n2", "n1", "then", "then"))).toMatch(/sortie à une entrée/);
    expect(checkLink(graph, catalog, link("n1", "n2", "then", "InString"))).toMatch(/exécution.*données/);
    expect(checkLink(graph, catalog, link("n2", "n2", "then", "execute"))).toMatch(/lui-même/);
    const wrong: CatalogNode[] = catalog.map((n) =>
      n.id === "Str" ? { ...n, pins: [{ name: "Value", label: "", direction: "output" as const, type: "int" }] } : n);
    expect(checkLink(graph, wrong, link("n3", "n2", "Value", "InString"))).toMatch(/incompatibles/);
  });

  it("empêche la suppression d'un node verrouillé", () => {
    const flow = buildFlow(graph, catalog);
    expect(flow.nodes.length).toBe(3);
    render(<BlueprintEditor graph={graph} catalog={catalog} lockedNodeIds={["n1"]} />);
    const locked = document.querySelector('[data-id="n1"]')!;
    expect(locked.className).not.toMatch(/selectable.*draggable/);
    expect(locked.classList.contains("draggable")).toBe(false);
  });

  it("compile localement et signale les nodes jamais exécutés", () => {
    expect(compileGraph(graph, catalog).join()).toMatch(/Print String ne sera jamais exécuté/);
    render(<BlueprintEditor graph={graph} catalog={catalog} />);
    fireEvent.click(screen.getByRole("button", { name: "Compiler" }));
    expect(screen.getByRole("status")).toHaveTextContent(/jamais exécuté/);
  });
});
