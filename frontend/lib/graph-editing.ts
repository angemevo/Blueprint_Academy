import type { CatalogNode, CatalogPin, NormalizedGraph } from "@/lib/node-catalog";

export type Link = { from: string; to: string; from_pin: string; to_pin: string };

const findPin = (def: CatalogNode | undefined, name: string, direction: CatalogPin["direction"]) =>
  def?.pins.find((p) => p.name === name && p.direction === direction);

/** Palette de l'exercice si elle existe, sinon tout le catalogue ; filtre par texte. */
export function filterPalette(
  catalog: CatalogNode[],
  palette: string[] | null,
  query: string,
): CatalogNode[] {
  const allowed = palette && palette.length > 0 ? new Set(palette) : null;
  const q = query.trim().toLowerCase();
  return catalog.filter(
    (n) => (!allowed || allowed.has(n.id)) && (!q || n.label.toLowerCase().includes(q)),
  );
}

/** Types de nodes de la palette d'un exercice (`content.palette`), ou null. */
export function paletteTypes(content: Record<string, unknown>): string[] | null {
  const raw = content.palette;
  if (!Array.isArray(raw)) return null;
  return raw.flatMap((i) => (i && typeof i.type === "string" ? [i.type as string] : []));
}

/** Retourne un message d'erreur si le lien est incohérent, sinon null. */
export function checkLink(graph: NormalizedGraph, catalog: CatalogNode[], link: Link): string | null {
  const byId = new Map(catalog.map((n) => [n.id, n]));
  const typeOf = (id: string) => graph.nodes.find((n) => n.id === id)?.type ?? "";
  const src = findPin(byId.get(typeOf(link.from)), link.from_pin, "output");
  const dst = findPin(byId.get(typeOf(link.to)), link.to_pin, "input");
  if (link.from === link.to) return "Impossible de relier un node à lui-même.";
  if (!src || !dst) return "Relie une sortie à une entrée.";
  if ((src.type === "exec") !== (dst.type === "exec"))
    return "Impossible de relier un pin d'exécution à un pin de données.";
  if (src.type !== dst.type && src.type !== "wildcard" && dst.type !== "wildcard")
    return `Types incompatibles : ${src.type} n'est pas compatible avec ${dst.type}.`;
  const dup = graph.edges.some(
    (e) =>
      e.from === link.from && e.to === link.to && e.from_pin === link.from_pin && e.to_pin === link.to_pin,
  );
  return dup ? "Ces deux pins sont déjà reliés." : null;
}

/** Ajoute un lien ; une entrée de données n'accepte qu'un seul lien (remplacé). */
export function addLink(graph: NormalizedGraph, catalog: CatalogNode[], link: Link): NormalizedGraph {
  const dst = catalog
    .find((n) => n.id === graph.nodes.find((x) => x.id === link.to)?.type)
    ?.pins.find((p) => p.name === link.to_pin);
  const edges =
    dst && dst.type !== "exec"
      ? graph.edges.filter((e) => !(e.to === link.to && e.to_pin === link.to_pin))
      : graph.edges;
  return { ...graph, edges: [...edges, link] };
}

/** Compilation locale : messages inspirés de l'éditeur. Ne valide pas l'exercice. */
export function compileGraph(graph: NormalizedGraph, catalog: CatalogNode[]): string[] {
  const byId = new Map(catalog.map((n) => [n.id, n]));
  const messages: string[] = [];
  for (const node of graph.nodes) {
    const def = byId.get(node.type);
    const title = node.label ?? def?.label ?? node.type;
    if (!def) {
      messages.push(`Erreur : le node ${title} est inconnu.`);
      continue;
    }
    // À vérifier dans Unreal : libellé exact de l'avertissement.
    const execIn = def.pins.find((p) => p.direction === "input" && p.type === "exec");
    if (execIn && !graph.edges.some((e) => e.to === node.id && e.to_pin === execIn.name))
      messages.push(`Avertissement : ${title} ne sera jamais exécuté (aucun lien d'exécution).`);
    for (const pin of def.pins) {
      if (pin.direction !== "input" || pin.type === "exec") continue;
      if (pin.required && !graph.edges.some((e) => e.to === node.id && e.to_pin === pin.name))
        messages.push(`Erreur : le pin ${pin.label || pin.name} de ${title} n'est pas connecté.`);
    }
  }
  for (const e of graph.edges) {
    const err = checkLink({ ...graph, edges: [] }, catalog, {
      from: e.from, to: e.to, from_pin: e.from_pin ?? "", to_pin: e.to_pin ?? "",
    });
    if (err) messages.push(`Erreur : lien ${e.from} → ${e.to} invalide. ${err}`);
  }
  return messages;
}

/** Graphe normalisé prêt à être soumis : `from_pin` / `to_pin` uniquement. */
export function normalizeGraph(graph: NormalizedGraph): NormalizedGraph {
  return {
    nodes: graph.nodes.map((n) => ({
      id: n.id,
      type: n.type,
      ...(n.properties ? { properties: n.properties } : {}),
      ...(n.position ? { position: n.position } : {}),
    })),
    edges: graph.edges.map((e) => ({
      from: e.from, to: e.to, from_pin: e.from_pin, to_pin: e.to_pin,
    })),
  };
}
