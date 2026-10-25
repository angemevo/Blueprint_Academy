import { render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import CataloguePage from "@/app/catalogue/page";
import PathDetailPage from "@/app/catalogue/[slug]/page";

vi.mock("next/link", () => ({
  default: ({ href, children }: { href: string; children: React.ReactNode }) => (
    <a href={href}>{children}</a>
  ),
}));
vi.mock("next/navigation", () => ({
  notFound: () => {
    throw new Error("NEXT_NOT_FOUND");
  },
}));

const json = (status: number, body: unknown) =>
  new Response(JSON.stringify(body), {
    status,
    headers: { "content-type": "application/json" },
  });

const path = (id: number, title: string, order = id) => ({
  id, title, slug: `p${id}`, subtitle: "", description: "", difficulty: "beginner",
  estimated_hours: 3, order,
});

afterEach(() => vi.restoreAllMocks());

describe("catalogue", () => {
  it("liste les parcours publies sans connexion", async () => {
    const fetchMock = vi.spyOn(globalThis, "fetch").mockResolvedValue(
      json(200, { results: [path(2, "Second"), path(1, "Premier")] }),
    );
    render(await CataloguePage());
    const links = screen.getAllByRole("link");
    expect(links.map((l) => l.textContent)).toEqual([
      expect.stringContaining("Premier"),
      expect.stringContaining("Second"),
    ]);
    expect(links[0]).toHaveAttribute("href", "/catalogue/p1");
    const headers = (fetchMock.mock.calls[0]?.[1]?.headers ?? {}) as Record<string, string>;
    expect(headers.Authorization).toBeUndefined();
  });

  it("gere l'etat vide", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue(json(200, { results: [] }));
    render(await CataloguePage());
    expect(screen.getByText(/Aucun parcours/)).toBeInTheDocument();
  });

  it("gere l'erreur API", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue(json(500, {}));
    render(await CataloguePage());
    expect(screen.getByRole("alert")).toBeInTheDocument();
  });
});

describe("detail d'un parcours", () => {
  const lesson = (id: number, title: string, order: number) => ({
    id, title, slug: `l${id}`, summary: "", order, estimated_minutes: 5,
  });

  it("affiche modules et lecons dans l'ordre", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue(
      json(200, {
        ...path(1, "Fondamentaux"),
        modules: [
          { id: 2, title: "Module B", slug: "b", description: "", order: 2, lessons: [] },
          {
            id: 1, title: "Module A", slug: "a", description: "", order: 1,
            lessons: [lesson(2, "Leçon 2", 2), lesson(1, "Leçon 1", 1)],
          },
        ],
      }),
    );
    render(await PathDetailPage({ params: Promise.resolve({ slug: "p1" }) }));
    const text = document.body.textContent ?? "";
    expect(text.indexOf("Module A")).toBeLessThan(text.indexOf("Module B"));
    expect(text.indexOf("Leçon 1")).toBeLessThan(text.indexOf("Leçon 2"));
  });

  it("renvoie une 404 pour un parcours inconnu", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue(json(404, {}));
    await expect(
      PathDetailPage({ params: Promise.resolve({ slug: "nope" }) }),
    ).rejects.toThrow("NEXT_NOT_FOUND");
  });
});
